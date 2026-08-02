# greenlight-mortgage-site

Consumer marketing site and partner-tools funnel for **Greenlight Mortgage**, powered by Co/LAB Lending. Longview, TX.

- **GitHub:** https://github.com/ktravis76/GreenlightMortgage
- **Vercel project:** `greenlight-mortgage-site`
- **Preview:** https://greenlight-mortgage-site.vercel.app
- **Domain:** not yet assigned — pending KT decision
- **Supabase:** project `athovwknbwbbqworsbrm` (Greenlight Mortgage, us-east-2)

## Naming — two different things, easy to confuse

| Vercel project | What it actually is |
| --- | --- |
| `greenlight-mortgage-site` | **This repo.** Public marketing site + funnel. |
| `greenlight-mortgage` | **Internal Sales Dashboard.** VA IRRRL pipeline, speed-to-lead, leaderboard, role-based views, live Teli data. Not a website. Do not deploy over it. |

**Pending rename:** the dashboard project should become `greenlight-mortgage-sales` so
the two stop colliding. **Not done yet** — renaming changes its `.vercel.app` URL, which
the sales team has bookmarked and which may be linked from ClickUp, Notion, and email.
Needs a notice window and a link sweep first.

## What this site has to do

Not a brochure. A funnel that walks a stranger from first click to submitted application,
plus a set of tools that make Greenlight the useful one to partner with.

### The hook: the Soft Quote / Estimated Savings tool

This is the centerpiece. Everything else on the site exists to get people here.

A visitor answers a handful of easy questions and gets a real, personalized number back
— what they could save, roughly what they could afford — with no hard credit pull and no
phone call required.

**Results are gated.** Name, phone, and email are required to see the output. That is the
trade, and it is stated plainly up front so nobody feels tricked at the end.

It works because every competitor makes you call and wait days to find anything out.
Here it takes two minutes and you keep the number.

**How to gate it without losing people:**

- **Say the ask before they start.** "Six questions, about two minutes. We'll need your
  name, email, and phone to send the results." Surprise gates at the finish line are
  where people rage-quit and never come back.
- **Ask at the end, not the beginning.** Let them answer the loan questions first. Sunk
  effort makes the form feel like the last step rather than a toll booth.
- **Three fields. Nothing else.** No address, no employer, no SSN, no "how did you hear
  about us." Every extra field costs completions.
- **Show the result on screen and email it.** They earned it. Do not make them go dig
  through their inbox for something they just filled out a form to get.
- **Promise the follow-up honestly and keep it.** "A licensed loan officer will reach out
  within one business day." Then do that — not six calls in an hour. The phone number is
  the most valuable thing on the page and the fastest way to burn goodwill.

> **⚠️ TCPA — this matters more than usual here.**
> Collecting a phone number for marketing calls or texts requires **express written
> consent**, and it needs its own clearly worded checkbox — not buried in a privacy link,
> not pre-ticked. It must name Greenlight, cover autodialed and pre-recorded calls and
> texts, state that consent is **not a condition of obtaining a loan**, and explain how to
> opt out.
>
> This is directly load-bearing for the planned 50,000-lead SMS campaign. Consent captured
> sloppily here is a per-message liability later. Get the wording from compliance before
> the tool ships, and log consent text, timestamp, and IP with every submission.

**Where it lives:** its own page, embedded on the homepage, on every loan-program page,
and offered at the end of relevant blog posts. It is the default call to action across
the entire site — softer than "Apply Now" and far more likely to be clicked.

> **⚠️ Naming — get this right before launch.**
> Internally the team says "Soft Quote." **Do not put the word *quote* in front of
> consumers.** A quote implies an actual rate offer, and only a licensed loan officer can
> give one after a real application. Using it loosely on a public page is precisely the
> kind of thing that draws regulatory attention.
>
> Consumer-facing labels to use instead: **"Estimated Savings," "Savings Estimate,"
> "See What You Could Save," "Ballpark Your Payment."** Keep "Soft Quote" for internal
> and team-facing surfaces only. Same tool, safer label.
>
> Every result screen carries: *estimate only · not a quote or approval · subject to
> credit approval and underwriting · not a commitment to lend*, plus EHO and NMLS. One
> tight line under the number, not a wall. Compliance signs off before it ships.

### The capture philosophy — everywhere, never salesy

Give people a reason to leave their information on **every page**, including blog posts —
and make each one feel like a favor rather than a pitch. Maximum opportunity, minimum
pressure. If a visitor feels sold to, we have already lost them.

**What that means in practice:**

- **Trade value for the information, every time.** Nobody fills in a form for "Contact Us."
  They will for "Send me the East Texas first-time buyer guide," "Email me this number,"
  or "Tell me when rates in my range move." The ask is always attached to something
  they actually want.
- **Ask for as little as possible.** One field beats four. Email alone is a win — get the
  rest later once there is a reason to. Progressive, never a wall.
- **Tools are the exception, and they earn it.** The Estimated Savings tool gates its
  result behind name, phone, and email — because the output is genuinely worth it and the
  ask is stated before they start. Everything *else* stays ungated. If every calculator
  and guide on the site demands a phone number, the whole place reads as a lead trap.
