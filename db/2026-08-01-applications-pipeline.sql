-- ============================================================================
-- Applications + the internal pipeline ("the conveyor belt")
-- Written 2026-08-01 from KT's spec. NOT YET APPLIED.
--
-- WHAT THIS DOES AND DELIBERATELY DOES NOT DO
--
-- KT asked for Apply Online to become our own form rather than handing off to
-- the external LOS, for it to reach kenneth@glmtg.com, and for the team to pass
-- a file down a line where everyone can see what is coming, what they hold, and
-- what they have passed on.
--
-- This builds all of that for a PRE-APPLICATION INTAKE. It does not build a
-- full 1003, and the schema below has nowhere to put one:
--
--   * There is no ssn column, no date_of_birth, no account numbers, no
--     employer income detail. Not "nullable" — absent. A column that does not
--     exist cannot be filled in by a well-meaning teammate at 6pm.
--   * A completed 1003 is nonpublic personal information under GLBA. Holding it
--     puts Greenlight under the Safeguards Rule for this database, this hosting,
--     this access model and this vendor list — a different compliance posture
--     from a marketing site, and one that needs a decision, not a migration.
--   * The licensed LOS at greenlight.my1003app.com already carries that
--     liability under Kenneth's own NMLS. The intake below hands off to it
--     clean, with the conversation already started.
--
-- So: we own the front door, the routing, the visibility and the follow-up.
-- The SSN-bearing part stays where the licence already covers it. If KT wants
-- the full 1003 in-house anyway, that is his call to make with compliance —
-- but it should be an explicit decision, not something that arrives as a side
-- effect of "make the apply button ours".
--
-- ON EMAIL: the notification to kenneth@glmtg.com is a heads-up containing the
-- applicant's name and a link. It does not contain the intake answers. Email is
-- the least controlled surface we have, it forwards, it syncs to phones, and
-- "leads land in individual inboxes and get reconciled by hand" is the exact
-- problem this project exists to fix. The record lives in the pipeline; the
-- email tells you to go look at it.
-- ============================================================================

begin;

-- ---------------------------------------------------------------- the stages
-- KT's conveyor belt. Order matters — it drives the board columns.

create type application_stage as enum (
  'new',              -- just submitted, nobody has touched it
  'contact',          -- first call / speed-to-lead
  'pre_qual',         -- gathering the basics, running numbers
  'loan_officer',     -- with a licensed LO
  'processing',       -- docs in, file being built
  'submitted_to_los', -- handed to the licensed 1003 system
  'closed_won',
  'closed_lost'
);

create table if not exists public.applications (
  id                uuid primary key default gen_random_uuid(),
  reference         text unique not null default
                      'GL-' || to_char(now(),'YYMMDD') || '-' ||
                      upper(substr(md5(random()::text), 1, 4)),

  -- Contact. The most sensitive thing here is a phone number.
  first_name        text not null check (length(btrim(first_name)) between 1 and 80),
  last_name         text not null check (length(btrim(last_name))  between 1 and 80),
  email             text not null check (email ~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$'
                                         and length(email) <= 254),
  phone             text not null check (length(phone) between 7 and 32),
  preferred_contact text check (preferred_contact in ('phone','text','email')),
  best_time         text check (length(best_time) <= 60),

  -- What they want. Ranges and buckets, never exact financial identifiers.
  purpose           text not null check (purpose in ('purchase','refinance','cash_out','not_sure')),
  property_city     text check (length(property_city) <= 80),
  property_state    text check (length(property_state) <= 2),
  price_band        text check (length(price_band) <= 40),
  down_band         text check (length(down_band) <= 40),
  timeline          text check (length(timeline) <= 40),
  employment        text check (length(employment) <= 40),
  credit_band       text check (length(credit_band) <= 40),   -- self-reported range
  veteran           boolean not null default false,
  first_time_buyer  boolean not null default false,
  working_with_agent boolean not null default false,
  agent_name        text check (length(agent_name) <= 120),
  notes             text check (length(notes) <= 4000),

  -- Consent, server-stamped. Same rule as leads: a browser cannot know its own
  -- IP and cannot be trusted to report it.
  tcpa_consent      boolean not null default false,
  consent_text      text,
  consent_at        timestamptz,
  consent_ip        text,
  consent_ua        text,

  -- Pipeline state
  stage             application_stage not null default 'new',
  assigned_to       uuid references public.profiles(user_id),
  stage_entered_at  timestamptz not null default now(),
  due_at            timestamptz,
  source            text default 'web:apply',

  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);

