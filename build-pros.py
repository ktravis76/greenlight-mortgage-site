#!/usr/bin/env python3
"""Partner tools — the B2B side of the funnel.

  /pros                     hub for realtors, title, inspectors, roofers, insurance
  /tools/affordability      what can my buyer afford
  /tools/net-proceeds       seller net sheet
  /tools/rent-vs-buy        rent versus buy

THE LOOP THIS SERVES
A realtor shares a co-branded link with their client. The client runs the
numbers on our page and the inquiry reaches Greenlight attributed to the
realtor. Everybody gets something: the client gets an answer, the realtor looks
useful without doing any work, and we get a warm lead from someone who already
trusts the person who sent them.

Two rules make it actually work rather than just exist:

1. NOTHING IS GATED. A realtor will not put a lead-harvesting form in front of
   their own client, and they are right not to. These run in the browser and
   collect nothing unless somebody chooses to ask us a question at the end.
2. THE CO-BRAND SAYS "SHARED WITH YOU BY", NOT "BROUGHT TO YOU BY". They are
   passing on a tool, not endorsing a lender, and we do not get to imply an
   endorsement on their behalf.

Each tool is also its own indexable page targeting local search intent, which
is the other half of KT's brief: people who never met a realtor should be able
to find these on Google.
"""
import os

import sitegen as S

ARROW = S.ARROW
A = S.APPLY


def write(path, html_out):
    rel = path.strip("/") + "/index.html"
    os.makedirs(os.path.dirname(rel), exist_ok=True)
    with open(rel, "w") as f:
        f.write(html_out)
    print(f"  {rel}  ({len(html_out):,} bytes)")


def fld(id_, label, value="", help_="", prefix="", suffix="", placeholder=""):
    p = f'<span class="affix">{prefix}</span>' if prefix else ""
    sfx = f'<span class="affix right">{suffix}</span>' if suffix else ""
    h = f'<p class="help">{help_}</p>' if help_ else ""
    v = f' value="{value}"' if value != "" else ""
    ph = f' placeholder="{placeholder}"' if placeholder else ""
    return (f'<div class="field pf"><label for="{id_}">{label}</label>{h}'
            f'<div class="pfin">{p}<input id="{id_}" type="text" inputmode="decimal"'
            f'{v}{ph}>{sfx}</div></div>')


def sel(id_, label, options, help_=""):
    opts = "".join(f"<option>{o}</option>" for o in options)
    h = f'<p class="help">{help_}</p>' if help_ else ""
    return (f'<div class="field pf"><label for="{id_}">{label}</label>{h}'
            f'<select id="{id_}">{opts}</select></div>')


RATE_HELP = ("A figure <strong>you</strong> choose, to model against. We do not pre-fill "
             "one &mdash; a number sitting in that box would read as a rate we are "
             "offering, and only a licensed loan officer can quote you one.")

PRO_CTA = """
<section class="alt"><div class="wrap"><div class="narrow" style="text-align:center">
<p class="eyebrow" style="justify-content:center"><span class="tick" aria-hidden="true"></span>For professionals</p>
<h2 style="margin-inline:auto">Share this with your clients.</h2>
<p class="sub" style="margin-inline:auto">Put your name on it and send it to anyone. Free,
nothing gated, and any inquiry that comes back is tagged to you.</p>
<div class="cta" style="justify-content:center">
<a class="btn go" href="/pros">Make your link {arrow}</a></div>
</div></div></section>
""".replace("{arrow}", ARROW)


# ==========================================================================
# /pros
# ==========================================================================

