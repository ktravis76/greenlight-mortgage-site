-- ============================================================================
-- RLS hardening — Supabase athovwknbwbbqworsbrm (Greenlight Mortgage)
-- Written 2026-08-01. See RLS-AUDIT.md for the reasoning behind each section.
--
-- NOT YET APPLIED. Sections 1, 4 and 5 are safe to run as-is. Sections 2 and 3
-- change surfaces the live internal VA screener writes to — run those, then
-- record one quote end-to-end through tools/va-refi-screener.html before
-- pointing any consumer traffic at /tools/estimate.
--
-- Every table is at zero rows as of the audit, so none of this is a data
-- migration. It is all policy and grants.
-- ============================================================================

begin;

-- ----------------------------------------------------------------------------
-- 1. soft_quotes aggregate views: stop serving them to the internet.   [HIGH]
--
-- Both were SECURITY DEFINER, which ignores RLS on soft_quotes underneath, and
-- both granted SELECT to anon. Anyone with the publishable key — which ships in
-- the page source of the public site — could read daily lead volume, the
-- strong/thin verdict split, average quoted rate, and total balance screened.
--
-- security_invoker = true makes the views respect the caller's RLS, so the
-- existing staff-only posture on soft_quotes applies to them too.
-- ----------------------------------------------------------------------------

alter view public.soft_quotes_daily     set (security_invoker = true);
alter view public.soft_quotes_by_source set (security_invoker = true);

revoke all on public.soft_quotes_daily     from anon, authenticated;
revoke all on public.soft_quotes_by_source from anon, authenticated;

-- Staff read these through the dashboard; the RLS on soft_quotes still decides
-- whether any rows come back.
grant select on public.soft_quotes_daily     to authenticated;
grant select on public.soft_quotes_by_source to authenticated;

-- soft_quotes itself has no SELECT policy at all, so it is currently write-only
-- to everyone but service_role. Give staff a way to read their own pipeline.
drop policy if exists soft_quotes_select_staff on public.soft_quotes;
create policy soft_quotes_select_staff on public.soft_quotes
  for select to authenticated
  using (private.is_staff());

grant select on public.soft_quotes to authenticated;


-- ----------------------------------------------------------------------------
-- 2. leads: validate the insert, and take consent out of the client's hands.
--                                                                      [HIGH]
--
-- Was: WITH CHECK (true) — any anonymous caller could write any value to any
-- column, unbounded, including the four TCPA consent columns. A consent record
-- the public can forge is not evidence of consent, and the planned 50,000-lead
-- SMS campaign is what turns that from untidy into expensive.
--
-- Two halves. The CHECK below bounds what a browser may write. The column-level
-- revoke below it means a browser may not write the consent columns AT ALL —
-- those are stamped server-side by the submit-lead Edge Function, which sees
-- the real request IP and user agent. A client cannot know its own IP and can
-- lie about all four fields, so the browser is simply not a valid source for
-- them.
-- ----------------------------------------------------------------------------

drop policy if exists funnel_anon_insert_leads on public.leads;

create policy leads_public_insert on public.leads
  for insert to anon, authenticated
  with check (
        length(btrim(name))  between 1 and 120
    and length(email)        <= 254
    and email ~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$'
    and (phone is null or length(phone) between 7 and 32)
    and (state is null or length(state) <= 64)
    and (source is null or length(source) <= 120)
    and (ref_code is null or length(ref_code) <= 64)
    and (goal is null or length(goal) <= 120)
    and (loan_type is null or length(loan_type) <= 64)
    and (notes is null or length(notes) <= 4000)
    -- Money and rate fields: sane ranges, so a bad actor cannot poison the
    -- pipeline reporting with absurd values.
    and (current_rate is null or current_rate between 0 and 30)
    and (current_payment is null or current_payment between 0 and 1000000)
    and (mortgage_balance is null or mortgage_balance between 0 and 100000000)
    and (estimated_home_value is null or estimated_home_value between 0 and 100000000)
    and (total_debt is null or total_debt between 0 and 100000000)
    and (estimated_monthly_savings is null
         or estimated_monthly_savings between -1000000 and 1000000)
    -- Workflow columns belong to staff, not to whoever filled in the form.
    and status = 'New'
    and coalesce(priority, false) = false
  );