- **Blog posts each carry their own soft offer**, matched to the post. A VA refinance
  article offers the VA savings worksheet, not a generic newsletter signup.
- **Multiple exits per page, all low-commitment.** Read more · get it emailed · text a
  question · book a call. Let people self-select their temperature instead of forcing
  everyone into "Apply Now."
- **Say what happens next.** "We'll email it in a minute. No calls unless you ask."
  Then honor it. Trust is the conversion mechanism here.

**Never:** exit-intent popups, countdown timers, fake scarcity, surprise gates sprung
after someone has already done the work, autoplay, or a chat bubble that opens itself.
Those all read as desperate, and they read that way fastest to exactly the
referral-quality people worth having.

### 1. Consumer funnel

**Land → learn → self-qualify → talk to a human → apply.**

No dead ends, no bare "contact us." Every page ends with the obvious next step.

### 2. Forms — all of them, better than the originals

Carried over from kennethtravis.com and rebuilt:

- **Loan application** — see the compliance note below before building
- Contact / general inquiry
- Mortgage calculator
- Home valuation request
- Testimonial submission
- Survey
- Live chat / text widget (exists today — replace it, do not lose it)

All structured submissions post directly into **GoHighLevel / Konnectd**
(location `LRAzmr7bQKMMlXiYfvi6`). They do **not** email a person. Today leads land in
individual inboxes and get reconciled by hand — the biggest operational drag on the
follow-up team, and this site is where it gets fixed.

> **⚠️ Application form — read before building.**
> Apply Online currently hands off to `greenlight.my1003app.com/233918/register`, a
> licensed LOS. **Keep it that way.** A full 1003 collects Social Security numbers,
> income, and asset detail — nonpublic personal information under GLBA. Do not rebuild
> the full 1003 here.
>
> Build instead: a short, friendly pre-application intake capturing only what is needed
> to start a conversation, then a clean handoff to the LOS. Better experience, none of
> the liability.

### 3. Video

Reuse the video from the current site, starting with the homepage file
(`/wp-content/themes/custom-kenneth-travis/images/kt-video.mp4`). Pull the originals
before the domain flips — do not hotlink to the old site. Longer term these feed from
the Descript pipeline, same as The Coop.

### 4. Partner tools — B2B

The differentiator. Competitors have brochures; this becomes the site other professionals
actually use. Tracked in **Greenlight Tool Lab → 06 B2B Tools**.

- **Realtors** — buyer affordability, seller net proceeds, rent vs. buy, co-branded flyers, pre-qual status
- **Mortgage lenders / LOs** — scenario desk, comp comparison, the Co/LAB "Third Option" path
- **Title companies** — closing timelines, document checklists, contact routing
- **Roofing contractors** — renovation and repair financing paths, insurance-claim timing
- **Home inspectors** — which findings affect financing, repair-escrow basics
- **Insurance agents, appraisers, builders** — same pattern: the thing they need from a lender, self-serve

## Compliance — present, never overbearing

Everything below is required. **How** it appears is a design decision, and the wrong
answer kills conversion. A wall of grey legal text at the top of a page reads as a
warning label. Done properly it reads as competence.

**The pattern:**

- **Footer carries the weight.** Full disclosure block lives once, in the footer, set
  small and quiet but legible. It is not hidden — it just is not shouting.
- **Inline only where it is actually earned.** A number on screen gets one short line
  next to it: *"Estimate only. Subject to credit approval and underwriting."* One line.
  Not a paragraph, not a modal, not a checkbox.
- **Trust marks are design elements, not disclaimers.** EHO mark, NMLS ID, and
  "Powered by Co/LAB Lending" belong in the header and footer as clean, deliberate marks
  — the same way a bank shows FDIC. They signal legitimacy. Treat them as brand assets.
- **Plain English over legalese** wherever the wording is ours to choose. "We shop
  lenders for you, and nothing here is a loan offer" beats a Reg Z recital.
- **Never interrupt the flow.** No consent gates, no acknowledgement checkboxes, no
  interstitials between a visitor and the next step.
- **Legible or it does not count.** Minimum 12px, real contrast, no 6pt grey-on-grey.
  Illegible disclosure is not disclosure — and it looks cheap.

**Required on every consumer-facing page:**

- "Powered by Co/LAB Lending"
- Company NMLS # and branch NMLS #
- Individual NMLS # on every loan officer bio
- Equal Housing Opportunity
- "This is not a commitment to lend"
- "Subject to credit approval and underwriting" on anything showing a number
- Texas Department of Savings and Mortgage Lending license disclosure
- No stated rates, APRs, payments, or approval guarantees
- Rate quotes and eligibility deferred to licensed loan officers

Any tool that outputs dollar figures (savings estimator, cheat sheet, affordability, net
proceeds) needs estimate-only framing and compliance sign-off before it ships.

**Two problems inherited from the current site — do not copy them forward:**

1. The footer carries a Reg Z §226.2 *"business professionals only"* disclaimer on a page
   that opens "Dear Future Homeowner" and asks consumers to apply. Those contradict.
   Compliance resolves the wording before it carries over.