comment on table public.applications is
  'Pre-application intake. Deliberately contains NO SSN, date of birth, account '
  'numbers or itemised income — the full 1003 stays on the licensed LOS. Do not '
  'add those columns without a GLBA Safeguards review.';

create index if not exists applications_stage_idx on public.applications (stage, stage_entered_at);
create index if not exists applications_assigned_idx on public.applications (assigned_to)
  where stage not in ('closed_won','closed_lost');

-- --------------------------------------------------------------- the handoffs
-- Every movement, who did it, who it went to. This is what makes the belt
-- visible: "on the way to me", "with me now", "I passed it on".

create table if not exists public.application_events (
  id              bigserial primary key,
  application_id  uuid not null references public.applications(id) on delete cascade,
  at              timestamptz not null default now(),
  actor           uuid references public.profiles(user_id),
  kind            text not null check (kind in
                    ('created','stage_changed','assigned','note','contacted','document','closed')),
  from_stage      application_stage,
  to_stage        application_stage,
  assigned_to     uuid references public.profiles(user_id),
  body            text check (length(body) <= 4000)
);

create index if not exists application_events_app_idx
  on public.application_events (application_id, at desc);

-- Keep stage_entered_at honest, and log the move without the caller having to
-- remember to. A handoff history that depends on discipline is not a history.
create or replace function public.applications_track_stage()
returns trigger language plpgsql security definer set search_path to 'public' as $$
begin
  if new.stage is distinct from old.stage then
    new.stage_entered_at := now();
    insert into public.application_events
      (application_id, actor, kind, from_stage, to_stage, assigned_to)
    values (new.id, auth.uid(), 'stage_changed', old.stage, new.stage, new.assigned_to);
  elsif new.assigned_to is distinct from old.assigned_to then
    insert into public.application_events
      (application_id, actor, kind, assigned_to)
    values (new.id, auth.uid(), 'assigned', new.assigned_to);
  end if;
  new.updated_at := now();
  return new;
end $$;

drop trigger if exists applications_track_stage on public.applications;
create trigger applications_track_stage
  before update on public.applications
  for each row execute function public.applications_track_stage();

-- --------------------------------------------------------------------- RLS
-- Same posture as leads: the public may create, only staff may read.
-- The browser writes nothing sensitive; the Edge Function stamps consent.

alter table public.applications      enable row level security;
alter table public.application_events enable row level security;

-- No public insert policy at all. Applications arrive ONLY through the
-- submit-application Edge Function using the service role, because the consent
-- record has to be stamped server-side to be worth anything.
revoke all on public.applications      from anon, authenticated;
revoke all on public.application_events from anon, authenticated;

create policy applications_staff_read on public.applications
  for select to authenticated using (private.is_staff());
create policy applications_staff_update on public.applications
  for update to authenticated using (private.is_staff()) with check (private.is_staff());

create policy events_staff_read on public.application_events
  for select to authenticated using (private.is_staff());
create policy events_staff_insert on public.application_events
  for insert to authenticated with check (private.is_staff());

grant select, update on public.applications to authenticated;
grant select, insert on public.application_events to authenticated;
grant usage, select on sequence public.application_events_id_seq to authenticated;

-- ------------------------------------------------------------- the board view
-- What the team sees. One row per application with how long it has been sitting
-- where it is — the number that actually drives a speed-to-lead conversation.

create or replace view public.pipeline_board
with (security_invoker = true) as
select a.id, a.reference, a.stage, a.assigned_to,
       p.full_name as assigned_name,
       a.first_name || ' ' || left(a.last_name, 1) || '.' as who,
       a.purpose, a.property_city, a.timeline, a.veteran,
       a.stage_entered_at,
       round(extract(epoch from (now() - a.stage_entered_at)) / 3600, 1) as hours_in_stage,
       a.created_at
from public.applications a
left join public.profiles p on p.user_id = a.assigned_to
where a.stage not in ('closed_won','closed_lost')
order by a.stage, a.stage_entered_at;

grant select on public.pipeline_board to authenticated;

commit;

-- ============================================================================
-- Still to do once this is applied
--   * Deploy supabase/functions/submit-application
--   * Seed allowed_staff + profiles so is_staff() returns true for the team
--     (profiles is currently EMPTY — every staff policy denies everyone today)
--   * Build the board UI at /admin
-- ============================================================================
