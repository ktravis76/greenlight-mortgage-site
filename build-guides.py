#!/usr/bin/env python3
"""Pages the Notion build plan called for that did not exist yet.

  /loans/va-irrrl   VA streamline refinance + the recoupment screener
  /why-a-broker     the bank-vs-broker argument, its own page
  /learn/<slug>     six Learning Center articles

Sources: "Greenlight Mortgage Website — Build Plan" and "Greenlight Platform —
Architecture & Phasing" in Notion, plus the 27 Jul VA refinance build session,
which is where the two levers on the IRRRL page came from — the disability
rating waiving the funding fee, and the escrow refund nobody explains.
"""
import os

import sitegen as S

ARROW = S.ARROW


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


def faq_block(faqs):
    return "".join(
        f'<details><summary>{S.esc(q)}</summary><div class="a"><p>{S.esc(a)}</p></div></details>'
        for q, a in faqs)


# ==========================================================================
# VA IRRRL
# ==========================================================================

def va_irrrl():
    """Now a funnel page — the flagship Facebook lead-ad destination. Structure
    and copy come from S.FUNNEL['va-irrrl']; the FAQs below carry the detailed
    education (recoupment, escrow refund, the disability-rating waiver). The
    deep-dive screener this page used to embed lives on at
    /tools/va-refi-screener for staff use."""
    faqs = [
        ("What is an IRRRL?",
         "The VA Interest Rate Reduction Refinance Loan — a streamline refinance for veterans "
         "already holding a VA loan. Less documentation than a full refinance, and in most "
         "cases no new appraisal and no new certificate of eligibility."),
        ("Does my disability rating really matter that much?",
         "Yes, and it is the single most overlooked thing in a VA refinance. A "
         "service-connected rating of 10% or higher waives the VA funding fee completely. On "
         "a $250,000 balance that is around $1,250 of cost gone, and it regularly turns a "
         "marginal file into one that clearly works."),
        ("Why does my new loan amount go up?",
         "Because the new loan funds a new escrow account for taxes and insurance, and the "
         "closing costs are usually financed in. Your current servicer then refunds the "
         "escrow balance you have already built, normally within about 30 days of closing. "
         "It largely washes out — but nobody explains it, so people assume they are simply "
         "borrowing more."),
        ("What is the 36-month rule?",
         "VA requires the cost of the refinance to be recovered by the monthly saving within "
         "36 months. It is a real requirement, not a guideline. If a file does not recoup in "
         "time, the loan cannot be written that way — and the screener above will tell you "
         "so rather than pretending otherwise."),
        ("Do I need a new appraisal?",
         "Usually not on an IRRRL. That is a large part of why it is quicker and cheaper "
         "than a standard refinance."),
        ("Can I take cash out with an IRRRL?",
         "No. An IRRRL is a rate-and-term streamline. Taking equity out means a VA cash-out "
         "refinance, which is a different loan with a full appraisal and full underwriting."),
    ]

    return S.page(
        path="/loans/va-irrrl",
        title="VA IRRRL Streamline Refinance | Longview, TX — Greenlight Mortgage",
        desc="VA IRRRL streamline refinance for East Texas veterans. See what a streamline "
             "could change monthly, what a 10% disability rating does to the funding fee, "
             "and the 36-month test every file must pass. Greenlight Mortgage, Longview. "
             "Equal Housing Opportunity.",
        body=S.funnel_body("va-irrrl", faqs),
        trail=[("/", "Home"), ("/loans", "Loan options"), ("/loans/va-irrrl", "VA IRRRL")],
        faqs=faqs,
        scripts=S.FUNNEL_SCRIPTS,
    )


# ==========================================================================
# WHY A BROKER
# ==========================================================================