def pros():
    tools = [
        ("/tools/affordability", "Buyer affordability",
         "What price range does this buyer actually sit in? Income, debts and a rate they "
         "choose, in and out in thirty seconds.", "Realtors"),
        ("/tools/net-proceeds", "Seller net proceeds",
         "What the seller walks away with after payoff, commission and closing costs. The "
         "listing-appointment number.", "Realtors"),
        ("/tools/rent-vs-buy", "Rent vs buy",
         "The honest version, including the years where renting genuinely wins.", "Everyone"),
        ("/tools/calculator", "Mortgage calculator",
         "Payment, full amortization, and what an extra payment a month really does.",
         "Everyone"),
        ("/tools/estimate", "Estimated Savings",
         "For a client already in a loan and wondering. This is the one that asks for "
         "contact details &mdash; disclosed before they start.", "Refinance"),
        ("/archive", "The Longview archive",
         f"{140} local professionals across 20 trades. You are probably already in it.",
         "Everyone"),
    ]
    cards = "".join(
        f'<a class="lcard" href="{h}" style="--accent:#0f7a4d">'
        f'<span class="who">{tag}</span><h3>{t}</h3><p>{d}</p>'
        f'<span class="go">Open {ARROW}</span></a>'
        for h, t, d, tag in tools)

    body = f"""{S.hero(
        eyebrow="For professionals",
        h1="Tools you can put in front of your own clients",
        lede="Free, nothing gated, and none of them harvest the people you send. Put your "
             "name on a link and share it &mdash; you look useful, your client gets a real "
             "answer, and if they need a lender we are already in the conversation.",
        ctas=[("#builder", "Make your link", "go"), ("/archive", "See the archive", "ghost")],
        trail=[("/", "Home"), (None, "For professionals")])}

<section><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>The tools</p>
<h2>Six things you can send today.</h2>
<div class="lgrid">{cards}</div>
</div></section>

<section class="dark" id="builder"><div class="wrap"><div class="narrow">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Your share link</p>
<h2>Put your name on it.</h2>
<p class="sub">Type your details, pick a tool, copy the link. Anyone who opens it sees your
name at the top, and anything that comes back to us is tagged to you.</p>

<form id="linkbuilder" novalidate style="margin-top:28px">
  <div class="frow">
    <div class="field"><label for="lb-name">Your name</label>
      <input id="lb-name" type="text" maxlength="80" placeholder="Jane Doe"></div>
    <div class="field"><label for="lb-co">Company</label>
      <input id="lb-co" type="text" maxlength="80" placeholder="Acme Realty"></div>
  </div>
  <div class="field"><label for="lb-tool">Tool</label>
    <select id="lb-tool">
      <option value="/tools/affordability">Buyer affordability</option>
      <option value="/tools/net-proceeds">Seller net proceeds</option>
      <option value="/tools/rent-vs-buy">Rent vs buy</option>
      <option value="/tools/calculator">Mortgage calculator</option>
      <option value="/tools/estimate">Estimated Savings</option>
      <option value="/">Our homepage</option>
    </select></div>
  <div class="field"><label for="lb-out">Your link</label>
    <input id="lb-out" type="text" readonly onclick="this.select()"></div>
  <div class="cta"><button class="btn go" type="button" id="lb-copy">Copy link</button></div>
  <p class="formstatus" role="status" aria-live="polite"></p>
</form>
</div></div></section>

<section><div class="wrap">
<div class="split">
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Why we do this</p>
  <h2>Because brochures do not get shared.</h2>
  <p class="sub">Most lenders give realtors a flyer with their face on it. Nobody has ever
  forwarded one of those to a client. A working affordability calculator gets forwarded,
  because it answers the question the client actually asked.</p>
  <p class="sub">We would rather be the lender whose tools you use than the one whose
  brochure is in your drawer.</p>
</div>
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>What we will not do</p>
  <ul class="ticks">
    <li>Gate your client behind a form to see a number</li>
    <li>Sell, rent, or share their details with anyone</li>
    <li>Call somebody who did not ask us to</li>
    <li>Put your name on anything implying you endorse us &mdash; the banner says
    &ldquo;shared with you by&rdquo;, and that is all it says</li>
  </ul>
  <div class="callout">
    <h3>Want one built for your trade?</h3>
    <p>Title timelines, inspection findings that affect financing, renovation financing
    paths for contractors. Tell us what you get asked and we will build it.</p>
  </div>
</div>
</div>
</div></section>

{S.cta_band(head="Working on a file right now?",
            sub="Call the office and talk it through with a licensed loan officer. No form "
                "in the middle.",
            primary=("/contact", "Get in touch"),
            secondary=("/archive", "Browse the archive"))}
"""
    return S.page(
        path="/pros",
        title="Tools for Realtors & Real Estate Professionals | Greenlight Mortgage — Longview, TX",
        desc="Free, shareable mortgage tools for Longview and East Texas realtors, title "
             "companies and inspectors — buyer affordability, seller net proceeds, rent vs "
             "buy. Co-brand them with your name. Powered by Co/LAB Lending. Equal Housing "
             "Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/pros", "For professionals")],
        scripts='<script src="/linkbuilder.js" defer></script>',
    )


