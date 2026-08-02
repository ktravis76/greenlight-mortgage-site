/**
 * submit-lead — the single write path for every form on greenlightmortgage.com.
 *
 * Handles two shapes:
 *   form: "application"  -> public.applications  (the /apply intake + pipeline)
 *   anything else        -> public.leads         (contact, estimate, home-value…)
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
 * As of the 2026-08-01 hardening migration this is not merely the preferred
 * path: INSERT on the four consent columns is revoked from anon and
 * authenticated, and public.applications takes no public insert at all.
 *
 * DEPLOY
 *   supabase functions deploy submit-lead --no-verify-jwt
 *   supabase secrets set GHL_WEBHOOK_URL=... RESEND_API_KEY=... NOTIFY_EMAIL=...
 */

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

// GoHighLevel / Konnectd, location LRAzmr7bQKMMlXiYfvi6. Leads go here rather than
// to an individual's inbox — reconciling inboxes by hand is the problem this fixes.
const GHL_WEBHOOK_URL = Deno.env.get("GHL_WEBHOOK_URL") ?? "";
const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY") ?? "";
const FROM_EMAIL = Deno.env.get("FROM_EMAIL")
  ?? "Greenlight Mortgage <noreply@greenlightmortgage.com>";
const NOTIFY_EMAIL = Deno.env.get("NOTIFY_EMAIL") ?? "kenneth@glmtg.com";

const ALLOWED_ORIGINS = [
  "https://greenlightmortgage.com",
  "https://www.greenlightmortgage.com",
  "https://greenlight-mortgage-site.vercel.app",
  "http://127.0.0.1:8787",
  "http://localhost:8787",
];

const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

// Kept in step with sitegen.LICENSES. Five states — Florida and South Carolina
// are NOT among them, whatever the old site's footer said.
const LICENSE_LINE =
  "Licensed in Texas, Louisiana, Michigan, North Dakota and Alabama.";

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

const PURPOSE = new Set(["purchase", "refinance", "cash_out", "not_sure"]);
const CONTACT = new Set(["phone", "text", "email"]);

const DISCLOSURE = `
<p style="font-size:13px;color:#555;line-height:1.6">
  <strong>This is an estimate, not a quote, an offer of credit, or an approval, and it is not
  a commitment to lend.</strong> It was produced from figures you entered, compared against
  illustrative rate reductions — not rates Greenlight is offering you. All loans are subject
  to credit approval and underwriting. Rate quotes and eligibility decisions are made only by
  a licensed loan officer following a complete application.
</p>`;

const SIGNOFF = `
<p style="font-size:12px;color:#777;line-height:1.6;border-top:1px solid #ddd;padding-top:12px">
  Greenlight Mortgage, LLC &middot; Powered by Co/LAB Lending &middot; Company NMLS #2426021
  &middot; Kenneth Travis, loan originator, NMLS #233918<br>
  4523 Judson Rd, Longview, TX 75605 &middot; 903-331-0892<br>
  ${LICENSE_LINE} Equal Housing Opportunity.
</p>`;