def why_broker():
    faqs = [
        ("Does using a broker cost me more?",
         "No. Brokers are compensated as part of the transaction in the same way a bank's "
         "retail channel is, and broker pricing is frequently better because wholesale "
         "lenders compete for the file. Your loan estimate shows every cost in writing, and "
         "you should compare it against anyone else's."),
        ("Is my loan sold afterwards either way?",
         "Almost certainly. Most mortgages get sold on the secondary market regardless of who "
         "originated them, including loans from big-name banks. Where you got it does not "
         "determine who ends up servicing it."),
        ("Why would a bank say no when a broker says yes?",
         "Because the bank has one set of guidelines and a broker has many. Self-employed "
         "income, a thin credit file, a rural address, a jumbo amount — one lender declines "
         "it and another writes it every week."),
        ("What is the catch?",
         "A broker cannot help if the right answer is a portfolio product only your own bank "
         "offers, and we will tell you when that is the case. We also cannot make an "
         "underwriter say yes."),
    ]

    body = f"""{S.hero(
        eyebrow="Why a broker",
        h1="One bank has one menu. We have a network.",
        lede="This is the whole argument, and it takes about two minutes to understand. Once "
             "you do, it is difficult to go back to asking one institution for one answer.",
        ctas=[("/tools/estimate", "See what you could save", "go"),
              ("/loans", "Browse loan options", "ghost")],
        trail=[("/", "Home"), (None, "Why a broker")])}

<section><div class="wrap">
<div class="split">
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>The difference</p>
  <h2>A loan officer at a bank works for the bank.</h2>
  <p class="sub">That is not a criticism, it is a job description. They can offer you that
  bank's programs at that bank's pricing under that bank's guidelines. If your file does not
  fit, the answer is no, and the conversation ends there.</p>
  <p class="sub">A brokerage takes the same file to a network of wholesale lenders. Different
  guidelines, different pricing, different appetites. We are free to recommend whichever one
  actually serves you, because we are not paid to steer you toward one.</p>
  <p class="sub">The difference shows up most on the files banks find awkward: self-employed
  income, credit that is recovering, a rural address, a jumbo amount, a VA benefit nobody
  explained properly.</p>
</div>
<div>
  <div class="estcard">
    <h3 style="font-size:20px">Same borrower, two routes</h3>
    <div class="tablewrap" style="margin-top:16px"><table><tbody>
      <tr><th>At a bank</th><td>One set of guidelines</td></tr>
      <tr><th></th><td>One pricing sheet</td></tr>
      <tr><th></th><td>One answer, and it is final</td></tr>
      <tr><th>Through a broker</th><td>A network of lenders</td></tr>
      <tr><th></th><td>Competing pricing on your file</td></tr>
      <tr><th></th><td>Options side by side, and you choose</td></tr>
    </tbody></table></div>
    <p class="disclose">Availability and pricing depend on your credit, income, the property
    and current market conditions. Not a commitment to lend.</p>
  </div>
</div>
</div>
</div></section>

<section class="dark"><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>What it means in practice</p>
<h2>Four things that change.</h2>
<div class="grid g2">
  <div class="card"><span class="num">01</span><h3>You get told no less often</h3>
  <p>A decline at one lender is a data point, not a verdict. We already know which lenders
  are comfortable with which files.</p></div>
  <div class="card"><span class="num">02</span><h3>Pricing is competed for</h3>
  <p>Wholesale lenders want the file. That competition happens on your behalf and you never
  have to run it yourself.</p></div>
  <div class="card"><span class="num">03</span><h3>We can say do nothing</h3>
  <p>If refinancing will not pay for itself before you move, we lose the deal by telling you.
  We would still rather tell you.</p></div>
  <div class="card"><span class="num">04</span><h3>One file, not five applications</h3>
  <p>You do not shop lenders yourself, and you do not collect five hard credit pulls doing
  it.</p></div>
</div>
</div></section>

<section><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Fair questions</p>
<h2>Including the skeptical ones</h2>
<div class="faq">{faq_block(faqs)}</div>
</div></section>

{S.cta_band()}
"""
    return S.page(
        path="/why-a-broker",
        title="Why Use a Mortgage Broker Instead of a Bank? | Longview, TX",
        desc="A bank offers one set of guidelines and one price. A mortgage broker shops a "
             "network of lenders on your file. What that actually means for Longview and "
             "East Texas borrowers. Greenlight Mortgage. Equal Housing Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/why-a-broker", "Why a broker")],
        faqs=faqs,
    )


# ==========================================================================
# LEARNING CENTER ARTICLES
# ==========================================================================
# Original explainers written for this site. Each is general education, hedged
# where it needs to be, with no rate, figure, or approval claim specific to
# Greenlight. KT should still read them before launch — they are our words.