# ==========================================================================
# Tool pages
# ==========================================================================

def affordability():
    faqs = [
        ("Is this a pre-approval?",
         "No. It is an estimate from figures you typed in, and it is not an offer of credit "
         "or a commitment to lend. A pre-approval means a licensed loan officer has looked "
         "at your credit, income and assets. This is the conversation before that one."),
        ("Why a range instead of one number?",
         "Because a single number invites people to treat it as an approval. The lower end "
         "uses conservative debt-to-income guidance and the upper end uses the more "
         "stretching limits some programs allow. Where you actually land depends on your "
         "credit, the program and the property."),
        ("What counts as monthly debts?",
         "Car payments, student loans, credit card minimums, child support — the recurring "
         "obligations that show on a credit report. Not groceries, utilities or petrol."),
        ("Does this affect my credit?",
         "No. Nothing on this page contacts a credit bureau, and nothing you type leaves "
         "your browser."),
    ]
    faq_html = "".join(
        f'<details><summary>{S.esc(q)}</summary><div class="a"><p>{S.esc(a)}</p></div></details>'
        for q, a in faqs)

    body = f"""{S.hero(
        eyebrow="Buyer affordability",
        h1="What can you actually afford?",
        lede="Income, monthly debts, and a rate you pick. It gives you a price range in "
             "about thirty seconds &mdash; no credit inquiry, nothing collected, nothing to "
             "fill in at the end.",
        trail=[("/", "Home"), ("/pros", "For professionals"), (None, "Affordability")])}

<section><div class="wrap">
<div class="split even">
<div><div class="estcard">
  <h2 style="font-size:23px">Your numbers</h2>
  <form id="afford" novalidate style="margin-top:20px">
    {fld("af-income", "Gross monthly income", prefix="$", placeholder="7,500",
         help_="Before tax. Include a co-borrower if you are buying together.")}
    {fld("af-debts", "Other monthly debt payments", value="0", prefix="$",
         help_="Car, student loans, credit card minimums, child support.")}
    {fld("af-rate", "Interest rate to model", suffix="%", placeholder="Enter a rate",
         help_=RATE_HELP)}
    {sel("af-term", "Term (years)", ["30", "25", "20", "15"])}
    {fld("af-down", "Down payment saved", value="0", prefix="$", placeholder="15,000")}
    {fld("af-tax", "Property tax rate", value="1.8", suffix="%",
         help_="Percent of value per year. East Texas commonly runs near this, but it "
               "varies by district &mdash; check the actual address.")}
    {fld("af-ins", "Home insurance per year", value="2400", prefix="$")}
    {fld("af-hoa", "HOA per month", value="0", prefix="$")}
  </form>
</div></div>
<div>
  <div class="result" id="af-out"><p class="cap">Enter your income and a rate to begin.</p></div>
  <div class="estcard" style="margin-top:18px">
    <h2 style="font-size:21px">How it got there</h2>
    <div id="af-detail"></div>
    <p class="disclose">Estimates only. Not a pre-approval and not a commitment to lend.
    Subject to credit approval and underwriting.</p>
  </div>
</div>
</div>
</div></section>

<section class="dark"><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Questions</p>
<h2>Straight answers</h2>
<div class="faq">{faq_html}</div>
</div></section>

{PRO_CTA}

{S.funnel_yes("affordability", "purchase", facts=False, goal="purchase",
    h2="Want the real version of this number?",
    sub="Thirty seconds. A licensed loan officer runs your actual numbers &mdash; credit, income, program &mdash; and calls once with real answers.")}
"""
    return S.page(
        path="/tools/affordability",
        title="Home Affordability Calculator | Longview, TX — Greenlight Mortgage",
        desc="Work out what price home you can afford in Longview and East Texas. Free, "
             "nothing collected, and no credit inquiry of any kind. Greenlight Mortgage. "
             "Equal Housing Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/pros", "For professionals"),
               ("/tools/affordability", "Affordability")],
        faqs=faqs,
        scripts='<script src="/protools.js" defer></script>' + S.FUNNEL_SCRIPTS,
    )


