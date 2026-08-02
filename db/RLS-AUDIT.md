# RLS audit — Supabase `athovwknbwbbqworsbrm`

Audited 2026-08-01.

> **Correction, same day.** This document originally said every table held zero rows.
> That repeated the claim in START-HERE.md instead of counting, and it is wrong:
> `leads` holds **4 rows** (2026-06-26) and `soft_quotes` holds **5** (2026-07-28,
> the VA screener). `businesses` holds 140 and `categories` 20 — that is the Longview
> directory, a separate app sharing this database.
>
> What changes: the findings below are not purely hypothetical, and the remediation
> now runs against a table with real rows. The migration is policy-and-grants only —
> it does not read, alter, or delete a single row — but "nothing has happened yet" was
> not a safe thing to have written. The exposure in §1 has been live for whatever
> period those views have existed.

> ## ✅ APPLIED 2026-08-01
>
> Migration `rls_hardening_2026_08_01`, on KT's go-ahead. Verified after:
>
> * `soft_quotes_daily` and `soft_quotes_by_source` now return **401 permission
>   denied** to the publishable key. The exposure in §1 is closed.
> * A forged-consent insert (`tcpa_consent`, `consent_ip`, `consent_at` from a
>   browser) is **rejected** — `42501 permission denied for table leads`.
> * An attempt to self-escalate (`priority: true`, `status: "Hot"`) is **rejected**.
> * A normal lead insert on permitted columns still returns **201**.
> * **The VA screener still works.** It posts with `Prefer: return=minimal`, which
>   needs no SELECT — confirmed 201 against the live endpoint with its exact call
>   shape. An earlier smoke test failed only because it used
>   `return=representation`, which does require SELECT and correctly no longer has
>   it. That was the test being wrong, not the screener.
> * The archive (`businesses`, `categories`) still reads fine — the public site
>   depends on it.
> * All test rows removed; back to the pre-existing 4 leads and 5 soft_quotes.
>
> Follow-up migration `revoke_execute_on_trigger_functions` also removed RPC
> EXECUTE from the five trigger/event-trigger functions the linter flagged and
> pinned the last mutable `search_path`. Both SECURITY DEFINER view errors are
> gone from the advisor.

---

## Headline

The read side is sound. No table exposes borrower names, emails, phones, or TCPA
consent to anonymous callers — `leads`, `soft_quotes` and `mortgage_statement_uploads`
are insert-only for `anon`, with SELECT gated behind `private.is_staff()`. That is the
right shape and whoever built it got the hard part right.

The write side is the problem, and one view leaks.

---

## 1 — `soft_quotes` aggregates are readable by the entire internet · HIGH

`soft_quotes_daily` and `soft_quotes_by_source` are **SECURITY DEFINER views**, which
means they run with the view owner's rights and ignore RLS on `soft_quotes` underneath.
Both grant `SELECT` to `anon`:

| view | grantee | privileges |
|---|---|---|
| `soft_quotes_daily` | `anon` | DELETE, INSERT, REFERENCES, **SELECT**, TRIGGER, TRUNCATE, UPDATE |
| `soft_quotes_by_source` | `anon` | DELETE, INSERT, REFERENCES, **SELECT**, TRIGGER, TRUNCATE, UPDATE |

Anyone holding the publishable key — which is, by design, in the page source of this
site the moment it ships — can `GET /rest/v1/soft_quotes_daily` and read:

- daily lead volume, and the strong / worth-a-call / thin-or-dead split
- `avg_quoted_rate`, the average rate coming off the quote engine
- `balance_screened`, total mortgage balance run through the pipeline

**To be accurate about the severity:** both views are pure aggregates with a `GROUP BY`.
No names, emails, phone numbers, balances-per-person, or consent records are reachable
through them. This is not a GLBA/NPI exposure. It is competitive intelligence — pipeline
volume, conversion quality, and average pricing — published to any competitor who views
source. That is bad, but it is a different kind of bad than a borrower data breach, and
it should not be escalated as one.

The write grants (INSERT/UPDATE/DELETE/TRUNCATE to `anon`) would fail in practice, since
an aggregate view with `GROUP BY` is not auto-updatable. They are still wrong and should
not be there.

**Fix:** rebuild both as `security_invoker = true`, revoke everything from `anon`, grant
`SELECT` to `authenticated` only. Then RLS on `soft_quotes` applies and only staff can
read them.

> ⚠️ **This is a launch blocker.** It is only exploitable once the publishable key is
> public, which happens the moment this site deploys. Fix before the first deploy, not
> after.

## 2 — `leads` accepts anything, including forged TCPA consent · HIGH

