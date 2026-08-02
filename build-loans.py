#!/usr/bin/env python3
"""Generates the six loan-program pages and the /loans hub.

One content dict per program; all chrome, compliance and schema come from site.py.
Run: python3 build-loans.py   ->  writes loans/<slug>/index.html + loans/index.html"""
import os

import sitegen as S

APPLY = "https://greenlight.my1003app.com/233918/register"

LOANS = [
  dict(slug="va", nav="VA",
    title="VA Loans in Longview, TX | Greenlight Mortgage",
    desc="VA home loans for veterans and service members in Longview and East Texas. No down payment in many cases and no monthly mortgage insurance. Powered by Co/LAB Lending.",
    h1="VA loans for East Texas veterans",
    lede="You earned this one. A VA loan is usually the strongest option on the table for an eligible veteran — and a lot of people who qualify never find out they do.",
    who=["Veterans, active duty, National Guard and Reserve members",
         "Surviving spouses who meet VA eligibility",
         "Anyone who has been told they need 20% down and hasn't checked their VA benefit"],
    facts=[("No down payment","In many cases you can finance the full purchase price. Not a gimmick — it's the benefit."),
           ("No monthly mortgage insurance","Unlike FHA and most low-down conventional loans. Over a full term this is real money."),
           ("Reusable","The benefit isn't one-and-done. Most people can use it again."),
           ("Funding fee, sometimes waived","There's a one-time VA funding fee — but it's waived entirely at a 10%+ service-connected disability rating.")],
    catch="A VA loan is not a rubber stamp. The property has to pass a VA appraisal, and some sellers still wrongly believe VA offers are harder to close. That's a communication problem, not a loan problem, and it's one we handle on your behalf every week.",
    faqs=[("Can I use a VA loan more than once?","Usually yes. Entitlement can often be restored or partially reused. It depends on your specific history, so it's worth an actual conversation rather than a guess."),
          ("Does a VA loan take longer to close?","Not inherently. The timeline is driven by the appraisal and how quickly documents come back — same as any loan."),
          ("What is a VA IRRRL?","A streamline refinance for veterans already in a VA loan. Less paperwork than a full refinance. VA requires it to produce a real benefit and for costs to recoup within 36 months."),
          ("Is the funding fee always charged?","No. It's waived for veterans with a service-connected disability rating of 10% or more.")]),

  dict(slug="conventional", nav="Conventional",
    title="Conventional Loans in Longview, TX | Greenlight Mortgage",
    desc="Conventional home loans in Longview and East Texas for buyers with steady income and solid credit. Powered by Co/LAB Lending. Equal Housing Opportunity.",
    h1="Conventional loans",
    lede="The standard route, and often the cheapest over the life of the loan if you qualify for it. Less flexible than FHA, but fewer strings attached once you're in.",
    who=["Buyers with steady, documentable income","Credit in reasonable shape","Anyone who can put down enough to avoid or quickly drop mortgage insurance","Buyers of second homes and investment property"],
    facts=[("Down payments start lower than people think","3% programs exist for qualifying first-time buyers. The 20% rule is a myth that costs people years."),
           ("Mortgage insurance comes off","Unlike FHA, conventional PMI can be removed once you reach sufficient equity."),
           ("Works for non-primary homes","Second homes and investment properties, which government programs generally won't cover."),
           ("Credit matters more here","Pricing is more sensitive to your score than on government loans.")],
    catch="Conventional underwriting is less forgiving. If your income is complicated, your credit is recovering, or your down payment is thin, FHA or a government program may genuinely serve you better. We'll say so.",
    faqs=[("How much do I actually need to put down?","Less than most people assume. Qualifying first-time buyers can see programs as low as 3%. What you should put down is a different question from what you must."),
          ("When does PMI go away?","Once you've built sufficient equity. Timing depends on your loan and how the value moves."),
          ("Is conventional always better than FHA?","No. For lower credit or a thinner down payment, FHA is frequently the better deal. It depends entirely on your file.")]),

  dict(slug="fha", nav="FHA",
    title="FHA Loans in Longview, TX | Greenlight Mortgage",
    desc="FHA home loans in Longview and East Texas. Lower down payment and more flexible credit requirements. Powered by Co/LAB Lending. Equal Housing Opportunity.",
    h1="FHA loans",
    lede="Built for people the conventional box doesn't fit. Lower down payment, more forgiving credit requirements, and the most common first step into a first house.",
    who=["First-time buyers","Anyone rebuilding credit after a rough stretch","Buyers with a smaller down payment saved","People who've been turned down for a conventional loan"],
    facts=[("Low down payment","3.5% down for qualifying borrowers."),
           ("Credit flexibility","FHA guidelines are more forgiving than conventional. Note that individual lenders add their own overlays on top."),
           ("Gift funds allowed","The down payment can come from an eligible gift."),
           ("Assumable","In some cases a future buyer can take over your FHA loan — which can matter a great deal in a higher-rate market.")],
    catch="FHA carries mortgage insurance, and on most loans today it stays for the life of the loan rather than dropping off. That's the real tradeoff. Many people refinance out of FHA later once credit and equity improve — a legitimate strategy, but plan for it going in.",
    faqs=[("What credit score do I need?","FHA's guidelines are more flexible than conventional, but individual lenders apply their own overlays. Being told no by one lender doesn't mean the answer is no."),
          ("Does FHA mortgage insurance ever come off?","On most current FHA loans it remains for the life of the loan. The common path off it is refinancing later."),
          ("Can I use FHA for a fixer-upper?","There are renovation options. Worth asking about specifically.")]),

  dict(slug="usda", nav="USDA",
    title="USDA Loans in Longview & East Texas | Greenlight Mortgage",
    desc="USDA rural home loans across East Texas. More of Gregg, Harrison and Upshur County qualifies than most people expect. Powered by Co/LAB Lending.",
    h1="USDA loans",
    lede="The most overlooked program in East Texas. Zero down payment on eligible properties — and far more of the area around Longview qualifies than people assume.",
    who=["Buyers looking just outside Longview city limits","Anyone buying in Gilmer, Hallsville, White Oak, Diana, Ore City and similar","Households within the income limits for the area","Buyers with nothing saved for a down payment"],
    facts=[("Zero down payment","On eligible properties. One of only two zero-down programs, and the other one requires military service."),
           ("The map is bigger than you think","People rule themselves out assuming they're too close to town. Check the address before you assume."),
           ("Income limits apply","It's tied to household income for the area, so it isn't for everyone."),
           ("Property has to qualify too","Both you and the house have to be eligible.")],
    catch="Two things have to line up: the property address and your household income. If either misses, USDA is off the table — so it's worth checking the address early rather than falling in love with a house first.",
    faqs=[("Does my area qualify?","More of East Texas than most people expect. It's determined by specific address, not by city or county, so check the actual property."),
          ("What are the income limits?","They're set by household size and area, and they're revised periodically. We'll check yours against the current figures."),
          ("Is it really zero down?","On eligible properties, yes. There are still closing costs, which is a separate conversation.")]),

  dict(slug="jumbo", nav="Jumbo",
    title="Jumbo Loans in Longview, TX | Greenlight Mortgage",
    desc="Jumbo home loans in Longview and East Texas for purchases above conforming limits. Powered by Co/LAB Lending. Equal Housing Opportunity.",
    h1="Jumbo loans",
    lede="For a purchase above the conforming loan limit. Different underwriting, a different set of lenders, and the place where being a broker rather than a bank matters most.",
    who=["Buyers above the conforming limit for the county","Higher-income borrowers with more complex finances","Self-employed buyers with strong but non-standard income","Anyone a single bank has already declined"],
    facts=[("Different rules entirely","Jumbo isn't backed by Fannie or Freddie, so each lender writes its own guidelines."),
           ("Reserves matter","Expect to document assets beyond the down payment."),
           ("Where a broker earns their keep","Jumbo guidelines vary enormously between lenders. One says no, another says yes on the same file. A bank only has its own answer."),
           ("Self-employment is workable","Complex income is normal in this space rather than a red flag.")],
    catch="Jumbo underwriting is genuinely more demanding — more documentation, more scrutiny, and more reserves. The upside is that the variation between lenders is huge, which is precisely why shopping it matters more here than on any other product.",
    faqs=[("What makes a loan jumbo?","Anything above the conforming loan limit for the county. That limit changes periodically, so check the current figure."),
          ("Do I need 20% down?","Not necessarily. Lender requirements vary widely on jumbo, which is exactly why it's worth shopping."),
          ("I'm self-employed. Is that a problem?","No. It's common in jumbo lending. It means more documentation, not a worse outcome.")]),

  dict(slug="refinance", nav="Refinance",
    title="Refinancing in Longview, TX | Greenlight Mortgage",
    desc="Mortgage refinancing in Longview and East Texas. Lower the payment, shorten the term, or use equity. Powered by Co/LAB Lending. Equal Housing Opportunity.",
    h1="Refinancing",
    lede="Three reasons people refinance: a lower payment, a shorter term, or getting at equity. The honest answer is that it isn't always worth doing — and we'll tell you when it isn't.",
    who=["Anyone whose rate is meaningfully above today's market","Homeowners wanting to drop mortgage insurance","People consolidating higher-interest debt","Veterans in a VA loan — see the IRRRL below"],
    facts=[("Rate-and-term","Lower the rate, change the term, or both. The most common reason."),
           ("Cash-out","Use built equity for a renovation or to consolidate debt. Your balance goes up — that's the trade."),
           ("Dropping mortgage insurance","Sometimes the savings has nothing to do with rate and everything to do with removing MI."),
           ("VA IRRRL","A streamline refinance for veterans already in a VA loan. Less paperwork than a full refinance.")],
    catch="Refinancing costs money to do. If you're moving in two years, the savings may never catch up to the closing costs. For VA refinances, federal rules require a real net tangible benefit and that costs recoup within 36 months — a standard worth applying to every refinance, not just VA ones. If the math doesn't work we'll say so and leave you alone.",
    faqs=[("How do I know if it's worth it?","Compare what you'd save monthly against what it costs to do. If it takes longer to break even than you plan to stay in the house, it isn't worth it."),
          ("Will this restart my 30 years?","It can, and that matters. A lower payment on a longer term isn't always a win. We'll show you both."),
          ("What's a VA IRRRL?","A streamline refinance for veterans already holding a VA loan. Less documentation, and VA requires costs to recoup within 36 months."),
          ("Can I take cash out?","Often, yes. It increases your balance, so it should be for something worth it.")]),
]