def net_proceeds():
    body = f"""{S.hero(
        eyebrow="Seller net proceeds",
        h1="What you walk away with",
        lede="Sale price, less what you owe, less what it costs to sell. The number sellers "
             "actually want at a listing appointment &mdash; and the one they rarely get "
             "before they have signed something.",
        trail=[("/", "Home"), ("/pros", "For professionals"), (None, "Net proceeds")])}

<section><div class="wrap">
<div class="split even">
<div><div class="estcard">
  <h2 style="font-size:23px">The sale</h2>
  <form id="netsheet" novalidate style="margin-top:20px">
    {fld("np-price", "Expected sale price", prefix="$", placeholder="285,000")}
    {fld("np-payoff", "Mortgage payoff", value="0", prefix="$",
         help_="What you still owe. Your servicer can give you an exact payoff quote.")}
    {fld("np-commission", "Total agent commission", value="6", suffix="%",
         help_="Commission is negotiable and always has been. Put in whatever you have "
               "actually agreed.")}
    {fld("np-closing", "Seller closing costs", value="1.5", suffix="%",
         help_="Title policy, escrow, recording, prorated taxes. A rough allowance.")}
    {fld("np-repairs", "Repairs or credits", value="0", prefix="$")}
    {fld("np-concessions", "Buyer concessions", value="0", prefix="$")}
    {fld("np-other", "Anything else", value="0", prefix="$",
         help_="Home warranty, HOA transfer, survey.")}
  </form>
</div></div>
<div>
  <div class="result" id="np-out"><p class="cap">Enter a sale price to see an estimate.</p></div>
  <div class="estcard" style="margin-top:18px">
    <h2 style="font-size:21px">Line by line</h2>
    <div id="np-detail"></div>
    <p class="disclose">Estimates only. The settlement statement from your title company is
    the figure that counts. We are not attorneys or tax advisers.</p>
  </div>
</div>
</div>
</div></section>

<section class="alt"><div class="wrap">
<div class="split">
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Selling and buying at once</p>
  <h2>The equity is usually the down payment.</h2>
  <p class="sub">Most sellers in this market are buyers too, and the proceeds above are what
  funds the next place. Worth running that side before you list, because it changes what you
  can offer and how strong you look to a seller.</p>
  <div class="cta"><a class="btn" href="/tools/affordability">Run the buying side {ARROW}</a></div>
</div>
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Watch for</p>
  <ul class="ticks">
    <li>Your payoff is not your balance &mdash; it includes interest to the closing date</li>
    <li>Prorated property taxes can move the number either direction</li>
    <li>An HOA transfer fee surprises people every single time</li>
    <li>Commission is negotiable, and the field above is editable for that reason</li>
  </ul>
</div>
</div>
</div></section>

{PRO_CTA}

{S.funnel_yes("net-proceeds", "purchase", facts=False, goal="sell_and_buy",
    h2="Selling, then buying? Line both up at once.",
    sub="Thirty seconds. A licensed loan officer looks at the sale and the next purchase together, and calls once with real answers.")}
"""
    return S.page(
        path="/tools/net-proceeds",
        title="Seller Net Proceeds Calculator | Longview, TX — Greenlight Mortgage",
        desc="Estimate what you will net from selling your Longview or East Texas home after "
             "payoff, commission and closing costs. Free and nothing collected. Greenlight "
             "Mortgage. Equal Housing Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/pros", "For professionals"),
               ("/tools/net-proceeds", "Net proceeds")],
        scripts='<script src="/protools.js" defer></script>' + S.FUNNEL_SCRIPTS,
    )


