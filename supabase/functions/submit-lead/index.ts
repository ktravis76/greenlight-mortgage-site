/**
 * submit-lead — the single write path for every form on greenlightmortgage.com.
 *
 * WHY THIS EXISTS RATHER THAN POSTING STRAIGHT TO POSTGREST
 *
 * TCPA express written consent is only worth having if you can later prove who
 * agreed to what, and when. Three of the four things that prove it — the IP
 * address, the user agent, and the timestamp — cannot be trusted from a browser.
 * A browser does not reliably know its own IP, and anything it does send can be
 * edited by whoever is sending it. So the client sends the checkbox state and the
 * exact sentence it displayed; this function stamps the rest from the real
 * request, using the service-role key, and writes the row.
 *
 * The companion migration (db/2026-08-01-rls-hardening.sql) revokes INSERT on the
 * four consent columns from anon and authenticated, so this is not merely the
 * preferred path — once applied it is the only one.
 *
 * DEPLOY
 *   supabase functions deploy submit-lead --no-verify-jwt
 *   supabase secrets set GHL_WEBHOOK_URL=... RESEND_API_KEY=...
 * Then flip LEAD_ENDPOINT_LIVE to true in config.js. Until that flip the site
 * tells visitors the form is not connected rather than faking a success message.
 */

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

// GoHighLevel / Konnectd, location LRAzmr7bQKMMlXiYfvi6. Leads go here rather than
// to an individual's inbox — reconciling inboxes by hand is the problem this fixes.
const GHL_WEBHOOK_URL = Deno.env.get("GHL_WEBHOOK_URL") ?? "";
const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY") ?? "";
const FROM_EMAIL = Deno.env.get("FROM_EMAIL") ?? "Greenlight Mortgage <noreply@greenlightmortgage.com>";

const ALLOWED_ORIGINS = [
  "https://greenlightmortgage.com",
  "https://www.greenlightmortgage.com",
  "https://greenlight-mortgage-site.vercel.app",
  "http://127.0.0.1:8787",
  "http://localhost:8787",
];

const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

function cors(origin: string | null) {
  const allow = origin && ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Headers": "content-type, apikey, authorization",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Vary": "Origin",
  };
}

/** First hop in X-Forwarded-For is the client; the rest are proxies. */
function clientIp(req: Request): string | null {
  const xff = req.headers.get("x-forwarded-for");
  if (xff) return xff.split(",")[0].trim().slice(0, 64);
  return req.headers.get("cf-connecting-ip")?.slice(0, 64) ?? null;
}

function clean(v: unknown, max: number): string | null {
  if (typeof v !== "string") return null;
  const s = v.trim();
  return s ? s.slice(0, max) : null;
}

function money(v: unknown): number | null {
  const n = typeof v === "number" ? v : parseFloat(String(v ?? "").replace(/[^0-9.\-]/g, ""));
  return Number.isFinite(n) ? n : null;
}

