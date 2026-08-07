/* Greenlight Mortgage — the ONE place a sample rate lives.

   Every estimator on the funnel pages reads this file and nowhere else.
   Change the figure here, rebuild nothing — every slider updates.

   ⚠️ COMPLIANCE. This is a SAMPLE RATE FOR ILLUSTRATION, not an offer, not a
   quote, and not today's pricing. It must always be labeled as a sample
   wherever it renders, and no consumer-facing copy may state it as "our rate".
   Only a licensed loan officer can price a loan, after a complete application.

   Loaded as a plain script (this site ships zero modules); exported both as a
   const for anything that inlines it and on window for funnel.js. */

const GLM_SAMPLE_RATES = {
  // One sample figure, used by every funnel estimator, purchase and refi alike.
  SAMPLE_RATE: 6.5,          // % — sample rate for illustration only
  SAMPLE_TERM_YEARS: 30,     // modeled term for purchase estimates

  // Refi estimator: when the visitor does not know their balance, it is
  // inferred from their payment and rate assuming this many years remain.
  ASSUMED_YEARS_LEFT: 27,

  // Sample closing-cost allowance for the 36-month recoupment meter (title,
  // recording, lender fees). The VA funding fee (0.5% of balance, waived at a
  // 10%+ service-connected disability rating) is added on top where relevant.
  // A sample for illustration — real costs come from a real loan estimate.
  ASSUMED_REFI_COSTS: 3000,

  // The label that must appear beside the figure anywhere it is visible.
  LABEL: 'sample figure for illustration only — not today’s pricing, not an offer, and your actual rate will differ',
};

window.GLM_SAMPLE_RATES = GLM_SAMPLE_RATES;