2. The welcome letter says *"I guarantee."* Rephrase.

## Migration source

Replaces the mortgage content on kennethtravis.com, which runs as **site #46 on the
Loan Officer X WordPress multisite** — a tenant install Greenlight does not control.

That domain ranks **#2 organically for "mortgage longview tx."** Cutover requires a full
301 redirect map or that equity is lost.

Pages to carry over: Home, Loan Options (Conventional, FHA, **Jumbo**, VA, USDA,
Refinancing), Resources, Learning Center, Blog, About, Reviews, Testimonials, Contact,
Mortgage Calculator, Home Valuation Report, Privacy Policy.

Also migrate: all 7 client testimonials, the six-state license footer (TX, AL, FL, LA,
ND, SC), Core Values, and the "Green means GO!" tagline.

## Stack

Static HTML/CSS/vanilla JS. No framework, no npm, no dependencies. Deploys on push.
Supabase backs the tools and structured intake; forms post through to Konnectd.

## Build

Every page is generated. Nothing in the tree is hand-edited HTML — edit the generator
and rebuild, or your change is gone next time somebody runs the build.

```bash
python3 build.py                       # generate everything, then run the checks
python3 -m http.server 8787            # preview at http://127.0.0.1:8787
```

| File | What it owns |
| --- | --- |
| `sitegen.py` | Header, footer, compliance block, schema, the TCPA sentence, verified facts. **Single source of truth.** |
| `build-loans.py` | Six loan programs + `/loans` hub |
| `build-pages.py` | Homepage, about, contact, testimonials, reviews, learn, resources, blog, survey, legal |
| `build-tools.py` | `/tools` hub, Estimated Savings, calculator, home value |
| `build.py` | Runs all three, writes `sitemap.xml` + `robots.txt`, then runs `check.py` |
| `check.py` | Link resolution + compliance gate. Exits non-zero on failure. |

`sitegen.py` is named that, not `site.py`, because Python imports a stdlib module called
`site` at startup and a local `site.py` would be silently shadowed by it.

### The checks are not advisory

```bash
python3 check.py
```

- **Links.** Resolves every internal `href`/`src` against the built tree the way Vercel
  would serve it. A previous pass shipped nav pointing at `/loans/va` while the files sat
  at `/loans/va.html` and every link on the site 404'd. This is what stops that.
- **Compliance.** Greps rendered copy for guarantees, superlative rate claims, stated
  rate/APR figures, and the Reg Z "business professionals only" line. Negation-aware, so
  the required disclaimers do not trip it. Also fails if a rate input ships pre-filled —
  a number sitting in that box reads as a rate we are offering.
- **Open items.** Prints every unconfirmed fact deliberately marked on a live page.

## State of the build

Marketing site and tools are built and passing. **The site is not launch-ready**, and the
blockers are listed here rather than buried.

### Launch blockers

1. **Apply `db/2026-08-01-rls-hardening.sql`.** Two SECURITY DEFINER views over
   `soft_quotes` are readable by anyone holding the publishable key, which ships in this
   site's page source. Aggregates only — no borrower PII — but it publishes lead volume,
   conversion mix and average quoted rate to any competitor. Also fixes an unvalidated
   `leads` insert that lets anyone forge a TCPA consent record. Full write-up in
   [`db/RLS-AUDIT.md`](db/RLS-AUDIT.md). **Nothing has been applied** — two sections touch
   surfaces the live VA screener writes to.
2. **Deploy the Edge Function**, then set `LEAD_ENDPOINT_LIVE: true` in `config.js`.
   Until then every form tells the visitor it is not connected and shows the office number.
   It does not fake a thank-you. See `supabase/functions/submit-lead/`.
3. **Compliance sign-off on the TCPA sentence** in `sitegen.py` (`TCPA_TEXT`) and on the
   Texas SML complaint notice (`TX_SML_NOTICE`, currently a marked placeholder — we did
   not invent the regulator's address).
4. **Legal review of `/privacy`.** Drafted to describe what the site actually does; GLBA
   annual-notice obligations need a lawyer's eye.
5. **Confirm the team roster.** `/about` ships six deliberately blank cards. No colleague
   has been invented, and no unconfirmed NMLS number published.

### Also outstanding

- Homepage video has no captions or transcript — the biggest known accessibility gap,
  and it is disclosed on `/accessibility` rather than quietly ignored.
- Eight WordPress blog posts still to migrate off the vendor multisite. One original post
  was written here to exercise the template; KT should read it before it stays up.
- Google / Facebook / Zillow profile URLs unknown, so `/reviews` links nowhere yet. No
  star rating is published anywhere — unsourced performance claims stay off a regulated site.
- Office hours unconfirmed, so they are absent from the page and from schema.
- Resource PDFs were never recovered from the old site. Pull them before the domain flips
  — that is the one irreversible step in this project.
- CSP allows `'unsafe-inline'` for scripts because of the anti-flash inline snippet in
  `<head>`. Moving to hashes would tighten it.
- Phase 2 (`/portal`, `/admin`) not started, per the brief's ordering.