Deno.serve(async (req) => {
  const headers = { ...cors(req.headers.get("origin")), "Content-Type": "application/json" };

  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers });
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "method not allowed" }), { status: 405, headers });
  }

  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return new Response(JSON.stringify({ error: "invalid json" }), { status: 400, headers });
  }

  const kind = clean(body.form, 40) ?? "unknown";
  const f = (body.fields ?? {}) as Record<string, unknown>;

  const name = clean(f.name, 120);
  const email = clean(f.email, 254);
  const phone = clean(f.phone, 32);

  if (!name || !email || !EMAIL_RE.test(email)) {
    return new Response(JSON.stringify({ error: "name and a valid email are required" }),
      { status: 400, headers });
  }

  // ---- consent: client supplies the decision and the wording it showed; the
  // server supplies everything that proves it. --------------------------------
  const consented = body.tcpa_consent === true && !!phone;
  const consentText = clean(body.tcpa_consent_text, 2000);
  const now = new Date().toISOString();

  const row: Record<string, unknown> = {
    name,
    email,
    phone,
    state: clean(f.state, 64),
    source: `web:${kind}`,
    ref_code: clean(f.ref_code, 64),
    goal: clean(f.goal, 120),
    loan_type: clean(f.loan_type, 64),
    veteran: f.veteran === "yes" || f.veteran === "spouse" || f.veteran === true,
    current_rate: money(f.current_rate),
    current_payment: money(f.current_payment),
    mortgage_balance: money(f.mortgage_balance),
    estimated_home_value: money(f.estimated_home_value),
    estimated_monthly_savings: money(f.estimated_monthly_savings),
    status: "New",

    // Server-stamped. Never read from the request body.
    tcpa_consent: consented,
    consent_at: consented ? now : null,
    consent_ip: consented ? clientIp(req) : null,
    consent_ua: consented ? req.headers.get("user-agent")?.slice(0, 500) ?? null : null,

    // The verbatim sentence the person agreed to, kept with the record so we are
    // never reconstructing months-old wording from memory.
    notes: [
      clean(f.message, 4000),
      clean(f.address, 200) ? `Address: ${clean(f.address, 200)}` : null,
      consented && consentText ? `TCPA consent text shown: "${consentText}"` : null,
    ].filter(Boolean).join("\n\n") || null,
  };

  const supabase = createClient(SUPABASE_URL, SERVICE_KEY, {
    auth: { persistSession: false },
  });

  const { data, error } = await supabase.from("leads").insert(row).select("id").single();

  if (error) {
    console.error("lead insert failed", error);
    return new Response(JSON.stringify({ error: "could not save" }), { status: 500, headers });
  }

  // ---- forward to the CRM. A failure here must not lose the lead: the row is
  // already committed, so we log and still report success to the visitor. ------
  if (GHL_WEBHOOK_URL) {
    try {
      await fetch(GHL_WEBHOOK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...row, lead_id: data.id, submitted_at: now }),
      });
    } catch (err) {
      console.error("GHL forward failed — lead is saved, CRM is behind", err);
    }
  }

  // ---- email the estimate back to them. Promised on screen, so it has to happen.
  if (RESEND_API_KEY && kind === "estimate") {
    const savings = row.estimated_monthly_savings;
    try {
      await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${RESEND_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from: FROM_EMAIL,
          to: email,
          subject: "Your Estimated Savings from Greenlight Mortgage",
          html: `
<p>Hi ${name},</p>
<p>Here is the estimate you just ran on our website.</p>
<p style="font-size:28px;font-weight:700;color:#0f7a4d;margin:18px 0">
  Up to ${savings ? "$" + Math.round(Number(savings)).toLocaleString("en-US") : "—"} a month
</p>
<p style="font-size:13px;color:#555;line-height:1.6">
  <strong>This is an estimate, not a quote, an offer of credit, or an approval, and it is not
  a commitment to lend.</strong> It was produced from figures you entered, compared against
  illustrative rate reductions — not rates Greenlight is offering you. All loans are subject
  to credit approval and underwriting. Rate quotes and eligibility decisions are made only by
  a licensed loan officer following a complete application.
</p>
<p>A licensed loan officer will follow up within one business day.</p>
<p style="font-size:12px;color:#777;line-height:1.6;border-top:1px solid #ddd;padding-top:12px">
  Greenlight Mortgage, LLC &middot; Powered by Co/LAB Lending &middot; Company NMLS #2426021
  &middot; Kenneth Travis NMLS #233918<br>
  4523 Judson Rd, Longview, TX 75605 &middot; 903-331-0892<br>
  Licensed in Texas, Alabama, Florida, Louisiana, North Dakota and South Carolina.
  Equal Housing Opportunity.
</p>`,
        }),
      });
    } catch (err) {
      console.error("estimate email failed", err);
    }
  }

  return new Response(JSON.stringify({ ok: true, id: data.id }), { status: 200, headers });
});