ARTICLES = [
    dict(slug="what-underwriting-looks-at", icon="shield",
         title="What underwriting actually looks at",
         blurb="Income, assets, credit, and the property. Knowing the four buckets makes the "
               "document requests stop feeling random.",
         sections=[
             ("The four buckets", [
                 "Every mortgage decision comes down to four questions, and every document "
                 "you are asked for belongs to one of them. Can you repay it? Do you have the "
                 "funds to close? How have you handled credit before? And is the property "
                 "worth what you are borrowing against it?",
                 "The requests feel random because nobody tells you which bucket each one "
                 "is filling. Once you know, the process stops feeling like an interrogation "
                 "and starts looking like a checklist.",
             ]),
             ("Income", [
                 "Underwriting wants income that is stable, documentable, and likely to "
                 "continue. A W-2 salary is the simplest case. Self-employment, commission, "
                 "bonus and rental income all count, but they are averaged over a longer "
                 "period and need more paperwork.",
                 "This is where the most files stall, and almost always over documentation "
                 "rather than the amount. If your income is complicated, say so at the "
                 "beginning rather than letting it emerge in week three.",
             ]),
             ("Assets", [
                 "You need enough for the down payment and closing costs, and lenders want to "
                 "see where it came from. A large deposit that appears from nowhere has to be "
                 "explained — not because anyone suspects you, but because the rules require "
                 "sourcing.",
                 "Gift funds are allowed on most programs with a gift letter. Move money "
                 "between accounts before you apply, not during.",
             ]),
             ("Credit", [
                 "Not just the score. Underwriting looks at payment history, how much of your "
                 "available credit you use, how long your accounts have been open, and "
                 "anything derogatory and how long ago it happened.",
                 "In the sixty days before you apply: do not open new accounts, do not close "
                 "old ones, and do not let a balance spike. Any of the three can move your "
                 "pricing.",
             ]),
             ("The property", [
                 "The house is collateral, so it gets underwritten too. An appraisal "
                 "establishes value, and condition matters — some programs have requirements "
                 "the property itself has to meet.",
                 "This is the bucket borrowers forget, and it is the one that most often "
                 "produces a late surprise.",
             ]),
         ]),

    dict(slug="the-20-percent-myth", icon="save",
         title="You probably do not need 20% down",
         blurb="Where the number came from, what it actually does, and how to work out "
               "whether waiting is costing you more than it saves.",
         sections=[
             ("Where the number came from", [
                 "Twenty percent is the threshold above which a conventional loan generally "
                 "does not require private mortgage insurance. That is the entire origin of "
                 "it. It was never a minimum to buy a house — it is the point at which one "
                 "particular cost falls away on one particular kind of loan.",
                 "Somewhere it became folk wisdom, and now people who could have bought years "
                 "ago are still saving toward a number nobody ever required of them.",
             ]),
             ("What is actually available", [
                 "Qualifying first-time buyers can see conventional programs starting far "
                 "below twenty percent. FHA is built around a lower down payment. VA, for an "
                 "eligible veteran, frequently requires nothing down and carries no monthly "
                 "mortgage insurance at all. USDA can be zero down on an eligible rural "
                 "address, and eligibility is set by specific address rather than by town.",
                 "Whether any of these is available to you depends on your credit, income, "
                 "the property and current guidelines. That is a conversation with a licensed "
                 "loan officer, not something a website can settle.",
             ]),
             ("The better question", [
                 "Not “how do I avoid mortgage insurance” but “what does "
                 "waiting cost me?” Those are different questions and people almost "
                 "always ask the first.",
                 "Waiting has three costs that rarely get counted. You keep paying rent, "
                 "building equity for someone else. You miss whatever the house appreciates "
                 "meanwhile, and in a rising market the target moves faster than most people "
                 "can save. And you are betting rates will not move against you.",
                 "Against that, mortgage insurance is a monthly cost that on a conventional "
                 "loan comes off once you have built enough equity. Sometimes the math says "
                 "wait. Frequently it says the opposite.",
             ]),
         ]),

    dict(slug="rate-versus-payment-versus-cost", icon="calc",
         title="Rate, payment and cost are three different things",
         blurb="People use them interchangeably. The cheapest rate is not always the cheapest "
               "loan, and the lowest payment is often the most expensive.",
         sections=[
             ("The rate is not the price", [
                 "A rate is what interest accrues at. The price of a loan is the rate plus "
                 "everything you paid to get it — points, lender fees, and anything financed "
                 "into the balance. Two loans at the same rate can cost thousands apart.",
                 "This is why the advertised rate is close to meaningless on its own, and why "
                 "comparing loan estimates side by side is the only honest comparison.",
             ]),
             ("Buying the rate down", [
                 "You can pay points at closing to lower the rate. Whether that is sensible "
                 "depends entirely on how long you keep the loan. Points have a break-even "
                 "period, and if you sell or refinance before it, you lost money.",
                 "Nobody can tell you how long you will keep the loan. You can, roughly, and "
                 "you should be the one deciding.",
             ]),
             ("The lowest payment trap", [
                 "Stretching a balance back out to thirty years lowers the monthly payment "
                 "and can raise the total cost enormously. A refinance that drops your "
                 "payment while restarting the clock is not automatically a win, and it is "
                 "the easiest thing in this business to sell to someone who is only looking "
                 "at the monthly number.",
                 "Ask for both: what the payment becomes, and what the loan costs in total "
                 "over the years you expect to hold it.",
             ]),
         ]),

    dict(slug="what-a-va-loan-is-worth", icon="home",
         title="What a VA loan is actually worth",
         blurb="No down payment, no monthly mortgage insurance, reusable, and a funding fee "
               "that disappears at a 10% disability rating.",
         sections=[
             ("The benefit is bigger than people think", [
                 "For an eligible veteran the VA loan is usually the strongest option on the "
                 "table, and a striking number of people who qualify never find out they do. "
                 "No down payment in many cases. No monthly mortgage insurance, which is the "
                 "part that quietly outweighs everything else over a full term.",
                 "It is also reusable. The benefit is not one-and-done, and entitlement can "
                 "often be restored or partially reused.",
             ]),
             ("The funding fee, and the rating that removes it", [
                 "There is a one-time VA funding fee. It is waived entirely for veterans with "
                 "a service-connected disability rating of 10% or higher.",
                 "That single fact changes the math on a great many files, and it is the most "
                 "commonly missed thing in the whole process. If you are rated and nobody has "
                 "asked you about it, they have not run your numbers properly.",
             ]),
             ("The friction, honestly", [
                 "A VA loan is not a rubber stamp. The property has to pass a VA appraisal, "
                 "and some sellers still believe VA offers are harder to close.",
                 "That belief is mostly outdated, but it is real, and it is a communication "
                 "problem your lender and agent should be handling on your behalf rather "
                 "than leaving you to argue.",
             ]),
             ("Already in a VA loan", [
                 "Then the streamline refinance — the IRRRL — is worth understanding. Less "
                 "paperwork, usually no new appraisal, and VA requires the costs to recoup "
                 "within 36 months, which is a genuine protection rather than red tape.",
             ]),
         ]),

    dict(slug="closing-costs-itemized", icon="book",
         title="Closing costs, line by line",
         blurb="What each item is, who sets it, and which ones you can actually shop for.",
         sections=[
             ("Three kinds of cost", [
                 "Closing costs fall into three groups and they behave completely "
                 "differently. Lender charges, third-party services, and prepaid items that "
                 "are not really costs at all.",
                 "Lumping them together is how a closing disclosure becomes intimidating.",
             ]),
             ("Lender charges", [
                 "Origination, underwriting, processing. Set by whoever is making the loan, "
                 "and therefore comparable between lenders. This is the part where shopping "
                 "genuinely pays.",
             ]),
             ("Third-party services", [
                 "Appraisal, title work, survey, recording fees. Some you can shop for and "
                 "your loan estimate will say which. Others are set by the county or by the "
                 "state and are the same wherever you go.",
             ]),
             ("Prepaids and escrow", [
                 "Property taxes, homeowner's insurance, and prepaid interest. These are not "
                 "really costs of the loan — they are your own expenses, collected early and "
                 "held for you.",
                 "It is why the cash-to-close number looks larger than the fees suggest, and "
                 "it is also why comparing two lenders on cash-to-close alone is misleading. "
                 "Compare the lender charges.",
             ]),
         ]),

    dict(slug="credit-what-moves-the-needle", icon="chat",
         title="Credit: what moves the needle before you apply",
         blurb="What helps, what does nothing, and what to avoid in the sixty days before an "
               "application.",
         sections=[
             ("What actually matters", [
                 "Payment history and how much of your available credit you are using carry "
                 "the most weight by a distance. Everything else is a rounding error by "
                 "comparison.",
                 "If you do one thing before applying, pay balances down. Utilization "
                 "responds faster than almost anything else on a credit file.",
             ]),
             ("What does nothing", [
                 "Checking your own credit does not hurt it. Neither does earning more, "
                 "having savings, or how long you have banked somewhere. Credit scoring is "
                 "narrower than people expect and does not know most of what you would "
                 "consider relevant.",
             ]),
             ("What to avoid in the sixty days before you apply", [
                 "Do not open new accounts, including store cards at a checkout. Do not close "
                 "old ones — that shortens your history and can raise your utilization. Do "
                 "not let a balance spike, even if you intend to clear it. Do not finance a "
                 "car.",
                 "And once you are under contract, keep doing nothing until you close. "
                 "Lenders re-check credit before funding, and a new account discovered at "
                 "that stage can genuinely stop a closing.",
             ]),
             ("If your credit is recovering", [
                 "It is workable more often than people assume. FHA guidelines are more "
                 "forgiving than conventional, individual lenders apply their own overlays on "
                 "top, and being declined by one lender does not mean the answer is no "
                 "everywhere.",
                 "That difference between lenders is precisely why a broker is useful on a "
                 "recovering file.",
             ]),
         ]),
]