# ---------------------------------------------------------------------------
# Rendering. Chrome, compliance, and schema all come from site.py so the
# license block cannot drift between these pages and the rest of the site.

ARROW = ('<svg viewBox="0 0 14 9" aria-hidden="true"><path d="M9.2.8 13 4.5 9.2 8.2M13 4.5H1"'
         ' fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"'
         ' stroke-linejoin="round"/></svg>')


def loan_body(l):
    who = "".join(f"<li>{S.esc(w)}</li>" for w in l["who"])
    facts = "".join(
        f'<div class="card reveal"><h3>{S.esc(k)}</h3><p>{S.esc(v)}</p></div>'
        for k, v in l["facts"])
    faqs = "".join(
        f'<details><summary>{S.esc(q)}</summary><div class="a"><p>{S.esc(a)}</p></div></details>'
        for q, a in l["faqs"])

    return f"""{S.hero(
        eyebrow=f'{S.esc(l["nav"])} loans &middot; Longview, TX',
        h1=S.esc(l["h1"]),
        lede=S.esc(l["lede"]),
        ctas=[("/tools/estimate", "See what you could save", "go"),
              ("/contact", "Talk to a person", "ghost")],
        trail=[("/", "Home"), ("/loans", "Loan options"), (None, l["nav"])])}

<section><div class="wrap">
<div class="split">
<div class="reveal">
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Who this is for</p>
  <h2>Is this you?</h2>
  <ul class="ticks">{who}</ul>
</div>
<div class="reveal">
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>The honest part</p>
  <h2>Where it can bite</h2>
  <p class="sub">{S.esc(l["catch"])}</p>
  <div class="callout">
    <h3>We will tell you when it is not worth it.</h3>
    <p>We are brokers, not a single bank with one menu to sell. If a different program
    serves you better &mdash; or if doing nothing serves you better &mdash; that is the
    answer you will get.</p>
  </div>
</div>
</div>
</div></section>

<section class="dark"><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>What matters</p>
<h2>The parts worth knowing</h2>
<div class="grid g2">{facts}</div>
</div></section>

<section><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Questions</p>
<h2>Straight answers</h2>
<div class="faq">{faqs}</div>
</div></section>

{S.cta_band(
    head=f'Find out where you stand on a {l["nav"]} loan.',
    sub="Answer a few questions and see an estimate in about two minutes. No hard credit "
        "pull to begin, and a licensed loan officer follows up within one business day.")}
"""