def rent_vs_buy():
    body = f"""{S.hero(
        eyebrow="Rent vs buy",
        h1="Is buying actually better?",
        lede="Sometimes not, and a lender saying so out loud is rare enough to be worth "
             "something. If you are moving in two years the math usually favors renting.",
        trail=[("/", "Home"), ("/pros", "For professionals"), (None, "Rent vs buy")])}

<section><div class="wrap">
<div class="split even">
<div><div class="estcard">
  <h2 style="font-size:23px">Assumptions</h2>
  <p class="sub" style="margin-top:6px">Every one of these is a guess about the future. Change
  them and watch the answer flip &mdash; that is the most useful thing this tool does.</p>
  <form id="rvb" novalidate style="margin-top:20px">
    {fld("rv-rent", "Rent per month now", prefix="$", placeholder="1,600")}
    {fld("rv-rentgrowth", "Rent rises per year", value="3", suffix="%")}
    {fld("rv-price", "Purchase price", prefix="$", placeholder="285,000")}
    {fld("rv-down", "Down payment", value="0", prefix="$")}
    {fld("rv-rate", "Interest rate to model", suffix="%", placeholder="Enter a rate",
         help_=RATE_HELP)}
    {sel("rv-years", "How long will you stay?", ["3", "5", "7", "10", "15", "20"],
         help_="The single biggest lever in the whole calculation.")}
    {fld("rv-appreciation", "Home value grows per year", value="3", suffix="%")}
    {fld("rv-tax", "Property tax rate", value="1.8", suffix="%")}
    {fld("rv-ins", "Insurance per year", value="2400", prefix="$")}
    {fld("rv-maint", "Maintenance per year", value="1", suffix="%",
         help_="Percent of value. One percent is the usual rule of thumb.")}
    {fld("rv-sellcost", "Cost to sell later", value="8", suffix="%")}
  </form>
</div></div>
<div>
  <div class="result" id="rv-out"><p class="cap">Fill in rent, price and a rate.</p></div>
  <div class="estcard" style="margin-top:18px">
    <h2 style="font-size:21px">The workings</h2>
    <div id="rv-detail"></div>
    <p class="disclose">An illustration only, not advice and not a commitment to lend.</p>
  </div>
</div>
</div>
</div></section>

<section class="dark"><div class="wrap">
<div class="split">
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>What it leaves out</p>
  <h2>Read this before you trust the number.</h2>
  <p class="sub">It ignores the tax treatment of mortgage interest, which can matter and
  depends entirely on your situation. It ignores what you might have earned investing the
  down payment instead. It assumes you stay the whole period, and that nothing breaks that
  is not covered by the maintenance figure.</p>
  <p class="sub">And it cannot price the things that actually decide it for most people:
  whether you want to paint a wall without asking, and whether you plan to still be here in
  five years.</p>
</div>
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Rules of thumb</p>
  <ul class="ticks">
    <li>Under three years, renting usually wins on cost alone</li>
    <li>Past seven, buying usually wins unless values fall</li>
    <li>In between it is close enough that the non-financial reasons decide it</li>
    <li>Anyone who tells you renting is always throwing money away is selling something</li>
  </ul>
</div>
</div>
</div></section>

{PRO_CTA}

{S.funnel_yes("rent-vs-buy", "purchase", facts=False, goal="purchase",
    h2="If buying wins, find out what you qualify for.",
    sub="Thirty seconds. No hard credit pull to start &mdash; a licensed loan officer runs your actual situation and calls once.")}
"""
    return S.page(
        path="/tools/rent-vs-buy",
        title="Rent vs Buy Calculator | Longview, TX — Greenlight Mortgage",
        desc="Compare renting against buying in Longview and East Texas over the years you "
             "plan to stay. Free, nothing collected, and honest about when renting wins. "
             "Greenlight Mortgage. Equal Housing Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/pros", "For professionals"),
               ("/tools/rent-vs-buy", "Rent vs buy")],
        scripts='<script src="/protools.js" defer></script>' + S.FUNNEL_SCRIPTS,
    )


def build():
    print("partner tools")
    write("/pros", pros())
    write("/tools/affordability", affordability())
    write("/tools/net-proceeds", net_proceeds())
    write("/tools/rent-vs-buy", rent_vs_buy())


if __name__ == "__main__":
    build()
