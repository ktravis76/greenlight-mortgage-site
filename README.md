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
— what they could save, roughly what they could afford — without a hard credit pull,
without a phone call, without talking to anyone. That is the trade: genuine value up
front, and the contact information comes because they *want* the result, not because we
gated it.

It works because every competitor makes you call to find anything out. We just tell you.

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
- **Tools capture by being useful.** Someone finishes the affordability calculator; the
  natural next step is "want this emailed to you?" They already got the answer for free.
  The result is never held hostage behind a form.
- **Blog posts each carry their own soft offer**, matched to the post. A VA refinance
  article offers the VA savings worksheet, not a generic newsletter signup.
- **Multiple exits per page, all low-commitment.** Read more · get it emailed · text a
  question · book a call. Let people self-select their temperature instead of forcing
  everyone into "Apply Now."
- **Say what happens next.** "We'll email it in a minute. No calls unless you ask."
  Then honor it. Trust is the conversion mechanism here.

**Never:** exit-intent popups, countdown timers, fake scarcity, content locked behind a
form, autoplay, or a chat bubble that opens itself. Those all read as desperate, and
they read that way fastest to exactly the referral-quality people worth having.

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

Static HTML/CSS today. No build step, no dependencies. Deploys on push. Supabase backs
the tools and structured intake; forms post through to Konnectd.
