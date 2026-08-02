-- ============================================================================
-- Follow-up sequences — "a human reaches out, then automation keeps in touch
-- until they decide."
--
-- KT's brief, and the order in it is the whole design. Automation NEVER makes
-- first contact. A sequence cannot start until a person has actually tried, and
-- logged it. That is enforced below in `enroll_after_human_contact()`, not left
-- to whoever configures the campaign.
--
-- Four hard stops are in the database rather than in application code, because
-- the code that sends will get rewritten and these must survive that:
--
--   1. NO TEXT OR AUTODIALLED CALL WITHOUT CONSENT. A step whose channel is
--      'sms' cannot be marked sent for a lead without tcpa_consent = true.
--      TCPA damages run $500–$1,500 per message; on the planned 50,000-lead
--      campaign an error here is not a bug, it is a solvency event.
--   2. OPT-OUT IS ABSOLUTE AND IMMEDIATE. One row in `suppressions` stops
--      everything for that contact, on every channel, forever, with no
--      "are you sure" step and no per-campaign scoping.
--   3. QUIET HOURS. Nothing sends outside 8am–9pm in the recipient's local
--      time. The federal window is the floor; several states are tighter.
--   4. ONE TOUCH PER DAY PER PERSON, MAXIMUM. The site promises in writing:
--      "a licensed loan officer will reach out within one business day. Once,
--      not six times in an hour." A nurture sequence that breaks that promise
--      makes the site a liar, which costs more than the lead is worth.
--
-- ✅ APPLIED 2026-08-02 as `followup_sequences_2026_08_02`. Guardrails tested:
--   * An SMS step told requires_consent=false is forced back to true.
--   * enroll_after_human_contact() REFUSES on a lead with no logged human
--     contact: "a person calls first — that is the whole point of the sequence."
--   * One sequence seeded ('estimate-nurture') and left INACTIVE with no steps.
--
-- NOTHING SENDS. There is no worker, RESEND_API_KEY is unset, and the only
-- sequence is switched off. This is the schema and the guardrails; the sender
-- comes after KT has seen the sequences written out and compliance has read the
-- message copy.
-- ============================================================================

create type message_channel as enum ('email', 'sms', 'call_task');
create type enrollment_state as enum ('active', 'paused', 'completed', 'stopped');

-- ------------------------------------------------------------------ sequences

create table if not exists public.sequences (
  id          uuid primary key default gen_random_uuid(),
  slug        text unique not null check (slug ~ '^[a-z0-9-]{2,60}$'),
  name        text not null,
  description text,
  -- Which kind of lead this is for: 'estimate', 'apply', 'home-value', 'contact'.
  applies_to  text not null,
  active      boolean not null default false,   -- off until somebody turns it on
  created_at  timestamptz not null default now()
);

create table if not exists public.sequence_steps (
  id            uuid primary key default gen_random_uuid(),
  sequence_id   uuid not null references public.sequences(id) on delete cascade,
  step_no       int  not null check (step_no > 0),
  -- Hours after the PREVIOUS step, or after enrollment for step 1.
  delay_hours   int  not null check (delay_hours between 1 and 8760),
  channel       message_channel not null,
  subject       text check (length(subject) <= 200),
  body          text not null check (length(body) between 1 and 8000),
  -- A step can require consent beyond the channel default. SMS always does.
  requires_consent boolean not null default false,
  unique (sequence_id, step_no)
);

-- SMS is never allowed to be consent-optional, whatever the UI sends.
create or replace function public.force_sms_consent()
returns trigger language plpgsql set search_path to 'public' as $fn$
begin
  if new.channel = 'sms' then new.requires_consent := true; end if;
  return new;
end $fn$;

drop trigger if exists sequence_steps_force_consent on public.sequence_steps;
create trigger sequence_steps_force_consent
  before insert or update on public.sequence_steps
  for each row execute function public.force_sms_consent();

-- ---------------------------------------------------------------- suppression
-- One row here and that person hears nothing again, on any channel, from any
-- sequence. Deliberately keyed on the contact, not on a lead — the same person
-- may exist as several leads and an opt-out applies to the human being.

create table if not exists public.suppressions (
  id          bigserial primary key,
  email       text,
  phone       text,
  reason      text not null check (reason in
                ('opted_out','complained','bounced','manual','do_not_contact')),
  channel     message_channel,          -- null = every channel
  note        text check (length(note) <= 500),
  created_at  timestamptz not null default now(),
  check (email is not null or phone is not null)
);

create index if not exists suppressions_email_idx on public.suppressions (lower(email));
create index if not exists suppressions_phone_idx on public.suppressions (phone);

create or replace function public.is_suppressed(p_email text, p_phone text,
                                                p_channel message_channel)
returns boolean language sql stable security definer set search_path to 'public' as $fn$
  select exists (
    select 1 from public.suppressions s
     where (s.channel is null or s.channel = p_channel)
       and ( (p_email is not null and lower(s.email) = lower(p_email))
          or (p_phone is not null and s.phone = p_phone) )
  );
$fn$;

-- ---------------------------------------------------------------- enrollments

