#!/usr/bin/env python3
"""Generates the tools hub and the three consumer tools.

  /tools            hub
  /tools/estimate   Estimated Savings — the primary CTA across the whole site
  /tools/calculator mortgage calculator, ungated
  /tools/home-value home value report request

Run: python3 build-tools.py   (or python3 build.py to run everything)

NAMING RULE, enforced on every consumer surface here: this is never a "quote".
Only a licensed loan officer can quote, after a complete application. Internally
the team says "soft quote"; consumers see "Estimated Savings".
"""
import os

import sitegen as S
from sitegen import TCPA_TEXT, ARROW

A = S.APPLY


def write(path, html_out):
    rel = path.strip("/") + "/index.html"
    os.makedirs(os.path.dirname(rel), exist_ok=True)
    with open(rel, "w") as f:
        f.write(html_out)
    print(f"  {rel}  ({len(html_out):,} bytes)")


# ==========================================================================
# TOOLS HUB
# ==========================================================================

def hub():
    body = f"""{S.hero(
        eyebrow="Tools",
        h1="Free tools that give you a real number",
        lede="Most lender calculators exist to capture your phone number. These exist to "
             "answer the question. Only one of them asks for anything, and it tells you so "
             "before you start.",
        trail=[("/", "Home"), (None, "Tools")])}

<section><div class="wrap">
<div class="lgrid">
  <a class="lcard" href="/tools/estimate"><h3>Estimated Savings</h3>
  <p>Six questions, about two minutes, and an estimate of what refinancing could save you.
  This is the one that asks for your name, email and phone &mdash; at the end, and we say so
  up front.</p><span class="go">See what you could save {ARROW}</span></a>

  <a class="lcard" href="/tools/calculator"><h3>Mortgage calculator</h3>
  <p>Payment breakdown, a full amortization schedule, and what an extra payment each month
  actually does to the term. Nothing gated, nothing collected.</p>
  <span class="go">Open the calculator {ARROW}</span></a>

  <a class="lcard" href="/tools/home-value"><h3>Home value report</h3>
  <p>A local estimate on your address, put together by someone who works this market rather
  than a national algorithm that has never driven down Judson Road.</p>
  <span class="go">Request a report {ARROW}</span></a>
</div>

<div class="split" style="margin-top:64px">
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Why they are free</p>
  <h2>Because the alternative is a phone call you did not want.</h2>
  <p class="sub">Every competitor makes you call and wait days to find anything out. That is
  not a business model, it is a hostage situation. Here it takes two minutes and you keep the
  number whether or not you ever speak to us.</p>
</div>
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>What we do with it</p>
  <ul class="ticks">
    <li>Nothing is sold. Ever, to anyone.</li>
    <li>The calculator collects nothing at all &mdash; it runs entirely in your browser.</li>
    <li>Where we do ask for a phone number, calling or texting you is a separate, un-ticked
    box, and ticking it is never a condition of getting a loan.</li>
    <li>One follow-up within a business day. Not six calls in an hour.</li>
  </ul>
</div>
</div>
</div></section>

<section class="alt"><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Coming for partners</p>
<h2>Tools for the professionals we work with.</h2>
<p class="sub">Buyer affordability, seller net proceeds, and rent versus buy &mdash; built for
realtors, title companies and financial planners to use with their own clients. Not built
yet; on the list.</p>
<div class="cta"><a class="btn ghost" href="/contact">Tell us what would actually help</a></div>
</div></section>

<section class="alt"><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Know your program already?</p>
<h2>Every loan page has its own live estimator.</h2>
<div class="progstrip">
  <a href="/loans/va">VA</a>
  <a href="/loans/va-irrrl">VA IRRRL</a>
  <a href="/loans/fha">FHA</a>
  <a href="/loans/conventional">Conventional</a>
  <a href="/loans/usda">USDA</a>
  <a href="/loans/jumbo">Jumbo</a>
  <a href="/loans/refinance">Refinance</a>
</div>
</div></section>

{S.cta_band()}
"""
    return S.page(
        path="/tools",
        title="Mortgage Tools & Calculators | Greenlight Mortgage — Longview, TX",
        desc="Free mortgage tools from Greenlight Mortgage in Longview, Texas — Estimated "
             "Savings, a full mortgage calculator, and a local home value report. Powered by "
             "Co/LAB Lending. Equal Housing Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/tools", "Tools")],
    )