-- Columns a browser may set. Everything omitted here — tcpa_consent,
-- consent_at, consent_ip, consent_ua, created_at, updated_at — is refused at
-- the privilege layer before RLS is even consulted.
revoke insert on public.leads from anon, authenticated;

grant insert (
  name, email, phone, state, source, ref_code, goal, loan_type, veteran,
  current_rate, current_payment, mortgage_balance, estimated_home_value,
  total_debt, estimated_monthly_savings, statement_uploaded, notes
) on public.leads to anon, authenticated;

comment on column public.leads.consent_ip is
  'Stamped server-side by the submit-lead Edge Function from the request IP. '
  'Never accept this from a client — a browser cannot know its own IP and can lie. '
  'INSERT on this column is deliberately not granted to anon/authenticated.';


-- ----------------------------------------------------------------------------
-- 3. soft_quotes: let signed-in staff write, not just anonymous visitors.
--                                                                 [FUNCTIONAL]
--
-- The old policy listed role {anon} only, while INSERT was granted to both anon
-- and authenticated. A loan officer signed into the dashboard becomes
-- `authenticated`, stops matching the policy, and their screener insert is
-- refused. Zero rows is why nobody has hit it yet.
-- ----------------------------------------------------------------------------

drop policy if exists "anon can insert quotes" on public.soft_quotes;

create policy soft_quotes_public_insert on public.soft_quotes
  for insert to anon, authenticated
  with check (true);   -- intentionally open: the screener posts a wide, evolving
                       -- 41-column payload and is an internal tool. Revisit if
                       -- it is ever exposed to consumers directly.


-- ----------------------------------------------------------------------------
-- 4. mortgage_statement_uploads: stop anonymous rows claiming someone else's
--    lead_id.                                                       [MEDIUM]
--
-- Was WITH CHECK (true), so a caller could attach a document record to any
-- borrower's lead. The Edge Function owns the lead_id linkage; the browser may
-- only describe the file it just uploaded.
-- ----------------------------------------------------------------------------

drop policy if exists funnel_anon_insert_uploads on public.mortgage_statement_uploads;

create policy uploads_public_insert on public.mortgage_statement_uploads
  for insert to anon, authenticated
  with check (
        lead_id is null                       -- linked server-side, not by the client
    and length(storage_path) between 1 and 512
    and (original_filename is null or length(original_filename) <= 255)
    and (mime_type is null or mime_type in (
          'application/pdf','image/jpeg','image/png','image/heic','image/webp'))
    and (source_slug is null or length(source_slug) <= 120)
    and status = 'uploaded'
  );

revoke insert on public.mortgage_statement_uploads from anon, authenticated;
grant insert (storage_path, original_filename, mime_type, source_slug, owner_key)
  on public.mortgage_statement_uploads to anon, authenticated;


-- ----------------------------------------------------------------------------
-- 5. Telemetry tables: cap the payload.                                 [LOW]
--
-- No data exposure, but both were unbounded anonymous inserts with a jsonb
-- column and no size limit — a storage-abuse vector and nothing else.
-- ----------------------------------------------------------------------------

drop policy if exists events_anon_insert on public.analytics_events;
create policy analytics_public_insert on public.analytics_events
  for insert to anon, authenticated
  with check (
        length(coalesce(event, '')) between 1 and 120
    and pg_column_size(coalesce(params, '{}'::jsonb)) <= 8192
  );

drop policy if exists "anon insert page_views" on public.page_views;
create policy page_views_public_insert on public.page_views
  for insert to anon, authenticated
  with check (
        length(coalesce(path, '')) <= 500
    and length(coalesce(referrer, '')) <= 500
    and length(coalesce(session_hash, '')) <= 128
    and length(coalesce(utm_source, '')) <= 120
    and length(coalesce(utm_medium, '')) <= 120
    and length(coalesce(utm_campaign, '')) <= 200
    and length(coalesce(country, '')) <= 8
    and length(coalesce(device, '')) <= 64
  );

commit;

-- ============================================================================
-- Verify
-- ============================================================================
-- select tablename, policyname, cmd, roles::text, with_check
--   from pg_policies where schemaname='public' order by tablename, cmd;
--
-- Expect zero rows (nothing sensitive readable by anon):
-- select table_name, privilege_type from information_schema.role_table_grants
--  where table_schema='public' and grantee='anon' and privilege_type='SELECT'
--    and table_name not in ('businesses','categories');
-- ============================================================================