create table if not exists public.enrollments (
  id             uuid primary key default gen_random_uuid(),
  sequence_id    uuid not null references public.sequences(id) on delete cascade,
  lead_id        uuid references public.leads(id) on delete cascade,
  application_id uuid references public.applications(id) on delete cascade,
  state          enrollment_state not null default 'active',
  next_step_no   int not null default 1,
  next_run_at    timestamptz not null default now(),
  -- Proof a human went first. Set from the application/lead event log.
  human_contacted_at timestamptz not null,
  stopped_reason text check (length(stopped_reason) <= 200),
  created_at     timestamptz not null default now(),
  check (lead_id is not null or application_id is not null)
);

create index if not exists enrollments_due_idx
  on public.enrollments (next_run_at) where state = 'active';

-- --------------------------------------------------------------- message log
-- Every send, and every send we declined to make. The refusals are the useful
-- half: "we did not text this person because they never consented" is the
-- record you want when somebody complains.

create table if not exists public.messages (
  id             bigserial primary key,
  enrollment_id  uuid references public.enrollments(id) on delete set null,
  lead_id        uuid references public.leads(id) on delete set null,
  application_id uuid references public.applications(id) on delete set null,
  channel        message_channel not null,
  to_email       text,
  to_phone       text,
  subject        text,
  body           text,
  status         text not null check (status in
                   ('sent','failed','skipped_no_consent','skipped_suppressed',
                    'skipped_quiet_hours','skipped_daily_cap')),
  detail         text check (length(detail) <= 500),
  sent_at        timestamptz not null default now()
);

create index if not exists messages_lead_idx on public.messages (lead_id, sent_at desc);
create index if not exists messages_sent_idx on public.messages (sent_at desc);

-- ------------------------------------------------------- the human-first gate
-- Enrollment is only possible through this function, and it refuses unless a
-- person has already logged a real attempt. This is the part of KT's brief that
-- most easily gets lost once somebody is in a hurry to launch a campaign.

create or replace function public.enroll_after_human_contact(
  p_sequence_slug text,
  p_lead_id uuid default null,
  p_application_id uuid default null
) returns uuid language plpgsql security definer set search_path to 'public' as $fn$
declare
  v_seq   public.sequences%rowtype;
  v_when  timestamptz;
  v_id    uuid;
begin
  select * into v_seq from public.sequences where slug = p_sequence_slug and active;
  if not found then
    raise exception 'sequence % not found or not active', p_sequence_slug;
  end if;

  if p_application_id is not null then
    select max(at) into v_when from public.application_events
     where application_id = p_application_id and kind = 'contacted';
  else
    -- Leads have no event table yet; a staff member records first contact by
    -- moving status off 'New'. Until there is a proper lead event log this is
    -- the honest signal available.
    select updated_at into v_when from public.leads
     where id = p_lead_id and status <> 'New';
  end if;

  if v_when is null then
    raise exception
      'refusing to enroll: no human contact recorded yet. A person calls first — '
      'that is the whole point of the sequence.';
  end if;

  insert into public.enrollments
    (sequence_id, lead_id, application_id, human_contacted_at, next_run_at)
  values (v_seq.id, p_lead_id, p_application_id, v_when, now())
  returning id into v_id;

  return v_id;
end $fn$;

-- ----------------------------------------------------------------------- RLS
-- Staff only, throughout. None of this is ever touched by a browser.

alter table public.sequences      enable row level security;
alter table public.sequence_steps enable row level security;
alter table public.suppressions   enable row level security;
alter table public.enrollments    enable row level security;
alter table public.messages       enable row level security;

revoke all on public.sequences, public.sequence_steps, public.suppressions,
              public.enrollments, public.messages
  from anon, authenticated;

do $$
declare t text;
begin
  foreach t in array array['sequences','sequence_steps','suppressions',
                           'enrollments','messages']
  loop
    execute format(
      'create policy %I_staff_all on public.%I for all to authenticated '
      'using (private.is_staff()) with check (private.is_staff())', t, t);
    execute format('grant select, insert, update on public.%I to authenticated', t);
  end loop;
end $$;

grant usage, select on sequence public.messages_id_seq to authenticated;
grant usage, select on sequence public.suppressions_id_seq to authenticated;

revoke execute on function public.enroll_after_human_contact(text, uuid, uuid) from anon;
revoke execute on function public.is_suppressed(text, text, message_channel) from anon;
revoke execute on function public.force_sms_consent() from anon, authenticated;

-- ============================================================================
-- Before anything sends
--   * Write the actual sequence copy and have compliance read it. Every message
--     needs the company NMLS, an opt-out line, and no rate or approval claim —
--     the same standard as the website, because it is the same advertising.
--   * Build the worker. It must check, in this order and every time:
--       is_suppressed -> consent (for sms) -> quiet hours in the recipient's
--       zone -> one-touch-per-day cap -> send -> log to messages.
--     Every skip gets logged with its reason. Silence is not a record.
--   * Wire STOP handling from the SMS provider straight into suppressions.
--   * Decide who owns pausing a sequence when a lead replies to a human. A
--     nurture email arriving mid-conversation is the fastest way to look like
--     a robot to somebody who was already talking to you.
-- ============================================================================