# ==========================================================================
# ESTIMATED SAVINGS
# ==========================================================================

def estimate():
    faqs = [
        ("Is this a quote?",
         "No. It is an estimate produced from the figures you type in, and it is not an offer "
         "of credit, an approval, or a commitment to lend. Only a licensed loan officer can "
         "quote you a rate, and only after a complete application."),
        ("Will this affect my credit?",
         "No. Nothing here runs a credit check of any kind. A hard credit pull only happens "
         "later, with your permission, if you decide to apply."),
        ("What do you do with my phone number?",
         "A licensed loan officer follows up once, within one business day. We only call or "
         "text using an autodialer if you tick the separate consent box, that box is never "
         "pre-ticked, and ticking it is not a condition of getting a loan. Reply STOP to any "
         "text and we stop."),
        ("Why do you ask for anything at all?",
         "Because the estimate is worth something and we would rather be straight about the "
         "trade than pretend otherwise. Three fields, asked at the end, disclosed before you "
         "start. The calculator asks for nothing if you would rather use that."),
        ("The rate reductions shown — are those your rates?",
         "No, and that matters. They are illustrative scenarios so you can see the shape of "
         "the math on your own balance. What is actually available to you depends on your "
         "credit, income, property and the market that day."),
    ]
    faq_html = "".join(
        f'<details><summary>{S.esc(q)}</summary><div class="a"><p>{S.esc(a)}</p></div></details>'
        for q, a in faqs)

    body = f"""{S.hero(
        eyebrow="Estimated Savings",
        h1="See what you could save",
        lede="Six questions, about two minutes, and a real number at the end. No hard credit "
             "pull, and no phone call needed to see the result.",
        trail=[("/", "Home"), ("/tools", "Tools"), (None, "Estimated Savings")])}

<section><div class="wrap"><div class="narrow">

<div id="estimator">
  <div class="estcard">
    <h2>Loading the estimator&hellip;</h2>
    <p class="sub">If nothing appears in a moment, JavaScript may be switched off. Call us on
    <a href="tel:{S.PHONE_HREF}" style="color:var(--g);font-weight:650">{S.PHONE}</a> and we
    will run exactly the same numbers with you over the phone &mdash; it takes about the same
    two minutes.</p>
  </div>
</div>

<noscript>
  <div class="callout"><h3>This tool needs JavaScript</h3>
  <p>Call <a href="tel:{S.PHONE_HREF}">{S.PHONE}</a> and a licensed loan officer will work
  through the same questions with you. Nothing is lost by doing it that way.</p></div>
</noscript>

</div></div></section>

<section class="alt"><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Before you ask</p>
<h2>Straight answers</h2>
<div class="faq">{faq_html}</div>
</div></section>

<section><div class="wrap"><div class="narrow">
<p class="disclose">Greenlight Mortgage, LLC &mdash; Company NMLS #{S.NMLS_CO}, Kenneth Travis
individual NMLS #{S.NMLS_KT}. {S.POWERED}. Equal Housing Opportunity. Estimates produced by
this tool are illustrative only, are not an offer or guarantee of any interest rate, APR,
monthly payment or loan term, and are <strong>not a commitment to lend</strong>. All loans are
subject to credit approval and underwriting.</p>
</div></div></section>
"""

    # The consent sentence and the apply URL are handed to estimate.js rather than
    # duplicated inside it, so there is exactly one copy of the TCPA wording on the
    # whole site and changing it in sitegen changes it everywhere.
    scripts = (
        '<script>\n'
        f'window.GLM_TCPA_TEXT = {S.jstr(TCPA_TEXT)};\n'
        f'window.GLM_APPLY = {S.jstr(A)};\n'
        '</script>\n'
        '<script src="/forms.js" defer></script>\n'
        '<script src="/estimate.js" defer></script>'
    )

    return S.page(
        path="/tools/estimate",
        title="Estimated Savings Calculator | Greenlight Mortgage — Longview, TX",
        desc="See what refinancing could save you in about two minutes. No hard credit pull "
             "and no phone call required to see your estimate. Greenlight Mortgage, Longview "
             "TX. Powered by Co/LAB Lending. Equal Housing Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/tools", "Tools"), ("/tools/estimate", "Estimated Savings")],
        faqs=faqs,
        scripts=scripts,
    )