def article(a):
    inner = "".join(
        f"<h2>{S.esc(h)}</h2>" + "".join(f"<p>{S.esc(p)}</p>" for p in ps)
        for h, ps in a["sections"])

    others = [x for x in ARTICLES if x["slug"] != a["slug"]][:3]
    more = "".join(
        f'<a class="lcard" href="/learn/{o["slug"]}" style="--accent:#0f7a4d">'
        f'<h3>{S.esc(o["title"])}</h3><p>{S.esc(o["blurb"])}</p>'
        f'<span class="go">Read {ARROW}</span></a>'
        for o in others)

    schema = (
        '{"@context":"https://schema.org","@type":"Article","headline":%s,'
        '"description":%s,"author":{"@type":"Organization","name":%s},'
        '"publisher":{"@type":"Organization","name":%s}}'
    ) % (S.jstr(a["title"]), S.jstr(a["blurb"]), S.jstr(S.COMPANY), S.jstr(S.COMPANY))

    body = f"""{S.hero(
        eyebrow="Learning Center",
        h1=S.esc(a["title"]),
        lede=S.esc(a["blurb"]),
        trail=[("/", "Home"), ("/learn", "Learning Center"), (None, a["title"])])}

<section><div class="wrap">
<div class="split narrowright">
<div class="prose">
{inner}
<p class="disclose">General information only. Nothing here is a commitment to lend, an offer
of credit, or a rate quote &mdash; those come from a licensed loan officer after a complete
application, and everything is subject to credit approval and underwriting.</p>
</div>
<div>
  <div class="estcard sticky">
    <h3 style="font-size:19px">Put this to work</h3>
    <p class="sub" style="margin-top:8px;font-size:15px">Two minutes and a real number, with
    no credit inquiry.</p>
    <div class="cta" style="margin-top:18px;flex-direction:column;align-items:stretch">
      <a class="btn go" href="/tools/estimate">See what you could save</a>
      <a class="btn ghost" href="/tools/affordability">What can I afford?</a>
      <a class="btn ghost" href="/contact">Ask a question</a>
    </div>
  </div>
</div>
</div>
</div></section>

<section class="alt"><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Keep reading</p>
<h2>Related</h2>
<div class="lgrid">{more}</div>
</div></section>

{S.cta_band()}
"""
    return S.page(
        path=f"/learn/{a['slug']}",
        title=f"{a['title']} | Greenlight Mortgage — Longview, TX",
        desc=a["blurb"][:300],
        body=body,
        trail=[("/", "Home"), ("/learn", "Learning Center"),
               (f"/learn/{a['slug']}", a["title"])],
        extra_schema=schema,
    )


def build():
    print("guides")
    write("/loans/va-irrrl", va_irrrl())
    write("/why-a-broker", why_broker())
    for a in ARTICLES:
        write(f"/learn/{a['slug']}", article(a))


if __name__ == "__main__":
    build()