def build():
    print("loan pages")
    for l in LOANS:
        body = loan_body(l)
        out = S.page(
            path=f'/loans/{l["slug"]}',
            title=l["title"],
            desc=l["desc"],
            body=body,
            trail=[("/", "Home"), ("/loans", "Loan options"), (f'/loans/{l["slug"]}', l["nav"])],
            faqs=l["faqs"],
        )
        os.makedirs(f'loans/{l["slug"]}', exist_ok=True)
        with open(f'loans/{l["slug"]}/index.html', "w") as f:
            f.write(out)
        # Legacy flat file from the pass that shipped nav pointing at /loans/va
        # while the files were at /loans/va.html. Remove it if it reappears.
        if os.path.exists(f'loans/{l["slug"]}.html'):
            os.remove(f'loans/{l["slug"]}.html')
        print(f'  loans/{l["slug"]}/index.html  ({len(out):,} bytes)')

    # ---------------------------------------------------------------- hub page
    cards = "".join(
        S.loan_card(l["slug"], l["nav"], S.esc(l["lede"]), cls="reveal")
        for l in LOANS)

    hub_faqs = [
        ("How do I know which loan I need?",
         "You do not have to. That is our job. Tell us the situation and we will lay the "
         "options out side by side in plain English, including what each one actually costs "
         "you over time."),
        ("Can I switch programs later?",
         "Often, yes. Plenty of people start on FHA and refinance to conventional once credit "
         "and equity improve. It is a legitimate strategy, not a workaround."),
        ("What does it cost to find out where I stand?",
         "Nothing, and there is no hard credit pull to begin the conversation."),
        ("Why use a broker instead of my bank?",
         "A bank can only offer you what that bank has. We are licensed in five states and we "
         "shop a network of lenders, which matters most on the files banks find awkward — "
         "self-employed income, thinner credit, jumbo amounts, or rural addresses."),
    ]
    faq_html = "".join(
        f'<details><summary>{S.esc(q)}</summary><div class="a"><p>{S.esc(a)}</p></div></details>'
        for q, a in hub_faqs)

    body = f"""{S.hero(
        eyebrow="Loan options",
        h1="Whatever the situation <em>actually</em> is",
        lede="First house, fifth house, self-employed, rebuilding credit, or just tired of "
             "the payment you have. There is usually a path &mdash; and we shop a network of "
             "lenders to find it instead of selling you one bank&rsquo;s menu.",
        ctas=[("/tools/estimate", "See what you could save", "go"),
              ("/contact", "Talk to a person", "ghost")],
        trail=[("/", "Home"), (None, "Loan options")])}

<section><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Six programs</p>
<h2>Start with the one that sounds like you.</h2>
<p class="sub">Not sure? Start anywhere. The differences matter less than getting an actual
look at your file.</p>
<div class="lgrid">{cards}</div>
</div></section>

<section class="alt"><div class="wrap">
<div class="split">
<div class="reveal">
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>The honest part</p>
  <h2>No single program is best for everyone.</h2>
  <p class="sub">FHA beats conventional on some files and costs more on others. USDA is
  effectively free money if the address qualifies and useless if it does not. VA is almost
  always the strongest option for someone eligible &mdash; and a lot of eligible people never
  find out they are.</p>
  <p class="sub">That is the whole reason a broker beats a bank here. We are not paid to steer
  you toward one answer.</p>
</div>
<div class="reveal">
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>How it goes</p>
  <div class="steps">
    <div class="step"><h3>Tell us the situation</h3><p>A short conversation or the online
    estimator. No hard credit pull to begin.</p></div>
    <div class="step"><h3>We shop it</h3><p>We take your file to a network of lenders rather
    than a single menu, and bring back what is actually available.</p></div>
    <div class="step"><h3>You decide</h3><p>Options side by side, in plain English, including
    the option of doing nothing.</p></div>
  </div>
</div>
</div>
</div></section>

<section><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Questions</p>
<h2>Straight answers</h2>
<div class="faq">{faq_html}</div>
</div></section>

{S.cta_band()}
"""
    out = S.page(
        path="/loans",
        title="Loan Options in Longview, TX | Greenlight Mortgage",
        desc="Conventional, FHA, VA, USDA, jumbo and refinance options in Longview and East "
             "Texas. A mortgage broker that shops a network of lenders. Powered by Co/LAB "
             "Lending. Equal Housing Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/loans", "Loan options")],
        faqs=hub_faqs,
    )
    with open("loans/index.html", "w") as f:
        f.write(out)
    print(f"  loans/index.html  ({len(out):,} bytes)")


if __name__ == "__main__":
    build()
    print(f"\n{len(LOANS)} loan pages + hub built.")