# ==========================================================================
# MORTGAGE CALCULATOR — ungated, runs entirely in the browser
# ==========================================================================

def calculator():
    body = f"""{S.hero(
        eyebrow="Mortgage calculator",
        h1="Work out the payment",
        lede="Principal and interest, taxes and insurance, the full amortization schedule, and "
             "what an extra payment each month really does. Nothing is collected and nothing "
             "leaves your browser.",
        trail=[("/", "Home"), ("/tools", "Tools"), (None, "Calculator")])}

<section><div class="wrap">
<div class="split even">
<div>
  <div class="estcard">
  <h2 style="font-size:24px">Your numbers</h2>
  <form id="calc" novalidate style="margin-top:22px">
    <div class="field"><label for="c-price">Home price</label>
      <input id="c-price" type="text" inputmode="decimal" value="285,000"></div>
    <div class="frow">
      <div class="field"><label for="c-down">Down payment</label>
        <input id="c-down" type="text" inputmode="decimal" value="28,500"></div>
      <div class="field"><label for="c-term">Term (years)</label>
        <select id="c-term">
          <option>30</option><option>25</option><option>20</option>
          <option>15</option><option>10</option>
        </select></div>
    </div>
    <div class="field"><label for="c-rate">Interest rate to model (%)</label>
      <input id="c-rate" type="text" inputmode="decimal" placeholder="Enter a rate"
             aria-describedby="c-rate-help">
      <p class="help" id="c-rate-help">A figure <strong>you</strong> choose, to model against.
      We deliberately do not pre-fill this &mdash; a number sitting in that box would read as
      a rate we are offering, and only a licensed loan officer can quote you one.</p></div>
    <div class="frow">
      <div class="field"><label for="c-tax">Property tax / year</label>
        <input id="c-tax" type="text" inputmode="decimal" value="5,700"></div>
      <div class="field"><label for="c-ins">Insurance / year</label>
        <input id="c-ins" type="text" inputmode="decimal" value="2,400"></div>
    </div>
    <div class="field"><label for="c-extra">Extra principal each month</label>
      <input id="c-extra" type="text" inputmode="decimal" value="0"></div>
  </form>
  </div>
</div>

<div>
  <div class="result">
    <p class="cap">Estimated monthly payment</p>
    <p class="big" id="c-total">&mdash;</p>
    <p class="cap" id="c-breakdown">principal &amp; interest, taxes and insurance</p>
    <p class="rnote">An illustration built from figures you entered. Not a quote, an offer of
    credit, or an approval, and <strong>not a commitment to lend</strong>. Subject to credit
    approval and underwriting. Excludes mortgage insurance, HOA dues, and any escrow shortage
    &mdash; all of which move the real number.</p>
  </div>

  <div class="estcard" style="margin-top:18px">
    <h2 style="font-size:22px">With the extra payment</h2>
    <p class="sub" id="c-extra-out">Add an amount above to see the effect.</p>
  </div>
</div>
</div>

<div style="margin-top:48px">
  <h2>Amortization</h2>
  <p class="sub">Year by year, where the money actually goes. In the early years most of it is
  interest &mdash; that is the part people find surprising.</p>
  <div class="tablewrap"><table id="c-amort">
    <thead><tr><th>Year</th><th>Interest paid</th><th>Principal paid</th>
    <th>Balance remaining</th></tr></thead><tbody></tbody></table></div>
  <p class="disclose">Estimates only. Subject to credit approval and underwriting.</p>
</div>
</div></section>

{S.funnel_yes("calculator", "purchase", facts=False, goal="purchase",
    h2="Want this run against your real file?",
    sub="Thirty seconds. A licensed loan officer prices your actual situation &mdash; and tells you plainly if the answer is wait.")}
"""
    return S.page(
        path="/tools/calculator",
        title="Mortgage Calculator | Greenlight Mortgage — Longview, TX",
        desc="Free mortgage calculator with full amortization schedule and extra-payment "
             "scenarios. Nothing collected, nothing gated. Greenlight Mortgage, Longview TX. "
             "Equal Housing Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/tools", "Tools"), ("/tools/calculator", "Calculator")],
        scripts='<script src="/calculator.js" defer></script>' + S.FUNNEL_SCRIPTS,
    )


