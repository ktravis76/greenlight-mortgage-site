/* Runtime configuration for the Greenlight Mortgage site.
   Loaded before forms.js on any page that submits something.

   The publishable key below is designed to be public — it identifies the project
   and nothing else. What actually protects the data is row-level security on the
   Supabase side, which is why db/RLS-AUDIT.md is a launch blocker rather than a
   nice-to-have: two aggregate views over soft_quotes are readable by anyone
   holding this key until db/2026-08-01-rls-hardening.sql is applied.

   No secret belongs in this file. The service-role key lives only in the Edge
   Function environment. */
window.GLM = {
  SUPABASE_URL: 'https://athovwknbwbbqworsbrm.supabase.co',
  SUPABASE_KEY: 'sb_publishable_2ajY5o6EJyVEiNpWD_HL0Q_3HLzxmXr',

  // Every lead goes through this function rather than straight to PostgREST.
  // It stamps consent IP, user agent and timestamp from the request — values a
  // browser cannot be trusted to report about itself — and forwards to
  // GoHighLevel/Konnectd. See supabase/functions/submit-lead/.
  LEAD_ENDPOINT: 'https://athovwknbwbbqworsbrm.functions.supabase.co/submit-lead',

  // GoHighLevel / Konnectd location. Used server-side; here for reference only.
  GHL_LOCATION: 'LRAzmr7bQKMMlXiYfvi6',

  // Deployed and tested 2026-08-01 — leads and applications both land, with
  // consent stamped server-side from the real request IP.
  //
  // Email delivery is a separate switch: the function returns `emailed`, and it
  // is false until RESEND_API_KEY is set on the function. The estimator reads
  // that flag and only claims a copy was sent when one actually was.
  LEAD_ENDPOINT_LIVE: true,

  PHONE: '903-331-0892',
};