```
policy funnel_anon_insert_leads · INSERT · {anon,authenticated} · WITH CHECK (true)
```

`WITH CHECK (true)` means an anonymous caller can insert a row with any values in any
column, unbounded length, at any rate. On this particular table that includes
`tcpa_consent`, `consent_at`, `consent_ip`, `consent_ua`, `priority`, `status`, and
`estimated_monthly_savings`.

Two consequences:

**The consent log is not evidence.** The whole point of logging consent text, timestamp,
IP and user agent is to be able to prove, later, that a specific person agreed to be
called. A record any anonymous caller can write says nothing about who agreed to what.
With a 50,000-lead SMS campaign planned on top of this data, a consent trail that cannot
be defended is a per-message liability, and the volume is what turns it into a large one.

**There is no rate or size limit.** Nothing stops a script inserting until the table is
the size of the disk.

Compare `directory_leads` on the same database, which validates name length, email
shape, phone length, message and referrer size. The table holding consumer contact
details and consent has less validation than the directory sign-up form.

**Fix, in two parts:**

1. A real `WITH CHECK` — length bounds, email shape, and a whitelist of `status` /
   `priority` values. In the migration.
2. **Consent must not be written from the browser at all.** A client cannot know its own
   IP and can lie about all four consent fields. The estimator therefore posts to an
   Edge Function that stamps `consent_ip` from the request headers, `consent_ua` from
   the request, and `consent_at` from the server clock, using the service-role key, and
   the four consent columns get revoked from `anon` entirely. That is why
   `/tools/estimate` on this site posts to a function rather than straight to PostgREST.

## 3 — `soft_quotes` cannot be written by a signed-in user · FUNCTIONAL BUG

```
policy "anon can insert quotes" · INSERT · {anon} · WITH CHECK (true)
```

The role list is `{anon}` only, but `INSERT` is granted to both `anon` and
`authenticated`. A logged-in staff member running the internal screener authenticates,
becomes `authenticated`, no longer matches the policy, and the insert is refused.

Nobody has hit this because the table has zero rows. It will surface the first time a
loan officer is signed in while using the screener.

Also: `soft_quotes` has no SELECT policy at all, so the 41-column quote engine is
write-only to everyone except `service_role`.

## 4 — `mortgage_statement_uploads` accepts arbitrary `lead_id` and `storage_path` · MEDIUM

Same `WITH CHECK (true)`. An anonymous caller can insert a row claiming any
`storage_path` and pointing `lead_id` at somebody else's lead, attaching a document
record to a borrower who never uploaded it. Needs bounds and the same
Edge-Function-mediated write as `leads`.

## 5 — `analytics_events` and `page_views` are unbounded anon inserts · LOW

`WITH CHECK (true)` with a `jsonb` params column and no size cap. Storage-abuse vector,
no data exposure. Cap the payload size and the string lengths.

## 6 — Advisor warnings that are not real · NOTED, NO ACTION

The linter flags `handle_new_staff_user()`, `promote_allowlisted_admin()` and
`rls_auto_enable()` as anon-executable SECURITY DEFINER functions. All three were read:
the first two return `trigger` and the third returns `event_trigger`, so calling them
over RPC fails before doing anything — `pg_event_trigger_ddl_commands()` errors outside
a real event-trigger context. All three correctly pin `search_path`. Both
`is_admin()` and `private.is_staff()` are SECURITY DEFINER with `search_path` pinned to
`public`, which is correct.

`allowed_staff` shows as "RLS enabled, no policies". That is deny-all, which is the
right answer — the only reader is `handle_new_staff_user()`, which is SECURITY DEFINER
and bypasses it. No change needed.

## 7 — Two parallel staff-auth systems on one database · NOTED

`admin_users` + `admin_email_allowlist` + `is_admin()` (a business-directory app) sit
alongside `profiles` + `allowed_staff` + `private.is_staff()` (this mortgage site) in
the same `public` schema. They are unrelated and neither knows about the other.

Nothing is broken today. But a future policy written against the wrong helper grants the
wrong people access, and the names are close enough to make that a live risk. Worth
splitting the directory app into its own schema or its own project before either grows.

---

## Applying it

```bash
supabase db push
```

or paste [`2026-08-01-rls-hardening.sql`](2026-08-01-rls-hardening.sql) into the SQL
editor. Re-run the audit afterwards:

```sql
select tablename, policyname, cmd, roles::text, with_check
from pg_policies where schemaname='public' order by tablename;
```

Sections 1, 5 and 6 are safe to apply immediately. **Sections 2, 3 and 4 change surfaces
the internal VA screener writes to** — confirm the screener still records a quote
end-to-end after applying, before pointing any consumer traffic at the estimator.