# ==========================================================================
# HOME VALUE
# ==========================================================================

def home_value():
    body = f"""{S.hero(
        eyebrow="Home value report",
        h1="What is your house actually worth?",
        lede="Not an algorithm's guess from a satellite photo. A local estimate put together "
             "by someone who works this market and knows which Longview streets appraise "
             "differently from the ones next to them.",
        trail=[("/", "Home"), ("/tools", "Tools"), (None, "Home value")])}

<section><div class="wrap">
<div class="split">
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Request a report</p>
  <h2>Tell us the address.</h2>
  <p class="sub">We will put a report together and email it to you, usually within one
  business day.</p>

  <form data-glm-form="home-value" style="margin-top:28px" novalidate>
    <div class="field"><label for="h-address">Property address</label>
      <input id="h-address" name="address" type="text" autocomplete="street-address"
             required maxlength="200" placeholder="123 Example St, Longview, TX 75605">
      <p class="err">Please enter the address you would like valued.</p></div>
    <div class="frow">
      <div class="field"><label for="h-name">Your name</label>
        <input id="h-name" name="name" type="text" autocomplete="name" required maxlength="120">
        <p class="err">Please tell us your name.</p></div>
      <div class="field"><label for="h-email">Email</label>
        <input id="h-email" name="email" type="email" autocomplete="email" required maxlength="254">
        <p class="err">Please enter a valid email address.</p></div>
    </div>
    <div class="frow">
      <div class="field"><label for="h-phone">Phone <span
        style="font-weight:450;color:var(--mut)">(optional)</span></label>
        <input id="h-phone" name="phone" type="tel" autocomplete="tel" maxlength="32"></div>
      <div class="field"><label for="h-plan">What are you thinking?</label>
        <select id="h-plan" name="goal">
          <option value="">Choose one…</option>
          <option>Thinking about selling</option>
          <option>Thinking about refinancing</option>
          <option>Removing mortgage insurance</option>
          <option>Just curious</option>
        </select></div>
    </div>

    <div class="consent">
      <input type="checkbox" id="h-tcpa" name="tcpa_consent" value="yes">
      <label for="h-tcpa">{TCPA_TEXT}</label>
    </div>
    <p class="disclose">Leave that unticked and we will email the report without calling you.
    You will still get it.</p>

    <div class="cta"><button class="btn go" type="submit">Send me the report</button></div>
    <p class="formstatus" role="status" aria-live="polite"></p>
  </form>
</div>

<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>What you get</p>
  <ul class="ticks">
    <li>An estimated value range for your address, not a single false-precision number</li>
    <li>Recent comparable sales nearby, with what makes them comparable</li>
    <li>What the equity position means for refinancing or dropping mortgage insurance</li>
    <li>A plain answer on whether now is a sensible time to do anything at all</li>
  </ul>

  <div class="callout">
    <h3>This is not an appraisal</h3>
    <p>An appraisal is a formal opinion of value by a licensed appraiser, ordered as part of a
    loan, and it is the only one a lender will act on. This report is an informal estimate to
    help you think. The two are not interchangeable and we will not pretend otherwise.</p>
  </div>

  <p class="disclose">Estimates only, and not a commitment to lend. Property values change and
  any figure we give you is an opinion, not a guarantee of what a buyer or an appraiser will
  conclude. Subject to credit approval and underwriting where a loan is involved.</p>
</div>
</div>
</div></section>

{S.cta_band(head="Already know the equity is there?",
            sub="Run the savings estimate and see what a refinance would actually do to the "
                "payment.")}
"""
    return S.page(
        path="/tools/home-value",
        title="Home Value Report | Greenlight Mortgage — Longview, TX",
        desc="Request a local home value estimate for your Longview or East Texas property "
             "from Greenlight Mortgage. Powered by Co/LAB Lending. Equal Housing Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/tools", "Tools"), ("/tools/home-value", "Home value")],
        scripts='<script src="/forms.js" defer></script>',
    )


def build():
    print("tools")
    write("/tools", hub())
    write("/tools/estimate", estimate())
    write("/tools/calculator", calculator())
    write("/tools/home-value", home_value())


if __name__ == "__main__":
    build()
