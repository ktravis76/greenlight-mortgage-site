# Loan-page funnel spec — Facebook lead-ad destinations

Every loan page becomes a post-lead-ad funnel page. Read this whole file before building.

## The traffic reality that shapes everything

Visitors arrive from a **Facebook Lead Ad**. They have ALREADY given name/phone/email on
Facebook's native form before they land here. Therefore:

- **NEVER open with a lead-capture form.** They just filled one out. Re-asking kills trust.
- The page's job is: (1) confirm they made a smart click, (2) deliver instant value,
  (3) drive ONE next action.
- Detect ad traffic via `?src=fb` UTM params and swap the hero kicker to
  "You're in the right place — here's what happens next." Organic traffic sees the
  standard page.

## The one next action, per audience

- **Refi pages (VA IRRRL, Refinance):** upload your mortgage statement — the existing
  `mortgage_statement_uploads` Supabase flow. Copy: "Your statement has the exact numbers.
  Send it over and a licensed loan officer runs the real math — usually same day."
- **Purchase pages (VA, FHA, USDA, Conventional, Jumbo):** the interactive estimator
  on-page, then "Talk to a human" — tel: link + callback request.

## Page structure (every loan page, top to bottom)

1. **Hook hero** — dark forest gradient, serif headline, one emotional promise per program
   (per-page hooks below). Kenneth's video/photo slot: `<div class="adhero-media">` with a
   placeholder poster until his per-program video exists.
2. **THE SLIDER MOMENT** — the centerpiece. An interactive estimator IN the page:
   - Refi: current-payment + current-rate sliders → big animated green number
     "Estimated monthly savings: $XXX*" that counts up as they slide, pulses when it improves.
   - Purchase: home price + down payment sliders → "Estimated monthly payment: $X,XXX*"
   - Math: standard amortization, same as tools/calculator. Rates come from ONE constant in
     `/assets/rates.js`, clearly labeled a sample rate.
   - The `*` footnote directly under the number, one line:
     "Estimate only — not a quote, offer, or approval. Subject to credit approval and
     underwriting. Your actual rate and payment will differ."

3. **"Here's how this works" — 3 numbered steps**, Brunson rhythm, short and punchy.
   Each step ends with a micro-CTA button.
4. **Objection blocks** — 3 cards knocking down that program's top fears
   ("My credit isn't perfect" / "I don't have 20% down" / "I hate paperwork").
5. **Proof** — 2 testimonials (already in repo) + trust badges.
6. **The Big Button** — full-width CTA band. Refi: "Send my statement". Purchase:
   "Let's run my real numbers". ONE button, not four.
7. **FAQ** (existing) and full compliance footer (existing, unchanged).

## Copy voice — Brunson energy, Kenneth's mouth

Direct address, short sentences, curiosity gaps — but it sounds like Kenneth Travis, not a
webinar bro. kt-voice patterns: "The math matters." "Stop guessing." "No fluff."
"Options win." Playful yes; hype no. BANNED: fake scarcity, countdown timers,
"only 3 spots left."

## Per-page hooks

- **VA:** "You earned this benefit. Most veterans never use it." Sub: "No down payment.
  No monthly mortgage insurance. That's not a promo — it's your benefit."
- **VA IRRRL:** "The refinance so streamlined the VA made it a word: IRRRL." Slider:
  current rate vs today → savings counter.
- **FHA:** "Your credit doesn't have to be perfect. That's the whole point of FHA."
- **Conventional:** "The 20% down rule is a myth. Let's talk about what's real."
- **USDA:** "Zero down — and more of East Texas qualifies than you think." Interactive:
  pick your town from a static list of known-eligible area names → "Gilmer? Likely
  eligible. Check your exact address with us." NO fake eligibility API.
- **Jumbo:** "Big loan? The bank gave you one answer. We ask thirty lenders."
- **Refinance:** "Your rate isn't a life sentence." Slider centerpiece.

## Compliance — hard lines, no exceptions

- The word "quote" NEVER appears in consumer copy. "Estimate / estimated savings" only.
- No specific rates in copy. Slider sample rate labeled "sample rate for illustration —
  your rate will differ."
- Every on-screen number carries the one-line estimate footnote.
- Footer unchanged on every page: not-a-commitment-to-lend, EHO, NMLS 2426021 +
  KT 233918, five states (TX, AL, LA, ND, MI-pending).
- Post-build grep must return ZERO hits:
  "guaranteed|lowest rate|best rate|instant quote|pre-approved instantly"
- VA/IRRRL pages keep the 36-month recoupment + net tangible benefit mention.

## Build mechanics

- Extend `sitegen.py` — pages stay generated, never hand-forked. Add a `funnel` dict per loan.
- Slider JS: one shared `/assets/funnel.js`, vanilla, no deps, graceful no-JS fallback
  to a static CTA.
- Analytics: write `analytics_events` rows (Supabase) on slider interaction and CTA click —
  `funnel_slide`, `funnel_cta`. Meta Pixel: do NOT fire `Lead` here (they already converted
  on Facebook) — fire `ViewContent` + custom `EstimatorUsed`.
- Verify every internal link before calling it done. Mobile first — this traffic is ~90% phones.