async function sendEmail(to: string, subject: string, html: string): Promise<boolean> {
  if (!RESEND_API_KEY) return false;
  try {
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${RESEND_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ from: FROM_EMAIL, to, subject, html }),
    });
    if (!res.ok) {
      console.error("resend failed", res.status, await res.text());
      return false;
    }
    return true;
  } catch (err) {
    console.error("resend threw", err);
    return false;
  }
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

  const email = clean(f.email, 254);
  const phone = clean(f.phone, 32);
  if (!email || !EMAIL_RE.test(email)) {
    return new Response(JSON.stringify({ error: "a valid email is required" }),
      { status: 400, headers });
  }

  // ---- consent: client supplies the decision and the wording it showed; the
  // server supplies everything that proves it. --------------------------------
  const consented = body.tcpa_consent === true && !!phone;
  const consentText = clean(body.tcpa_consent_text, 2000);
  const now = new Date().toISOString();
  const consent = {
    tcpa_consent: consented,
    consent_at: consented ? now : null,
    consent_ip: consented ? clientIp(req) : null,
    consent_ua: consented ? req.headers.get("user-agent")?.slice(0, 500) ?? null : null,
  };

  const supabase = createClient(SUPABASE_URL, SERVICE_KEY, {
    auth: { persistSession: false },
  });

  // ======================================================== APPLICATION intake
  if (kind === "application") {
    const first = clean(f.first_name, 80);
    const last = clean(f.last_name, 80);
    const purposeRaw = clean(f.purpose, 20) ?? "not_sure";
    if (!first || !last || !phone) {
      return new Response(JSON.stringify({ error: "name and phone are required" }),
        { status: 400, headers });
    }

    const pc = (clean(f.preferred_contact, 20) ?? "").toLowerCase();
    const row = {
      first_name: first,
      last_name: last,
      email,
      phone,
      preferred_contact: CONTACT.has(pc.replace(/\s.*$/, "")) ? pc.replace(/\s.*$/, "")
        : pc.startsWith("phone") ? "phone" : pc.startsWith("text") ? "text"
        : pc.startsWith("email") ? "email" : null,
      best_time: clean(f.best_time, 60),
      purpose: PURPOSE.has(purposeRaw) ? purposeRaw : "not_sure",
      property_city: clean(f.property_city, 80),
      property_state: clean(f.property_state, 2),
      price_band: clean(f.price_band, 40),
      timeline: clean(f.timeline, 40),
      employment: clean(f.employment, 40),
      credit_band: clean(f.credit_band, 40),
      veteran: f.veteran === true || f.veteran === "yes",
      first_time_buyer: f.first_time_buyer === true || f.first_time_buyer === "yes",
      working_with_agent: f.working_with_agent === true || f.working_with_agent === "yes",
      notes: clean(f.notes, 4000),
      consent_text: consented ? consentText : null,
      source: "web:apply",
      ...consent,
    };

    const { data, error } = await supabase
      .from("applications").insert(row).select("id, reference").single();

    if (error) {
      console.error("application insert failed", error);
      return new Response(JSON.stringify({ error: "could not save" }), { status: 500, headers });
    }

    await supabase.from("application_events").insert({
      application_id: data.id, kind: "created",
      body: `Submitted from the website. Consent to call/text: ${consented ? "yes" : "no"}.`,
    });

    // Heads-up only. Deliberately NOT the applicant's answers — email forwards,
    // syncs to phones, and cannot be recalled. The record lives in the pipeline.
    await sendEmail(NOTIFY_EMAIL,
      `New application ${data.reference} — ${first} ${last[0]}.`,
      `<p>A new application came in through the website.</p>
       <p><strong>Reference:</strong> ${data.reference}<br>
          <strong>Name:</strong> ${first} ${last[0]}.<br>
          <strong>Purpose:</strong> ${row.purpose}<br>
          <strong>Consent to call/text:</strong> ${consented ? "yes" : "no — email only"}</p>
       <p>Open the pipeline to see the full intake and pick it up. Contact details and
          answers are deliberately not included in this email.</p>${SIGNOFF}`);

    if (GHL_WEBHOOK_URL) {
      try {
        await fetch(GHL_WEBHOOK_URL, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ...row, application_id: data.id, reference: data.reference }),
        });
      } catch (err) {
        console.error("GHL forward failed — application is saved, CRM is behind", err);
      }
    }

    const emailed = await sendEmail(email,
      "We have your application — Greenlight Mortgage",
      `<p>Hi ${first},</p>
       <p>Thanks — we have your application. Your reference is
          <strong>${data.reference}</strong>.</p>
       <p>A licensed loan officer will be in touch within one business day. Once, not six
          times in an hour.</p>
       <p style="font-size:13px;color:#555">Submitting this form is not an application for
          credit and is <strong>not a commitment to lend</strong>. Any loan is subject to
          credit approval and underwriting.</p>${SIGNOFF}`);

    return new Response(JSON.stringify({ ok: true, reference: data.reference, emailed }),
      { status: 200, headers });
  }

  // ================================================================ LEAD forms
  const name = clean(f.name, 120);
  if (!name) {
    return new Response(JSON.stringify({ error: "name is required" }), { status: 400, headers });
  }

  const row: Record<string, unknown> = {
    name, email, phone,
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
    ...consent,
    notes: [
      clean(f.message, 4000),
      clean(f.address, 200) ? `Address: ${clean(f.address, 200)}` : null,
      consented && consentText ? `TCPA consent text shown: "${consentText}"` : null,
    ].filter(Boolean).join("\n\n") || null,
  };

  const { data, error } = await supabase.from("leads").insert(row).select("id").single();

  if (error) {
    console.error("lead insert failed", error);
    return new Response(JSON.stringify({ error: "could not save" }), { status: 500, headers });
  }

  if (GHL_WEBHOOK_URL) {
    try {
      await fetch(GHL_WEBHOOK_URL, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...row, lead_id: data.id, submitted_at: now }),
      });
    } catch (err) {
      console.error("GHL forward failed — lead is saved, CRM is behind", err);
    }
  }

  // `emailed` is returned honestly. The estimator only tells the visitor a copy
  // is on its way if this actually came back true.
  let emailed = false;
  if (kind === "estimate") {
    const s = row.estimated_monthly_savings;
    emailed = await sendEmail(email, "Your Estimated Savings from Greenlight Mortgage",
      `<p>Hi ${name},</p>
       <p>Here is the estimate you just ran on our website.</p>
       <p style="font-size:28px;font-weight:700;color:#0f7a4d;margin:18px 0">
         Up to ${s ? "$" + Math.round(Number(s)).toLocaleString("en-US") : "—"} a month
       </p>${DISCLOSURE}
       <p>A licensed loan officer will follow up within one business day.</p>${SIGNOFF}`);
  }

  return new Response(JSON.stringify({ ok: true, id: data.id, emailed }),
    { status: 200, headers });
});
