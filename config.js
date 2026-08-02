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

  // ⚠️ NOT YET DEPLOYED. Until the Edge Function is live, forms fail closed:
  // the visitor is shown the office phone number instead of a false success
  // message. Never pretend a submission worked.
  LEAD_ENDPOINT_LIVE: false,

  PHONE: '903-331-0892',
};
