#!/usr/bin/env python3
"""Generates the homepage and every content page.

Same pattern as build-loans.py: content as data, chrome from sitegen.
Run: python3 build-pages.py   (or python3 build.py to run everything)

RULE OBSERVED THROUGHOUT: where a fact is not confirmed, the page says so
visibly rather than filling the gap with something plausible. Search this file
for TODO to find every one of them.
"""
import os

import sitegen as S

A = S.APPLY

ARROW = S.ARROW

STAR = ('<svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">'
        '<path d="M10 1.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L10 14.9l-5.2 2.7 1-5.8L1.5 7.7l5.9-.9z"/></svg>')


def write(path, html_out):
    """path is a site URL: '/about' -> about/index.html ; '/' -> index.html"""
    rel = "index.html" if path == "/" else path.strip("/") + "/index.html"
    os.makedirs(os.path.dirname(rel) or ".", exist_ok=True)
    with open(rel, "w") as f:
        f.write(html_out)
    print(f"  {rel}  ({len(html_out):,} bytes)")


# ---------------------------------------------------------------------- icons
# Drawn for this site rather than pulled from a set. Each one is specific to the
# thing it labels — a signpost for choosing between loan programs, a lantern for
# the brand, an actual amortization curve for the calculator. The previous set
# was four variations on a rounded rectangle, which is the tell of a generated
# site: technically an icon, semantically nothing.
#
# Two-layer construction throughout: a soft filled shape carrying the green, a
# crisp stroke on top. That is what stops line icons looking like clip-art.

def icon(body, fill=""):
    return (f'<svg viewBox="0 0 32 32" fill="none" aria-hidden="true">'
            f'{fill}{body}</svg>')


_S = ('stroke="currentColor" stroke-width="1.9" stroke-linecap="round" '
      'stroke-linejoin="round" fill="none"')
_F = 'fill="currentColor" opacity=".15"'

ICONS = {
    # Signpost: several ways to go, which is the actual proposition of the page.
    "loans": icon(
        f'<path d="M16 4.5v23" {_S}/>'
        f'<path d="M6.5 8.5h15l3.5 3.5-3.5 3.5h-15z" {_F}/>'
        f'<path d="M6.5 8.5h15l3.5 3.5-3.5 3.5h-15z" {_S}/>'
        f'<path d="M25.5 18h-15L7 21.5 10.5 25h15z" {_S}/>'
        f'<path d="M12 27.5h8" {_S}/>'),

    # A real amortization curve, not a calculator body with fake buttons.
    "calc": icon(
        f'<path d="M4.5 25.5V6.5" {_S}/><path d="M4.5 25.5h23" {_S}/>'
        f'<path d="M8 25.5c6-1 9-3.5 11-8s3.5-7.5 7.5-9v17z" {_F}/>'
        f'<path d="M8 22.5c6-1 9-3.5 11-8s3.5-7.5 7.5-9" {_S}/>'
        f'<circle cx="26.5" cy="5.5" r="2" fill="currentColor"/>'),

    # House with the roofline doubling as a rising value line.
    "home": icon(
        f'<path d="M5 15 16 6l11 9v12H5z" {_F}/>'
        f'<path d="M3 16.5 16 5.5l13 11" {_S}/>'
        f'<path d="M6 14.5V27h20V14.5" {_S}/>'
        f'<path d="M12.5 27v-7.5h7V27" {_S}/>'
        f'<path d="M20.5 11.5h4.5V16" {_S}/>'),

    # Quote inside a speech bubble — testimonials, not a generic star.
    "star": icon(
        f'<path d="M4.5 8.5A2.5 2.5 0 0 1 7 6h18a2.5 2.5 0 0 1 2.5 2.5v11A2.5 2.5 0 0 1 25 22h-9.5L9 27v-5H7a2.5 2.5 0 0 1-2.5-2.5z" {_F}/>'
        f'<path d="M4.5 8.5A2.5 2.5 0 0 1 7 6h18a2.5 2.5 0 0 1 2.5 2.5v11A2.5 2.5 0 0 1 25 22h-9.5L9 27v-5H7a2.5 2.5 0 0 1-2.5-2.5z" {_S}/>'
        f'<path d="M12 10.5c-1.8 0-3 1.2-3 2.9 0 1.5 1 2.6 2.4 2.6.4 0 .8-.1 1-.2-.3 1.1-1.2 2-2.3 2.4M20.5 10.5c-1.8 0-3 1.2-3 2.9 0 1.5 1 2.6 2.4 2.6.4 0 .8-.1 1-.2-.3 1.1-1.2 2-2.3 2.4" {_S}/>'),

    # Coins with an upward arrow — savings, specifically.
    "save": icon(
        f'<ellipse cx="13" cy="9" rx="8.5" ry="3.5" {_F}/>'
        f'<path d="M21.5 9c0 1.9-3.8 3.5-8.5 3.5S4.5 10.9 4.5 9 8.3 5.5 13 5.5 21.5 7.1 21.5 9z" {_S}/>'
        f'<path d="M4.5 9v6c0 1.9 3.8 3.5 8.5 3.5M4.5 15v6c0 1.9 3.8 3.5 8.5 3.5 1 0 2-.1 2.9-.2" {_S}/>'
        f'<path d="M21.5 9v4" {_S}/>'
        f'<path d="M23 27v-8m0 0-3.5 3.5M23 19l3.5 3.5" {_S}/>'),

    # Open book with a bookmark.
    "book": icon(
        f'<path d="M4 6.5h9a3 3 0 0 1 3 3V26a3 3 0 0 0-3-3H4z" {_F}/>'
        f'<path d="M4 6.5h9a3 3 0 0 1 3 3V26a3 3 0 0 0-3-3H4zM28 6.5h-9a3 3 0 0 0-3 3V26a3 3 0 0 1 3-3h9z" {_S}/>'
        f'<path d="M21.5 6.5v7l2.5-1.8 2.5 1.8v-7" {_S}/>'),

    # Two bubbles — a conversation, not a notification.
    "chat": icon(
        f'<path d="M3.5 8.5A2.5 2.5 0 0 1 6 6h11a2.5 2.5 0 0 1 2.5 2.5v6A2.5 2.5 0 0 1 17 17H9l-5.5 4z" {_F}/>'
        f'<path d="M3.5 8.5A2.5 2.5 0 0 1 6 6h11a2.5 2.5 0 0 1 2.5 2.5v6A2.5 2.5 0 0 1 17 17H9l-5.5 4z" {_S}/>'
        f'<path d="M23 12h3a2.5 2.5 0 0 1 2.5 2.5v6A2.5 2.5 0 0 1 26 23h-1v4l-5-4h-4a2.5 2.5 0 0 1-2.4-1.8" {_S}/>'),

    # Shield with a check — underwriting, verification.
    "shield": icon(
        f'<path d="M16 3.5 5.5 8v8c0 6.7 4.4 12.3 10.5 13.9C22.1 28.3 26.5 22.7 26.5 16V8z" {_F}/>'
        f'<path d="M16 3.5 5.5 8v8c0 6.7 4.4 12.3 10.5 13.9C22.1 28.3 26.5 22.7 26.5 16V8z" {_S}/>'
        f'<path d="m11.5 16.5 3.2 3.2 6.3-6.6" {_S}/>'),
}


# ==========================================================================
# HOMEPAGE
# ==========================================================================

def homepage():
    tiles = [
        ("/loans", "loans", "Explore loan options",
         "Conventional, FHA, VA, USDA, jumbo and refinance — what each one actually costs you."),
        ("/tools/calculator", "calc", "Mortgage calculator",
         "Payment breakdown, full amortization, and what an extra $100 a month really does."),
        ("/tools/home-value", "home", "Check my home value",
         "A local estimate on your address, prepared by someone who works this market."),
        ("/testimonials", "star", "Client testimonials",
         "Real clients, in their own words, with the source shown on every one."),
    ]
    tile_html = "".join(
        f'<a class="tile" href="{h}"><span class="ti">{ICONS[i]}</span>'
        f'<h3>{t}</h3><p>{p}</p>'
        f'<span class="go">Open {ARROW}</span></a>'
        for h, i, t, p in tiles)

    quotes = "".join(S.review_card(r) for r in S.REVIEWS[:6])

    loans = "".join(
        S.loan_card(slug, nav, blurb, cls="reveal")
        for slug, nav, blurb in [
            ("conventional", "Conventional",
             "The standard route, and often the lowest total cost once you qualify."),
            ("fha", "FHA",
             "Lower down payment, more forgiving credit. The most common first step."),
            ("va", "VA",
             "For eligible veterans. Frequently no down payment and no monthly mortgage insurance."),
            ("usda", "USDA",
             "Zero down on eligible rural addresses. More of East Texas qualifies than people expect."),
            ("jumbo", "Jumbo",
             "Above the conforming limit, where shopping a network of lenders matters most."),
            ("refinance", "Refinancing",
             "Lower the payment, shorten the term, or use equity. Including the VA IRRRL."),
        ])

    towns = "".join(f"<span>{t}</span>" for t in S.TOWNS)

    # The two doors — first thing on the page, per KT. A BOLD question, an
    # explicit pick-one instruction, and two visibly different paths with real
    # buttons: refinance goes to the refi funnel; purchase opens with the
    # veteran question and NEVER shares a destination with refinance.
    doors = f"""<section class="doors" aria-label="What brings you here today">
  <div class="doorswrap">
    <p class="doorsq"><strong>What brings you here today?</strong>
    <span>Pick the answer below &mdash; the two paths are completely different,
    and picking right saves you time.</span></p>
    <div class="doorsgrid">

      <div class="door refi">
        <span class="dnum">01</span>
        <span class="dkick">I already own a home</span>
        <span class="dtitle">Refinance</span>
        <ul class="dlist">
          <li>Lower the payment</li>
          <li>Shorten the term</li>
          <li>Drop mortgage insurance</li>
          <li>Use my equity</li>
        </ul>
        <p class="dnote">Veteran with a VA loan? Ask about the
        <a href="/loans/va-irrrl">VA IRRRL</a> &mdash; the streamline refinance
        built for you.</p>
        <a class="btn shiny lg dbtn" href="/loans/refinance" data-funnel-cta="door_refi">
          Click here &mdash; see refinancing options &rarr;</a>
      </div>

      <div class="door buy">
        <span class="dnum">02</span>
        <span class="dkick">I&rsquo;m buying a home</span>
        <span class="dtitle">Purchase</span>
        <span class="dsub">A completely different path than refinancing &mdash;
        and it starts with one question:</span>
        <p class="dvetq">Are you a veteran or service member?</p>
        <div class="dvet">
          <a class="btn shiny lg dbtn" href="/loans/va" data-funnel-cta="door_va">
            YES &mdash; use my VA benefit &rarr;</a>
          <a class="btn onDark lg dbtn" href="/buy" data-funnel-cta="door_buy">
            NO &mdash; show me my path &rarr;</a>
        </div>
      </div>

    </div>
    <p class="doorsnote">Not sure yet? <a href="#estimator">Play with the dials
    below</a> &mdash; estimate only, no hard credit pull, nobody asks for your email.</p>
  </div>
</section>"""

    body = f"""
{doors}

<div class="hero home"><div class="wrap">
<div class="herogrid">
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Longview, Texas &middot; Licensed in {S.STATE_COUNT_WORD} states</p>
  <h1>A mortgage broker, <span class="rule">not a bank.</span></h1>
  <p class="lede">A bank can only sell you what the bank has. We shop a network of lenders,
  bring back the real options, and tell you which one actually costs you less &mdash;
  including when the answer is to do nothing.</p>
  <div class="cta">
    <a class="btn go lg" href="#estimator" data-big-cta data-short-label="See your number">See what you could save &darr;</a>
    <a class="btn ghost lg" href="/about">Meet the team</a>
  </div>
  <div class="heroproof">
    <div><b>2008</b><span>Serving East Texas since</span></div>
    <div><b>{S.STATE_COUNT}</b><span>States licensed</span></div>
    <div><b>{len(S.TESTIMONIALS)}</b><span>Client reviews, verbatim</span></div>
  </div>
</div>
<div>
  <div class="vidframe">
    <video controls preload="metadata" playsinline
           poster="/assets/from-old-site/kenneth-travis-headshot.png">
      <source src="/assets/from-old-site/kt-video.mp4" type="video/mp4">
      Your browser cannot play this video.
      <a href="/assets/from-old-site/kt-video.mp4">Download it instead</a>.
    </video>
  </div>
  <p class="vidcap">Kenneth Travis &middot; President &amp; CEO &middot;
  Loan Originator NMLS #{S.NMLS_KT}</p>
</div>
</div>
</div></div>

{S.funnel_rig_dual()}

{S.funnel_yes("home", "dual")}

<div class="wrap"><div class="tiles">{tile_html}</div></div>

<section class="dark letter"><div class="wrap">
<div class="split">
<div class="reveal">
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>From Kenneth</p>
  <h2>Longview, TX mortgage consultant</h2>
  <p class="salut">Dear Future Homeowner,</p>
  <p class="sub">My name is <strong>Kenneth Travis</strong>, and thank you for taking the
  time to visit. You will find plenty here to help you buy a home or refinance the one you
  are in &mdash; and a few tools that give you a real number before you ever pick up the
  phone.</p>
  <p class="sub">Every customer has specific needs, so we meet them with a wide range of
  products and lenders, and with quality service and individual attention. What I can
  promise you is straight answers and a team that returns your call. Whether a particular
  loan works is decided by underwriting, not by me &mdash; and I would rather tell you that
  up front than sell you something that falls apart at closing.</p>
  <p class="sub">The question I built this company around was simple:
  <em>how can we be better, how can we be different?</em></p>

  <div class="sign">
    <img src="/assets/from-old-site/kenneth-travis-headshot.png" alt="" width="72" height="72">
    <div>
      <p class="signame">Kenneth Travis</p>
      <p class="sigrole">President &amp; CEO &middot; Loan Originator NMLS #{S.NMLS_KT}<br>
      United States Marine Corps, eight years, Sergeant</p>
    </div>
  </div>

  <div class="cta">
    <a class="btn go" href="/contact">Questions? Contact me</a>
    <a class="btn onDark" href="{A}">Start an application</a>
  </div>
</div>
<div class="reveal">
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Core values</p>
  <h2>The standard others get measured by.</h2>
  <div class="grid g2" style="margin-top:26px">
    <div class="card"><span class="num">01</span><h3>Service &amp; Compassion</h3>
    <p>We honor the client experience by treating each borrower like a member of our family.
    We are in business to serve our clients, our employees, and our community.</p></div>
    <div class="card"><span class="num">02</span><h3>Operational Excellence</h3>
    <p>We excel by continually improving and constantly exceeding standards. We review our
    processes and support systems to ensure customer satisfaction.</p></div>
    <div class="card"><span class="num">03</span><h3>Trust &amp; Integrity</h3>
    <p>We cherish lasting relationships built on integrity, transparent communication, and
    respect. We are committed to doing the right thing, 100% of the time.</p></div>
    <div class="card"><span class="num">04</span><h3>Green means GO!</h3>
    <p>Drive home with Greenlight Mortgage. When the light turns green you should already
    know what you are driving into &mdash; no surprises at the closing table.</p></div>
  </div>
</div>
</div>
</div></section>

<section class="alt"><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Loan options</p>
<h2>Whatever the situation actually is.</h2>
<p class="sub">First house, fifth house, self-employed, rebuilding credit, or just tired of
the payment you have.</p>
<div class="lgrid">{loans}</div>
</div></section>

<section><div class="wrap">
<div class="split narrowright">
<div class="reveal">
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Why a broker</p>
  <h2>One bank has one menu. We have a network.</h2>
  <p class="sub">A loan officer at a bank can only offer you that bank's programs at that
  bank's pricing. If your file does not fit, the answer is no, and that is the end of the
  conversation.</p>
  <p class="sub">We are a brokerage. We take the same file to a network of lenders and come
  back with what is actually available. That matters most on exactly the files banks find
  awkward &mdash; self-employed income, credit that is recovering, a rural address, a jumbo
  amount, a VA benefit nobody explained properly.</p>
  <div class="steps">
    <div class="step"><h3>Tell us the situation</h3><p>A short conversation or the online
    estimator. No hard credit pull to start.</p></div>
    <div class="step"><h3>We shop it</h3><p>Your file goes to a network of lenders rather
    than one menu.</p></div>
    <div class="step"><h3>You decide</h3><p>Options side by side in plain English, including
    the option to walk away.</p></div>
  </div>
</div>
<div class="reveal">
  <div class="callout" style="margin-top:0">
    <h3>Licensed in {S.STATE_COUNT_WORD} states</h3>
    <p>{S.STATE_NAMES}. If you are moving out of the area &mdash; or into it &mdash; we may
    still be able to help.</p>
  </div>
  <div class="callout">
    <h3>We do not rebuild the application</h3>
    <p>Applying happens on a licensed loan origination system under Kenneth's own NMLS. Your
    Social Security number and income documents go there, not into a marketing website.</p>
  </div>
</div>
</div>
</div></section>

<section class="alt"><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Client testimonials</p>
<h2>What East Texas says.</h2>
<p class="sub">Real clients, in their own words. Each one shows where it came from &mdash; and where we have not yet re-checked the wording against its source, it says so.</p>
<div class="tgrid">{quotes}</div>
<div class="cta"><a class="btn ghost" href="/testimonials">Read all seven {ARROW}</a>
<a class="btn ghost" href="/reviews">Where to find our reviews</a></div>
</div></section>

<section><div class="wrap">
<div class="locard reveal">
  <img src="/assets/from-old-site/kenneth-travis-headshot.png"
       alt="Kenneth Travis, President and CEO of Greenlight Mortgage" width="168" height="168">
  <div>
    <h3>Kenneth Travis</h3>
    <p class="role">President &amp; CEO &middot; NMLS #{S.NMLS_KT}</p>
    <p class="meta">{S.COMPANY}<br>{S.STREET}, {S.CITY}, {S.STATE} {S.ZIP}<br>
    <a href="tel:{S.PHONE_HREF}">{S.PHONE}</a></p>
    <p class="tag">&ldquo;{S.TAGLINE}&rdquo;</p>
    <div class="cta" style="margin-top:22px">
      <a class="btn" href="{A}">Start an application</a>
      <a class="btn ghost" href="/contact">Ask a question first</a>
    </div>
  </div>
</div>
</div></section>

<section class="dark"><div class="wrap">
<div class="split">
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Where we work</p>
  <h2>East Texas is the whole point.</h2>
  <p class="sub">We live here. We know which Longview neighborhoods appraise the way people
  expect and which ones surprise them, which addresses just outside town still qualify for a
  zero-down USDA loan, and how long a Gregg County closing actually takes.</p>
  <p class="sub">That is not a marketing line. It is the difference between a file that closes
  on time and one that falls over at the appraisal.</p>
</div>
<div>
  <p class="places">{towns}</p>
  <p class="districts">Including the {", ".join(S.DISTRICTS)} communities &mdash; and we lend
  in {S.STATE_COUNT_WORD} states, so a move out of the area does not have to mean a new lender.</p>
</div>
</div>
</div></section>

{S.cta_band(
    head="Two minutes for a real number.",
    sub="Answer a few questions and see an estimate on screen. No hard credit pull to begin, "
        "and a licensed loan officer follows up within one business day — once, not six times.")}
"""

    return S.page(
        path="/",
        title="Longview TX Mortgage Consultant | Greenlight Mortgage — Kenneth Travis",
        desc="Greenlight Mortgage in Longview, Texas — a mortgage broker, not a bank. We shop "
             "a network of lenders for purchase, refinance, VA, FHA, USDA and jumbo loans "
             "across East Texas. Powered by Co/LAB Lending. Equal Housing Opportunity.",
        body=body,
        org=True,
        trail=[("/", "Home")],
        scripts=S.FUNNEL_SCRIPTS,
    )


# ==========================================================================
# /buy — the purchase gateway
# ==========================================================================
# The homepage purchase door's "NO — show me my path" lands here: a purchase
# funnel path that is deliberately separate from anything refinance. One
# veteran check at the top (belt and braces — some arrive here directly),
# then situation cards into the right program funnel, then the purchase rig
# and the YES walk-through for anyone still unsure.

def buy_page():
    situations = [
        ("fha", "FHA",
         "First house, thinner savings, or credit still healing. 3.5% down for "
         "qualifying buyers &mdash; and the down payment can be a gift."),
        ("conventional", "Conventional",
         "Steady income, credit in decent shape. Often the lowest total cost "
         "once you qualify &mdash; and the 20% rule is a myth."),
        ("usda", "USDA",
         "Buying just outside town? Zero down on eligible addresses, and more "
         "of East Texas qualifies than people think."),
        ("jumbo", "Jumbo",
         "Above the conforming limit. Each lender writes its own rules, which "
         "is exactly why we shop a network of them."),
    ]
    cards = "".join(
        S.loan_card(slug, nav, blurb, cls="reveal") for slug, nav, blurb in situations)

    body = f"""{S.hero(
        eyebrow='<span data-fb-kicker>Buying a home &middot; East Texas</span>',
        h1="Let&rsquo;s find <em>your</em> way in.",
        lede="Buying is its own path &mdash; nothing here is about refinancing. One "
             "question, one pick, and you're standing on the page built for exactly "
             "your situation.",
        variant="funnel",
        trail=[("/", "Home"), (None, "Buy a home")])}

<section class="dark"><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>First question</p>
<h2>Are you a veteran or service member?</h2>
<p class="sub">Or a surviving spouse. If yes, stop here &mdash; the VA loan is usually
the strongest option on the table, and most eligible people never use it.</p>
<div class="cta">
  <a class="btn shiny lg" href="/loans/va" data-funnel-cta="buy_va">YES &mdash; use my VA benefit &rarr;</a>
  <a class="btn onDark lg" href="#situations" data-funnel-cta="buy_notvet">No &mdash; keep going &darr;</a>
</div>
</div></section>

<section id="situations"><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Pick your situation</p>
<h2>Which one sounds like you?</h2>
<p class="sub">Every card opens a page with its own live estimator. Not sure? Skip
ahead to the dials below and we'll sort the program out together.</p>
<div class="lgrid">{cards}</div>
</div></section>

{S.funnel_rig("buy", "purchase",
    "Not sure which? Start with the payment.",
    "Dial in a price and a down payment &mdash; including zero &mdash; and see the "
    "monthly shape of it. The program question is our job, not yours.")}

{S.funnel_yes("buy", "purchase")}

{S.cta_band(
    head="Rather just talk it through?",
    sub="Five minutes with a licensed loan officer beats an hour of reading. No hard "
        "credit pull to start.",
    primary=("tel:" + S.PHONE_HREF, "Call " + S.PHONE),
    secondary=("/contact", "Send a question instead"))}
"""
    return S.page(
        path="/buy",
        title="Buy a Home in East Texas | Greenlight Mortgage — Longview, TX",
        desc="Buying a home in Longview or East Texas? One question and one pick puts "
             "you on the right loan path — VA, FHA, USDA, conventional or jumbo — with "
             "a live payment estimator. Powered by Co/LAB Lending. Equal Housing "
             "Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/buy", "Buy a home")],
        scripts=S.FUNNEL_SCRIPTS,
    )


# ==========================================================================
# ABOUT
# ==========================================================================

def about():
    # Real names from KT. No titles or NMLS numbers came with them, so none are
    # shown — see the TEAM comment in sitegen.py for why guessing either one is
    # worse than leaving a visible gap on a mortgage broker's team page.
    def person(p):
        if p.get("photo"):
            img = f'<img src="{p["photo"]}" alt="{S.esc(p["name"])}" width="104" height="104">'
        else:
            initials = "".join(w[0] for w in p["name"].split()[:2]).upper()
            img = f'<div class="ph" aria-hidden="true">{initials}</div>'

        role = (f'<p class="role">{S.esc(p["role"])}</p>' if p.get("role")
                else '<p class="role pending">Role to be confirmed</p>')
        nmls = (f'<p class="nmls">NMLS #{p["nmls"]}</p>' if p.get("nmls")
                else '<p class="nmls pending">NMLS # to be confirmed</p>')
        note = f'<p>{S.esc(p["note"])}</p>' if p.get("note") else ""
        cls = "person" if p.get("confirmed") else "person unconfirmed"
        return f'<div class="{cls}">{img}<h3>{S.esc(p["name"])}</h3>{role}{nmls}{note}</div>'

    cards = "".join(person(p) for p in S.TEAM)
    pending = "".join(
        f'<li><strong>{S.esc(n)}</strong> &mdash; {S.esc(why)}</li>'
        for n, why in S.PENDING_LICENSES)

    body = f"""{S.hero(
        eyebrow="About Greenlight",
        h1="Built around one question",
        lede="&ldquo;How can we be better, how can we be different?&rdquo; Kenneth Travis "
             "started Greenlight Mortgage in 2008 with that question and has run it that way "
             "since.",
        ctas=[("/contact", "Talk to us", "go"), ("/reviews", "Read our reviews", "ghost")],
        trail=[("/", "Home"), (None, "About")])}

<section><div class="wrap">
<div class="locard">
  <img src="/assets/from-old-site/kenneth-travis-headshot.png"
       alt="Kenneth Travis, President and CEO of Greenlight Mortgage" width="168" height="168">
  <div>
    <h3>Kenneth Travis</h3>
    <p class="role">President &amp; CEO &middot; Loan Originator NMLS #{S.NMLS_KT}</p>
    <p class="meta">Eight years in the United States Marine Corps, discharged as a Sergeant.
    Founded {S.COMPANY} in 2008. Working out of the office on Judson Road in Longview.</p>
    <p class="meta"><a href="tel:{S.PHONE_HREF}">{S.PHONE}</a></p>
    <p class="tag">&ldquo;{S.TAGLINE}&rdquo;</p>
  </div>
</div>
</div></section>

<section class="dark"><div class="wrap">
<div class="split">
<div class="reveal">
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>The company</p>
  <h2>A brokerage, on purpose.</h2>
  <p class="sub">Greenlight is a mortgage brokerage, powered by Co/LAB Lending. That is a
  deliberate structure, not a technicality. A bank employs loan officers to sell that bank's
  products. A brokerage takes your file to a network of lenders and is free to recommend
  whichever one serves you best.</p>
  <p class="sub">It also means we can say no to a loan. If refinancing will not pay for
  itself before you move, or if the program you asked about costs more than one you have not
  heard of, you will hear that from us.</p>
</div>
<div class="reveal">
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Core values</p>
  <div class="grid g2" style="margin-top:0">
    <div class="card"><span class="num">01</span><h3>Service &amp; Compassion</h3>
    <p>Treat each borrower like a member of the family. We are here to serve clients,
    employees and community.</p></div>
    <div class="card"><span class="num">02</span><h3>Operational Excellence</h3>
    <p>Continually improving, constantly exceeding standards, reviewing the process so the
    experience holds up.</p></div>
    <div class="card"><span class="num">03</span><h3>Trust &amp; Integrity</h3>
    <p>Lasting relationships built on transparent communication. Doing the right thing, 100%
    of the time.</p></div>
    <div class="card"><span class="num">04</span><h3>Green means GO!</h3>
    <p>You should know exactly what you are driving into before the light turns green.</p></div>
  </div>
</div>
</div>
</div></section>

<section><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Meet the team</p>
<h2>The people who will actually answer.</h2>
<p class="sub">Everyone below works here. What is not yet shown is each person's job title
and, where they hold one, their individual NMLS number &mdash; those are being confirmed
rather than guessed at.</p>

<div class="team">{cards}</div>

<div class="callout">
  <h3><span class="todo">Build note</span> &mdash; titles and NMLS numbers outstanding</h3>
  <p>On a mortgage site a name shown beside an NMLS number reads as &ldquo;this person is a
  licensed loan originator.&rdquo; Inventing a title would either manufacture a license that
  does not exist or quietly remove one from somebody who has it, so every unconfirmed field
  is left visibly blank. Send titles, NMLS numbers where applicable, photos, and Lisa's
  surname, and these fill in on the next build. KT also noted there are likely more people
  than the seven here.</p>
</div>
</div></section>

<section class="alt"><div class="wrap">
<div class="split">
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Where to find us</p>
  <h2>4523 Judson Road, Longview.</h2>
  <p class="sub">{S.COMPANY}<br>{S.STREET}<br>{S.CITY}, {S.STATE} {S.ZIP}</p>
  <p class="sub"><a href="tel:{S.PHONE_HREF}" style="color:var(--g);font-weight:650">{S.PHONE}</a></p>
  <div class="cta"><a class="btn" href="/contact">Send us a message</a></div>
</div>
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Licensed in</p>
  <ul class="ticks">
    {"".join(f"<li><strong>{n}</strong> &mdash; license {num}</li>" for n, num in S.LICENSES)}
  </ul>
  <p class="disclose">Company NMLS #{S.NMLS_CO}. Kenneth Travis, loan originator,
  NMLS #{S.NMLS_KT}. Verify either at nmlsconsumeraccess.org.</p>
  <div class="callout">
    <h3><span class="todo">Build note</span> &mdash; state not yet advertised</h3>
    <ul style="margin:10px 0 0 20px">{pending}</ul>
    <p style="margin-top:12px">Held back rather than published. Advertising a license the
    company does not hold is a licensing problem; omitting one it does hold costs a line of
    copy until someone checks.</p>
  </div>
</div>
</div>
</div></section>

{S.cta_band(head="Come talk to a person.",
            sub="No script, no hard credit pull, and no obligation on either side.",
            primary=("/contact", "Contact the team"),
            secondary=("/tools/estimate", "Or run the numbers first"))}
"""
    return S.page(
        path="/about",
        title="About Greenlight Mortgage | Meet the Team — Longview, TX",
        desc="Greenlight Mortgage was founded in Longview, Texas in 2008 by Kenneth Travis, "
             "USMC veteran and mortgage broker. Powered by Co/LAB Lending. Equal Housing "
             "Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/about", "About")],
    )


# ==========================================================================
# TESTIMONIALS + REVIEWS
# ==========================================================================

def testimonials():
    quotes = "".join(S.review_card(r) for r in S.REVIEWS)

    body = f"""{S.hero(
        eyebrow="Client testimonials",
        h1="In their words, not ours",
        lede="Seven clients from around East Texas. Carried over verbatim from the previous "
             "site &mdash; we have not edited, shortened, or tidied them up.",
        trail=[("/", "Home"), (None, "Testimonials")])}

<section><div class="wrap">
<div class="tgrid">{quotes}</div>
<p class="disclose">Testimonials reflect the individual experience of these clients and are
not a guarantee of any particular outcome, loan approval, rate or term. Every loan is subject
to credit approval and underwriting.</p>
</div></section>

<section class="alt"><div class="wrap">
<div class="narrow">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Worked with us?</p>
<h2>Tell us how it went.</h2>
<p class="sub">Good or bad. If something went wrong we would rather hear it from you than
read it later.</p>

<form class="reveal" data-glm-form="testimonial" style="margin-top:32px" novalidate>
  <div class="frow">
    <div class="field"><label for="t-name">Your name</label>
      <input id="t-name" name="name" type="text" autocomplete="name" required maxlength="120">
      <p class="err">Please tell us your name.</p></div>
    <div class="field"><label for="t-town">Town</label>
      <input id="t-town" name="town" type="text" placeholder="Longview, TX" maxlength="80"></div>
  </div>
  <div class="field"><label for="t-email">Email</label>
    <input id="t-email" name="email" type="email" autocomplete="email" required maxlength="254">
    <p class="help">So we can check it is really you before we publish anything.</p>
    <p class="err">Please enter a valid email address.</p></div>
  <div class="field"><label for="t-body">What happened?</label>
    <textarea id="t-body" name="message" rows="6" required maxlength="4000"></textarea>
    <p class="err">Please tell us a little about your experience.</p></div>
  <div class="consent">
    <input type="checkbox" id="t-pub" name="publish_ok" value="yes">
    <label for="t-pub">You may publish this on the Greenlight Mortgage website with my first
    name and town. I can ask you to take it down at any time.</label>
  </div>
  <div class="cta"><button class="btn go" type="submit">Send it</button></div>
  <p class="formstatus" role="status" aria-live="polite"></p>
</form>
</div>
</div></section>

{S.cta_band()}
"""
    return S.page(
        path="/testimonials",
        title="Client Testimonials | Greenlight Mortgage — Longview, TX",
        desc="What Greenlight Mortgage clients across Longview, Gilmer and Jefferson say "
             "about working with Kenneth Travis and the team. Powered by Co/LAB Lending. "
             "Equal Housing Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/testimonials", "Testimonials")],
        scripts='<script src="/forms.js" defer></script>',
    )


def reviews():
    def plat(pr):
        if pr["verified"]:
            score = (f'<p class="score">{pr["rating"]}</p>'
                     f'<p class="of">out of 5 &middot; {pr["count"]} reviews'
                     f'<br>read {pr["checked"]}</p>')
            link = (f'<span class="go">Read them on {S.esc(pr["platform"])} &nearr;</span>')
            return (f'<a class="plat" href="{pr["url"]}" rel="nofollow noopener" '
                    f'target="_blank">{score}<h3>{S.esc(pr["platform"])}</h3>'
                    f'<p>{S.esc(pr["note"])}</p>{link}</a>')
        return (f'<div class="plat unconfirmed"><p class="score">&mdash;</p>'
                f'<p class="of"><span class="todo">not yet confirmed</span></p>'
                f'<h3>{S.esc(pr["platform"])}</h3><p>{S.esc(pr["note"])}</p></div>')

    cards = "".join(plat(pr) for pr in S.REVIEW_PROFILES)
    quotes = "".join(S.review_card(r) for r in S.REVIEWS[:3])

    body = f"""{S.hero(
        eyebrow="Reviews",
        h1="Read us somewhere we cannot edit",
        lede="Testimonials we choose and publish ourselves are, in the end, testimonials we "
             "chose. These are the places you can read about Greenlight on a page we do not "
             "control &mdash; with the rating, the count, and the date we last checked it.",
        ctas=[("/testimonials", "Or read the ones on this site", "ghost")],
        trail=[("/", "Home"), (None, "Reviews")])}

<section><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Independent profiles</p>
<h2>Where the reviews actually live.</h2>
<p class="sub">Ratings move. Each card shows the date we read it, and every link goes
straight to the source so you can check the current number yourself.</p>
<div class="grid g3">{cards}</div>
<p class="disclose">Star ratings and review counts are those published by each platform on the
date shown and will have changed since. We do not control, moderate, or select which reviews
appear on any of these sites. Individual experiences vary and are not a guarantee of any
particular outcome, loan approval, rate or term.</p>
</div></section>

<section class="dark"><div class="wrap">
<div class="split">
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>How we handle reviews</p>
  <h2>If we cannot source it, we say so.</h2>
  <p class="sub">Every review on this site carries where it came from. Where the exact wording
  has been read from a page we can link you to, it says <em>verified</em> and links there.
  Where it was carried across from our previous website and has not been re-checked
  word-for-word, it says that instead.</p>
  <p class="sub">That is a deliberately unflattering thing to publish. It is also the only
  version of a review page worth trusting.</p>
</div>
<div>
  <div class="callout">
    <h3><span class="todo">Open</span> &mdash; three profiles to confirm</h3>
    <p>A Zillow lender profile was found in search but could not be confirmed as Greenlight's.
    The Google Business Profile and Facebook review URLs have not been supplied. None of the
    three link out from this page until KT confirms them.</p>
  </div>
  <div class="callout">
    <h3><span class="todo">Open</span> &mdash; address mismatch</h3>
    <p>The Birdeye listing shows <strong>1328 Heritage Blvd</strong>, not
    <strong>{S.STREET}</strong>. One of the two is out of date. Beyond the confusion for a
    client trying to find the office, inconsistent address data across listings measurably
    hurts local search &mdash; and this domain ranks #2 for &ldquo;mortgage longview tx.&rdquo;</p>
  </div>
</div>
</div>
</div></section>

<section><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>On this site</p>
<h2>A few of them.</h2>
<div class="tgrid">{quotes}</div>
<div class="cta"><a class="btn go" href="/testimonials">Read all of them {ARROW}</a></div>
</div></section>

{S.cta_band(head="Rather just talk to someone?",
            sub="Ask us anything. No obligation and no hard credit pull to begin.",
            primary=("/contact", "Contact us"),
            secondary=("/tools/estimate", "See what you could save"))}
"""
    return S.page(
        path="/reviews",
        title="Reviews | Greenlight Mortgage — Longview, TX",
        desc="Independent reviews of Greenlight Mortgage in Longview, Texas on "
             "Experience.com and Birdeye, plus client testimonials with their sources shown. "
             "Powered by Co/LAB Lending. Equal Housing Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/reviews", "Reviews")],
    )


# ==========================================================================
# CONTACT
# ==========================================================================

def contact():
    body = f"""{S.hero(
        eyebrow="Contact",
        h1="Talk to a person",
        lede="Call, email, or send the form. Whichever you pick, a real person from the "
             "Longview office answers &mdash; and we tell you what happens next.",
        trail=[("/", "Home"), (None, "Contact")])}

<section><div class="wrap">
<div class="split">
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Send a message</p>
  <h2>What is on your mind?</h2>
  <p class="sub">No script and no obligation. If we are not the right fit we will say so.</p>

  <form data-glm-form="contact" style="margin-top:30px" novalidate>
    <div class="frow">
      <div class="field"><label for="c-name">Name</label>
        <input id="c-name" name="name" type="text" autocomplete="name" required maxlength="120">
        <p class="err">Please tell us your name.</p></div>
      <div class="field"><label for="c-phone">Phone <span style="font-weight:450;color:var(--mut)">(optional)</span></label>
        <input id="c-phone" name="phone" type="tel" autocomplete="tel" maxlength="32"></div>
    </div>
    <div class="field"><label for="c-email">Email</label>
      <input id="c-email" name="email" type="email" autocomplete="email" required maxlength="254">
      <p class="err">Please enter a valid email address.</p></div>
    <div class="field"><label for="c-goal">What are you trying to do?</label>
      <select id="c-goal" name="goal">
        <option value="">Choose one…</option>
        <option>Buy a home</option>
        <option>Refinance the one I have</option>
        <option>Find out if I qualify</option>
        <option>Ask about my VA benefit</option>
        <option>Something else</option>
      </select></div>
    <div class="field"><label for="c-msg">Message</label>
      <textarea id="c-msg" name="message" rows="5" maxlength="4000"></textarea></div>

    <div class="consent">
      <input type="checkbox" id="c-tcpa" name="tcpa_consent" value="yes">
      <label for="c-tcpa">{TCPA_TEXT}</label>
    </div>
    <p class="disclose">Leave the box unticked and we will only reply by email. You will still
    get an answer.</p>

    <div class="cta"><button class="btn go" type="submit">Send message</button></div>
    <p class="formstatus" role="status" aria-live="polite"></p>
  </form>
</div>

<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>The office</p>
  <h2>4523 Judson Road</h2>
  <p class="sub">{S.CITY}, {S.STATE} {S.ZIP}</p>
  <div class="grid g2" style="margin-top:26px">
    <div class="card"><h3>Call</h3><p><a href="tel:{S.PHONE_HREF}"
      style="color:var(--g);font-weight:700;font-size:19px">{S.PHONE}</a></p></div>
    <div class="card"><h3>Apply</h3><p>Applications are handled on our licensed origination
      system.</p><p style="margin-top:10px"><a href="{A}"
      style="color:var(--g);font-weight:650">Start an application {ARROW}</a></p></div>
  </div>

  <div class="callout">
    <h3>What happens after you send this</h3>
    <p>It goes straight into our system &mdash; not to one person's inbox where it can sit.
    A licensed loan officer replies within one business day. Once. We are not going to call
    you six times in an hour.</p>
  </div>

  <div class="callout">
    <h3><span class="todo">Build note</span> — office hours not confirmed</h3>
    <p>Opening hours were not captured in the migration and have not been invented. Kenneth
    confirms them and they go here and into the MortgageBroker schema.</p>
  </div>

  <p class="disclose">Please do not send Social Security numbers, account numbers or income
  documents through this form. When it is time for those, your loan officer will send you a
  secure link.</p>
</div>
</div>
</div></section>
"""
    return S.page(
        path="/contact",
        title="Contact Greenlight Mortgage | Longview, TX — 903-331-0892",
        desc="Contact Greenlight Mortgage at 4523 Judson Rd, Longview, TX 75605 or call "
             "903-331-0892. A licensed loan officer replies within one business day. Powered "
             "by Co/LAB Lending. Equal Housing Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/contact", "Contact")],
        scripts='<script src="/forms.js" defer></script>',
    )


TCPA_TEXT = S.TCPA_TEXT   # single source of truth lives in sitegen.py


# ==========================================================================
# LEARNING CENTER / RESOURCES
# ==========================================================================

def learn():
    import importlib.util as _il
    _spec = _il.spec_from_file_location("bg", os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "build-guides.py"))
    _bg = _il.module_from_spec(_spec); _spec.loader.exec_module(_bg)

    cards = "".join(
        f'<a class="lcard reveal" href="/learn/{a["slug"]}" style="--accent:#0f7a4d">'
        f'<span class="lmark">{ICONS[a["icon"]]}</span>'
        f'<h3>{S.esc(a["title"])}</h3><p>{S.esc(a["blurb"])}</p>'
        f'<span class="go">Read it {ARROW}</span></a>'
        for a in _bg.ARTICLES)

    body = f"""{S.hero(
        eyebrow="Learning Center",
        h1="The parts nobody explains",
        lede="Plain-English explanations of the things that decide whether a mortgage works "
             "for you &mdash; written for people buying a house, not for people in the "
             "industry.",
        ctas=[("/tools/estimate", "See what you could save", "go"),
              ("/resources", "Practical resources", "ghost")],
        trail=[("/", "Home"), (None, "Learning Center")])}

<section><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Topics</p>
<h2>Start wherever you are stuck.</h2>
<div class="grid g3">{cards}</div>

<div class="callout">
  <h3><span class="todo">Build note</span> — articles pending</h3>
  <p>These six topics are the planned structure, drawn from the questions the office actually
  gets asked. The full articles have not been written yet, and the 557-video YouTube library
  is the intended source for most of them. Nothing here links to a page that does not exist.</p>
</div>
</div></section>

<section class="alt"><div class="wrap">
<div class="split">
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Ask directly</p>
  <h2>Or just ask us the question.</h2>
  <p class="sub">Every article on this site exists because somebody phoned and asked. If
  yours is not here, that is what the phone is for.</p>
  <div class="cta"><a class="btn" href="/contact">Ask a question</a>
  <a class="btn ghost" href="tel:{S.PHONE_HREF}">{S.PHONE}</a></div>
</div>
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Common starting points</p>
  <ul class="ticks">
    <li><a href="/loans/va" style="color:var(--g)">VA loans</a> &mdash; if you served, start here</li>
    <li><a href="/loans/usda" style="color:var(--g)">USDA</a> &mdash; check the address before you rule it out</li>
    <li><a href="/loans/fha" style="color:var(--g)">FHA</a> &mdash; if credit is recovering</li>
    <li><a href="/tools/calculator" style="color:var(--g)">The calculator</a> &mdash; if you just want a number</li>
  </ul>
</div>
</div>
</div></section>

{S.cta_band()}
"""
    return S.page(
        path="/learn",
        title="Learning Center | Greenlight Mortgage — Longview, TX",
        desc="Plain-English mortgage explanations from Greenlight Mortgage in Longview, Texas "
             "— underwriting, down payments, closing costs, VA benefits and credit. Powered "
             "by Co/LAB Lending. Equal Housing Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/learn", "Learning Center")],
    )


def resources():
    body = f"""{S.hero(
        eyebrow="Resources",
        h1="Things that are actually useful",
        lede="Tools, checklists and the handful of outside links worth having when you are "
             "buying or refinancing in East Texas.",
        trail=[("/", "Home"), (None, "Resources")])}

<section><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Our tools</p>
<h2>Free, and none of them need your phone number.</h2>
<p class="sub">With one exception, and we tell you about it before you start.</p>
<div class="lgrid">
  <a class="lcard" href="/tools/calculator"><h3>Mortgage calculator</h3>
  <p>Payment breakdown, a full amortization schedule, and what an extra payment each month
  actually does to the term. Nothing gated.</p>
  <span class="go">Open the calculator {ARROW}</span></a>
  <a class="lcard" href="/tools/estimate"><h3>Estimated Savings</h3>
  <p>Six questions, about two minutes, and a real number for what a refinance could save you.
  This one asks for your name, email and phone at the end &mdash; that is the trade.</p>
  <span class="go">See what you could save {ARROW}</span></a>
  <a class="lcard" href="/tools/home-value"><h3>Home value report</h3>
  <p>A local estimate on your address, put together by someone who works this market rather
  than an algorithm that has never been to Longview.</p>
  <span class="go">Request a report {ARROW}</span></a>
</div>
</div></section>

<section class="alt"><div class="wrap">
<div class="split">
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Worth bookmarking</p>
  <h2>Outside links we trust.</h2>
  <ul class="ticks">
    <li><a href="https://www.nmlsconsumeraccess.org" style="color:var(--g)">NMLS Consumer
    Access</a> &mdash; verify any loan officer, including ours. Ours is #{S.NMLS_KT}.</li>
    <li><a href="https://www.consumerfinance.gov/owning-a-home/" style="color:var(--g)">CFPB
    Owning a Home</a> &mdash; the federal consumer bureau's own buying guide. Neutral, and
    genuinely good.</li>
    <li><a href="https://www.va.gov/housing-assistance/home-loans/" style="color:var(--g)">VA
    home loan benefits</a> &mdash; straight from the source, including how to request your
    Certificate of Eligibility.</li>
    <li><a href="https://www.sml.texas.gov" style="color:var(--g)">Texas Department of Savings
    and Mortgage Lending</a> &mdash; the state regulator, and where complaints go.</li>
  </ul>
</div>
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Before you start looking</p>
  <div class="steps">
    <div class="step"><h3>Get a real number first</h3><p>Knowing your range before you fall in
    love with a house is the difference between a calm search and a stressful one.</p></div>
    <div class="step"><h3>Do not open new credit</h3><p>New accounts and big balance changes in
    the sixty days before you apply can move your pricing.</p></div>
    <div class="step"><h3>Keep your documents together</h3><p>Two years of tax returns, recent
    pay stubs, and two months of bank statements covers most of it.</p></div>
  </div>
</div>
</div>

<div class="callout">
  <h3><span class="todo">Build note</span> — downloadable guides pending</h3>
  <p>The migration notes mention resource PDFs on the old site. None were recovered before the
  domain work started, so no downloads are linked here. If they still exist on the vendor's
  multisite they should be pulled before the domain flips &mdash; that is the one
  irreversible step in this project.</p>
</div>
</div></section>

{S.cta_band()}
"""
    return S.page(
        path="/resources",
        title="Home Buying Resources | Greenlight Mortgage — Longview, TX",
        desc="Free mortgage tools, checklists and trusted outside links for buyers and "
             "homeowners in Longview and East Texas. Powered by Co/LAB Lending. Equal Housing "
             "Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/resources", "Resources")],
    )


# ==========================================================================
# BLOG
# ==========================================================================

# Original copy written for this build to exercise the post template end-to-end.
# It states no figure specific to Greenlight and makes no rate or approval claim.
# ⚠️ KT should read it before it stays up — it is our words in his voice.
POSTS = [
    dict(
        slug="the-20-percent-down-payment-myth",
        date="2026-08-01",
        dateline="1 August 2026",
        tag="Buying a home",
        title="The 20% down payment myth is costing East Texas buyers years",
        desc="You probably do not need 20% down to buy a house in Longview. Where the number "
             "came from, what it actually does, and how to work out whether waiting is costing "
             "you more than it saves.",
        lede="It is the single most expensive misunderstanding in this business, and almost "
             "everybody arrives with it.",
        sections=[
            ("Where the number came from", [
                "Twenty percent is the threshold above which a conventional loan generally does "
                "not require private mortgage insurance. That is the whole origin of it. It was "
                "never a minimum to buy a house &mdash; it is the point at which one particular "
                "cost falls away on one particular kind of loan.",
                "Somewhere along the way that turned into folk wisdom, and now people who could "
                "have bought three years ago are still saving.",
            ]),
            ("What is actually available", [
                "Qualifying first-time buyers can see conventional programs starting far below "
                "twenty percent. FHA is built around a lower down payment and more forgiving "
                "credit. VA, for an eligible veteran, frequently requires no down payment at all "
                "and carries no monthly mortgage insurance. USDA can be zero down on an eligible "
                "rural address &mdash; and a great deal more of the area around Longview qualifies "
                "than people assume, because eligibility is set by specific address rather than by "
                "town or county.",
                "Whether any of these is available to you depends on your credit, your income, the "
                "property, and current guidelines. That is a conversation with a licensed loan "
                "officer, not something a website can tell you.",
            ]),
            ("The question worth actually asking", [
                "Not &ldquo;how do I avoid mortgage insurance,&rdquo; but &ldquo;what does waiting "
                "cost me?&rdquo; Those are different questions and people almost always ask the "
                "first one.",
                "Waiting has three costs that rarely get counted. You keep paying rent, which "
                "builds equity for somebody else. You miss whatever the house appreciates in the "
                "meantime, and in a market where prices are moving, the target moves faster than "
                "most people can save. And you are betting that rates will not move against you, "
                "which is a bet nobody can win reliably.",
                "Against that, mortgage insurance is a monthly cost that, on a conventional loan, "
                "comes off once you have built enough equity. Sometimes the math says wait. "
                "Frequently it says the opposite. It is arithmetic, and it is specific to you.",
            ]),
            ("What we would rather you did", [
                "Find out where you actually stand before you decide to wait. It costs nothing, "
                "there is no hard credit pull to start the conversation, and you may discover the "
                "thing you have been saving toward was never required.",
                "And if the answer genuinely is that waiting serves you better, we will say so. "
                "We are brokers &mdash; we are not paid to push you toward one answer.",
            ]),
        ],
        embed=dict(program="conventional", mode="purchase", after=2,
                   h2="Try it: what does YOUR down payment actually change?",
                   sub="Drag the down payment dial and watch the monthly number. Most "
                       "people are surprised how small the gap is between 5% and 20% "
                       "&mdash; and how many years of rent the difference costs.",
                   down=(3, 30, 5, 0.5)),
        funnel=("conventional", "Conventional loans",
                "The standard route, and often the lowest total cost once you qualify. "
                "The 20% rule is a myth — here's what's real."),
    ),

    dict(
        slug="va-irrrl-streamline-refinance-veterans",
        date="2026-08-05",
        dateline="5 August 2026",
        tag="Veterans",
        title="The VA refinance most East Texas veterans have never used: the IRRRL",
        desc="The VA's streamline refinance — usually no appraisal, far less paperwork, "
             "and a federal rule that forces the math to work in your favor. What the "
             "IRRRL is, who qualifies, and the disability-rating detail nobody asks about.",
        lede="The VA built a refinance so streamlined they gave it its own word. Most of "
             "the veterans it was built for have never heard it.",
        sections=[
            ("What an IRRRL actually is", [
                "Interest Rate Reduction Refinance Loan. It exists for exactly one "
                "situation: you already hold a VA loan, and a lower cost is available. "
                "No cash out, no equity games &mdash; the same loan at a lower cost.",
                "Because the VA already knows the loan and you have already proven "
                "yourself on it, the process skips most of the obstacle course. Usually "
                "no appraisal. Usually no new certificate of eligibility. Far less "
                "credit paperwork than a full refinance. Clean files have closed in as "
                "little as eight business days &mdash; every file sets its own pace, but "
                "&ldquo;streamline&rdquo; is the VA's word for it, not ours.",
            ]),
            ("The six-month box", [
                "The biggest qualification question is one you can answer right now: "
                "have you paid your VA loan on time for the last six months? If yes, "
                "the biggest box is already checked.",
                "That is the whole spirit of the program. You proved yourself on the "
                "loan you have. The VA's position is that you should not have to "
                "re-audition to keep more of your own money.",
            ]),
            ("The rule that protects you", [
                "VA requires the costs of an IRRRL to be recovered by the monthly "
                "saving within 36 months, and the refinance to produce a real net "
                "tangible benefit. If a file does not clear that test, the loan "
                "cannot be written &mdash; full stop.",
                "That rule exists because streamline refinances are easy to sell and "
                "easy to abuse. We run it first, and if your file fails it, we tell "
                "you that for free instead of after somebody pulled your credit.",
            ]),
            ("The 10% detail nobody asks about", [
                "There is a one-time VA funding fee on an IRRRL &mdash; half a percent "
                "of the loan. It is waived entirely for veterans with a "
                "service-connected disability rating of 10% or higher.",
                "On a $250,000 balance that is $1,250 of cost that simply disappears, "
                "and it regularly flips a marginal file into a clear win. If you are "
                "rated and nobody has asked you about it, they have not run your "
                "numbers properly.",
            ]),
        ],
        embed=dict(program="va-irrrl", mode="refi", after=2,
                   h2="Try it: what would a streamline change monthly?",
                   sub="Set the dials to what you pay now. The green number is the "
                       "monthly difference &mdash; an estimate to start a real "
                       "conversation, not the end of one."),
        funnel=("va-irrrl", "VA IRRRL",
                "The full page: the live 36-month test, how the process runs, and the "
                "fastest way to get your real numbers."),
    ),

    dict(
        slug="zero-down-usda-loans-east-texas",
        date="2026-08-05",
        dateline="5 August 2026",
        tag="Buying a home",
        title="Zero down around Longview: the USDA map is bigger than you think",
        desc="USDA loans put people in homes around Gilmer, Hallsville, White Oak, Diana "
             "and Ore City with no down payment. How eligibility actually works, the "
             "income limits, and why you should check the address before you assume.",
        lede="One of exactly two zero-down loans in America does not require military "
             "service. It requires the right address — and East Texas has a lot of them.",
        sections=[
            ("The most overlooked program in the region", [
                "USDA rural development loans finance eligible homes with zero down "
                "payment. Not low. Zero. And the word &ldquo;rural&rdquo; does a lot of "
                "quiet damage here, because people picture forty acres and a tractor "
                "and rule themselves out from the couch.",
                "The map is drawn address by address, not by town or county &mdash; and "
                "communities just outside Longview qualify constantly. Gilmer, "
                "Hallsville, White Oak, Diana, Ore City, Jefferson &mdash; homes around "
                "all of them regularly fit.",
            ]),
            ("Two things have to line up", [
                "First, the property address has to sit inside the current USDA map. "
                "Second, your household income has to fit the limit for the area and "
                "your family size. Both are checkable in minutes, and both change "
                "periodically &mdash; which is why the answer is checking, not "
                "assuming.",
                "If either one misses, USDA is off the table and we will tell you what "
                "does fit instead. If both line up, the down payment conversation is "
                "over before it starts.",
            ]),
            ("What zero down does and does not mean", [
                "It means the purchase price is fully financed. It does not mean the "
                "transaction is free &mdash; closing costs still exist, though there "
                "are legitimate ways to handle them, including seller contributions.",
                "What it changes is the timeline. The five years you were going to "
                "spend saving a down payment can become this year, in a house, "
                "building your own equity instead of a landlord's.",
            ]),
        ],
        embed=dict(program="usda", mode="purchase", after=1,
                   h2="Try it: what does zero-down cost monthly?",
                   sub="Leave the down payment dial on zero &mdash; that's the program. "
                       "The number is principal and interest on a sample figure.",
                   down=(0, 20, 0, 0.5)),
        funnel=("usda", "USDA loans",
                "The full page: the town picker, the income-limit reality, and the "
                "two-minute address check."),
    ),

    dict(
        slug="fha-loans-rebuilding-credit-longview",
        date="2026-08-05",
        dateline="5 August 2026",
        tag="Buying a home",
        title="Rebuilding credit? FHA was built for exactly that",
        desc="FHA loans exist for real people with real credit histories — 3.5% down for "
             "qualifying buyers, gift funds allowed, and guidelines more forgiving than "
             "conventional. What actually matters and why one lender's no is not the answer.",
        lede="Perfect credit is not a requirement to buy a house in East Texas. It never "
             "was. That is the entire reason FHA exists.",
        sections=[
            ("The point of the program", [
                "FHA was created for buyers the conventional box does not fit &mdash; "
                "thinner savings, credit still healing from a rough stretch, a file "
                "with a story in it. Lower down payment, more forgiving guidelines, "
                "and the most common first step into a first house in this market.",
                "It is not a consolation prize. For plenty of files it is genuinely "
                "the better deal, and a broker who says otherwise without running "
                "both is guessing.",
            ]),
            ("What underwriting actually cares about", [
                "Less than you fear, more than you hope. Payment history and how much "
                "of your available credit you are using carry most of the weight. A "
                "rough patch two years ago with clean payments since reads very "
                "differently from chaos last month.",
                "And the down payment can come from an eligible gift &mdash; family "
                "helping with the 3.5% is normal, documented, and allowed.",
            ]),
            ("One lender's no is one data point", [
                "FHA sets the floor, but individual lenders stack their own "
                "requirements on top &mdash; overlays, in the jargon. That means the "
                "same file gets declined at one desk and approved at another, every "
                "single week.",
                "This is precisely where a broker earns their keep. We already know "
                "which lenders are comfortable with which files, and we shop yours "
                "instead of letting one bank's overlay be the final word.",
            ]),
        ],
        embed=dict(program="fha", mode="purchase", after=1,
                   h2="Try it: what would the payment be?",
                   sub="The down payment dial starts at 3.5% &mdash; FHA's floor for "
                       "qualifying buyers. Principal and interest on a sample figure.",
                   down=(3.5, 25, 3.5, 0.5)),
        funnel=("fha", "FHA loans",
                "The full page: what the credit conversation really looks like, and "
                "the fastest way to find out where you stand."),
    ),

    dict(
        slug="refinance-break-even-math",
        date="2026-08-05",
        dateline="5 August 2026",
        tag="Refinancing",
        title="When refinancing is a bad idea — and how to know in five minutes",
        desc="Refinancing costs money, and it only pays if the savings outrun the costs "
             "before you move. The break-even test, the term-restart trap, and the three "
             "honest reasons to refinance a Longview mortgage.",
        lede="Half this business is telling people when NOT to do the thing we sell. "
             "Here is that math, in the open.",
        sections=[
            ("Three honest reasons to refinance", [
                "A lower payment. A shorter term. Getting rid of mortgage insurance. "
                "If none of those three is on the table, the conversation should end "
                "there &mdash; and with us, it does.",
                "Cash-out is its own animal: legitimate for the right purpose, "
                "expensive as a habit. Your balance goes up. That is the trade, and "
                "anyone who does not say so plainly is selling, not advising.",
            ]),
            ("The break-even test", [
                "Every refinance has costs. Divide them by the monthly saving and you "
                "get the number of months until the refinance has paid for itself. "
                "If you will still own the house past that month, the math works. If "
                "you might move before it, the refinance loses you money no matter "
                "how good the new payment feels.",
                "That is the entire test. The VA makes a version of it federal law on "
                "streamline refinances &mdash; costs must recoup within 36 months "
                "&mdash; and it is a standard worth applying to every refinance, not "
                "just VA ones.",
            ]),
            ("The term-restart trap", [
                "Stretching a balance back out to thirty years drops the monthly "
                "payment and can quietly raise the total cost by tens of thousands. "
                "A lower payment on a longer clock is not automatically a win.",
                "It is also avoidable: a refinance can keep your remaining term, or "
                "shorten it. Ask for both numbers &mdash; the new payment AND the "
                "total cost over the years you expect to hold the loan. We show "
                "both, unprompted.",
            ]),
        ],
        embed=dict(program="refinance", mode="refi", after=1,
                   h2="Try it: is there anything on the table?",
                   sub="Set the dials to your current loan. The number is the monthly "
                       "difference a refinance could make &mdash; the break-even math "
                       "comes next, and we run it with you."),
        funnel=("refinance", "Refinancing",
                "The full page: the live break-even meter, the honest cases for and "
                "against, and the fastest path to real numbers."),
    ),

    dict(
        slug="va-loan-benefit-worth-east-texas",
        date="2026-08-05",
        dateline="5 August 2026",
        tag="Veterans",
        title="You earned the VA loan. Here's what it's actually worth in East Texas.",
        desc="No down payment in many cases, no monthly mortgage insurance, reusable, and "
             "a funding fee that disappears at a 10% disability rating. What the VA home "
             "loan benefit really does for Longview-area veterans.",
        lede="A striking number of East Texas veterans qualify for the strongest loan "
             "program in the country and never find out.",
        sections=[
            ("What the benefit actually does", [
                "In many cases: no down payment. On every VA loan: no monthly mortgage "
                "insurance &mdash; the quiet cost that drags on FHA and low-down "
                "conventional loans for years. Over a full term, that second part is "
                "usually worth more than the first.",
                "It is also reusable. The benefit is not one-and-done; entitlement can "
                "often be restored or partially reused, even if you bought before.",
            ]),
            ("The funding fee, and the rating that removes it", [
                "There is a one-time VA funding fee. It is waived entirely for "
                "veterans with a service-connected disability rating of 10% or more. "
                "That single fact changes the math on a great many files, and it is "
                "the most commonly missed question in the whole process.",
                "If you are rated and your lender has not asked, your numbers have "
                "not been run properly. Ours asks first.",
            ]),
            ("The myth that costs veterans houses", [
                "Some sellers still believe VA offers are slow or fragile. That "
                "belief is mostly outdated &mdash; a VA loan closes on the same "
                "calendar as any other when the lender knows the program.",
                "It is a communication problem, not a loan problem, and handling it "
                "is your lender's job. We close VA files every week, and our team "
                "was built by a Marine. The seller conversation is ours to win, not "
                "yours to dread.",
            ]),
        ],
        embed=dict(program="va", mode="purchase", after=1,
                   h2="Try it: the payment with nothing down",
                   sub="Start the down payment dial at zero &mdash; that's the point "
                       "of the benefit. Principal and interest on a sample figure.",
                   down=(0, 25, 0, 0.5)),
        funnel=("va", "VA loans",
                "The full page: eligibility, the funding-fee math, and what your "
                "entitlement is actually worth."),
    ),
]


def blog_index():
    postlist = "".join(
        f'<a class="post" href="/blog/{p["slug"]}">'
        f'<time datetime="{p["date"]}">{p["dateline"]}</time>'
        f'<div><h3>{S.esc(p["title"])}</h3><p>{S.esc(p["desc"])}</p>'
        f'<span class="tagline">{S.esc(p["tag"])}</span></div></a>'
        for p in POSTS)

    body = f"""{S.hero(
        eyebrow="Blog",
        h1="Notes from the Longview office",
        lede="What we are seeing in the East Texas market, and answers to the questions that "
             "keep coming up on the phone.",
        trail=[("/", "Home"), (None, "Blog")])}

<section><div class="wrap">
<div class="postlist">{postlist}</div>

<div class="callout">
  <h3><span class="todo">Build note</span> &mdash; eight WordPress posts still to migrate</h3>
  <p>Eight posts exist on the current WordPress site &mdash; one legacy article and seven from
  July &mdash; and they have not been migrated. They live on a vendor's multisite that
  Greenlight does not control, so they need pulling before the domain moves. The posts above
  were written for this build in Kenneth's voice, each with a live estimator inside it;
  Kenneth should read them before launch.</p>
</div>

<div class="split" style="margin-top:56px">
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>The plan</p>
  <h2>Feed it from the video library.</h2>
  <p class="sub">There are 557 videos already recorded, and the local ones pull between three
  and twelve thousand views. That is the content. It needs transcribing, editing into
  articles, and publishing on a schedule &mdash; not writing from scratch.</p>
</div>
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Why it matters</p>
  <p class="sub">About ten pages of the current site are indexed. Competitors are running
  fifty or more. The blog is the cheapest way to close that gap, and every post is another
  page that can rank for a Longview, Gilmer or Kilgore search.</p>
</div>
</div>
</div></section>

{S.cta_band(head="In the meantime, ask us directly.",
            sub="The articles exist to answer questions. You can skip ahead and just ask one.",
            primary=("/contact", "Ask a question"),
            secondary=("/learn", "Browse the Learning Center"))}
"""
    return S.page(
        path="/blog",
        title="Blog | Greenlight Mortgage — Longview, TX",
        desc="Mortgage and housing notes from Greenlight Mortgage in Longview, Texas. Powered "
             "by Co/LAB Lending. Equal Housing Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/blog", "Blog")],
    )


def blog_post(slug, title, desc, date, dateline, lede, sections, tag="Guide",
              embed=None, funnel=None):
    """The reusable post template.

    embed:  dict(program=<loan slug>, mode='refi'|'purchase', h2=..., sub=...,
                 after=<section index>, price=..., down=...) — drops the live
                 slider rig mid-post and the YES walk-through after the prose.
                 `program` is the loan the rig feeds, so the lead's loan_type
                 is meaningful; analytics rows carry the page path separately.
    funnel: (loan_slug, title, blurb) — the go-deeper card routing the reader
                 to that program's funnel page."""
    blocks = [f"<h2>{h}</h2>" + "".join(f"<p>{p}</p>" for p in ps)
              for h, ps in sections]

    schema = (
        '{"@context":"https://schema.org","@type":"Article","headline":%s,'
        '"datePublished":%s,"author":{"@type":"Organization","name":%s},'
        '"publisher":{"@type":"Organization","name":%s},"description":%s}'
    ) % (S.jstr(title), S.jstr(date), S.jstr(S.COMPANY), S.jstr(S.COMPANY), S.jstr(desc))

    disclose = ("""<p class="disclose">General information only. Nothing here is a commitment to lend, an offer
of credit, or a rate quote &mdash; those come from a licensed loan officer after a complete
application, and everything is subject to credit approval and underwriting.</p>""")

    godeeper = ""
    if funnel:
        fslug, ftitle, fblurb = funnel
        if fslug in S.LOAN_MARKS:
            card = S.loan_card(fslug, ftitle, S.esc(fblurb))
        else:
            card = (f'<a class="lcard" href="/loans/{fslug}" style="--accent:#8a6d1f">'
                    f'<h3>{S.esc(ftitle)}</h3><p>{S.esc(fblurb)}</p>'
                    f'<span class="go">Read more {ARROW}</span></a>')
        godeeper = f"""<section class="alt"><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Go deeper</p>
<h2>The page built for exactly this.</h2>
<div class="lgrid" style="max-width:560px">{card}</div>
</div></section>"""

    if embed:
        cut = embed.get("after", 1)
        rig = S.funnel_rig(
            embed["program"], embed["mode"], embed["h2"], embed["sub"],
            price=embed.get("price", (80000, 900000, 250000, 5000)),
            down=embed.get("down", (0, 25, 5, 0.5)))
        middle = f"""</div>
</div></section>

{rig}

<section><div class="wrap">
<div class="prose">"""
        inner = "".join(blocks[:cut]) + middle + "".join(blocks[cut:]) + disclose
        tail = S.funnel_yes(embed["program"], embed["mode"]) + godeeper
        scripts = S.FUNNEL_SCRIPTS
    else:
        inner = "".join(blocks) + disclose
        tail = godeeper + S.cta_band(
            head="Want this run against your actual numbers?",
            sub="Two minutes, no hard credit pull, and a real estimate on screen at the end.")
        scripts = ""

    body = f"""{S.hero(
        eyebrow=tag,
        h1=S.esc(title),
        lede=lede,
        trail=[("/", "Home"), ("/blog", "Blog"), (None, title)])}

<section><div class="wrap">
<div class="prose">
<p class="updated">Published {dateline} &middot; {S.SHORT}, Longview TX</p>
{inner}
</div>
</div></section>

{tail}
"""
    return S.page(
        path=f"/blog/{slug}",
        title=f"{title} | Greenlight Mortgage",
        desc=desc,
        body=body,
        trail=[("/", "Home"), ("/blog", "Blog"), (f"/blog/{slug}", title)],
        extra_schema=schema,
        scripts=scripts,
    )


# ==========================================================================
# SURVEY
# ==========================================================================

def survey():
    def scale(name, label):
        opts = "".join(
            f'<label class="choice"><input type="radio" name="{name}" value="{v}">'
            f'<span>{v}</span></label>' for v in range(1, 6))
        return (f'<fieldset class="field"><legend style="font-size:17px">{label}</legend>'
                f'<div class="choices" style="grid-template-columns:repeat(5,1fr)">{opts}</div>'
                f'</fieldset>')

    body = f"""{S.hero(
        eyebrow="Client survey",
        h1="How did we do?",
        lede="Two minutes, and it goes straight to Kenneth. If something went wrong we would "
             "much rather hear it here than read it somewhere else.",
        trail=[("/", "Home"), (None, "Survey")])}

<section><div class="wrap"><div class="narrow">
<form data-glm-form="survey" novalidate>
  <div class="frow">
    <div class="field"><label for="s-name">Your name</label>
      <input id="s-name" name="name" type="text" autocomplete="name" required maxlength="120">
      <p class="err">Please tell us your name.</p></div>
    <div class="field"><label for="s-email">Email</label>
      <input id="s-email" name="email" type="email" autocomplete="email" required maxlength="254">
      <p class="err">Please enter a valid email address.</p></div>
  </div>

  {scale("q_communication", "1 &mdash; How well did we keep you informed? (1 poor, 5 excellent)")}
  {scale("q_speed", "2 &mdash; How did the pace of the process feel?")}
  {scale("q_clarity", "3 &mdash; Were the costs and terms explained clearly?")}
  {scale("q_recommend", "4 &mdash; How likely are you to recommend us?")}

  <div class="field"><label for="s-best">What went well?</label>
    <textarea id="s-best" name="what_went_well" rows="4" maxlength="4000"></textarea></div>
  <div class="field"><label for="s-worst">What should we fix?</label>
    <textarea id="s-worst" name="what_to_fix" rows="4" maxlength="4000"></textarea>
    <p class="help">Be blunt. This is the useful box.</p></div>
  <div class="field"><label for="s-lo">Who did you work with? <span
    style="font-weight:450;color:var(--mut)">(optional)</span></label>
    <input id="s-lo" name="loan_officer" type="text" maxlength="120"></div>

  <div class="cta"><button class="btn go" type="submit">Send feedback</button></div>
  <p class="formstatus" role="status" aria-live="polite"></p>
</form>

<div class="callout">
  <h3><span class="todo">Build note</span> — confirm this is still in use</h3>
  <p>The migration map flags the old survey page as &ldquo;confirm it&rsquo;s still
  used.&rdquo; This rebuild keeps it and routes responses into the CRM rather than an inbox.
  If the team has stopped using it, delete the page and drop the 301 rather than leaving a
  form nobody reads.</p>
</div>
</div></div></section>
"""
    return S.page(
        path="/survey",
        title="Client Survey | Greenlight Mortgage — Longview, TX",
        desc="Tell Greenlight Mortgage how your loan went. Two minutes, straight to Kenneth "
             "Travis. Powered by Co/LAB Lending. Equal Housing Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/survey", "Survey")],
        scripts='<script src="/forms.js" defer></script>',
        noindex=True,   # a feedback form has no business competing in search
    )


# ==========================================================================
# APPLY — our own intake, replacing the handoff to the external LOS
# ==========================================================================

def apply_page():
    """KT's call: Apply Online becomes our form, reaching our team, routed
    internally rather than dumped in one inbox.

    What this form does NOT ask for: Social Security number, date of birth,
    account numbers, itemised income. Those belong on the licensed LOS, and the
    applications table has no columns for them. See the header comment in
    db/2026-08-01-applications-pipeline.sql for the reasoning.
    """

    def sel(id_, name, label, options, required=False, help_=""):
        opts = "".join(f'<option>{o}</option>' for o in options)
        req = " required" if required else ""
        h = f'<p class="help">{help_}</p>' if help_ else ""
        return (f'<div class="field"><label for="{id_}">{label}</label>{h}'
                f'<select id="{id_}" name="{name}"{req}>'
                f'<option value="">Choose one…</option>{opts}</select>'
                f'<p class="err">Please choose an option.</p></div>')

    body = f"""{S.hero(
        eyebrow="Apply",
        h1="Start your application",
        lede="About three minutes. Enough for a licensed loan officer to look at your "
             "situation properly and come back with real options &mdash; and no more than "
             "that.",
        trail=[("/", "Home"), (None, "Apply")])}

<section><div class="wrap"><div class="narrow">

<div class="callout">
  <h3>What we ask for here, and what we do not</h3>
  <p>Nothing on this page asks for your Social Security number, date of birth, or account
  numbers. It does not involve a credit inquiry. It is the conversation-starter &mdash; once a loan
  officer has spoken to you and you both decide to go ahead, the formal application happens
  on our secure loan origination system, which is where that information belongs.</p>
</div>

<form data-glm-form="application" novalidate style="margin-top:36px">

  <fieldset style="margin-bottom:34px">
    <legend>1 &mdash; Who you are</legend>
    <div class="frow">
      <div class="field"><label for="a-first">First name</label>
        <input id="a-first" name="first_name" type="text" autocomplete="given-name"
               required maxlength="80"><p class="err">Please enter your first name.</p></div>
      <div class="field"><label for="a-last">Last name</label>
        <input id="a-last" name="last_name" type="text" autocomplete="family-name"
               required maxlength="80"><p class="err">Please enter your last name.</p></div>
    </div>
    <div class="frow">
      <div class="field"><label for="a-email">Email</label>
        <input id="a-email" name="email" type="email" autocomplete="email"
               required maxlength="254"><p class="err">Please enter a valid email.</p></div>
      <div class="field"><label for="a-phone">Phone</label>
        <input id="a-phone" name="phone" type="tel" autocomplete="tel"
               required maxlength="32"><p class="err">Please enter a phone number.</p></div>
    </div>
    <div class="frow">
      {sel("a-contact", "preferred_contact", "Best way to reach you",
           ["Phone call", "Text message", "Email"])}
      {sel("a-time", "best_time", "Best time",
           ["Morning", "Afternoon", "Evening", "Any time"])}
    </div>
  </fieldset>

  <fieldset style="margin-bottom:34px">
    <legend>2 &mdash; What you are trying to do</legend>
    <div class="field"><label>Purpose</label>
      <div class="choices two">
        <label class="choice"><input type="radio" name="purpose" value="purchase" required>
          <span>Buy a home<small>First one or next one</small></span></label>
        <label class="choice"><input type="radio" name="purpose" value="refinance">
          <span>Refinance<small>Lower the payment or the term</small></span></label>
        <label class="choice"><input type="radio" name="purpose" value="cash_out">
          <span>Use my equity<small>Renovation, or clear other debt</small></span></label>
        <label class="choice"><input type="radio" name="purpose" value="not_sure">
          <span>Not sure yet<small>Tell me what makes sense</small></span></label>
      </div></div>
    <div class="frow">
      <div class="field"><label for="a-city">Property city</label>
        <input id="a-city" name="property_city" type="text" maxlength="80"
               placeholder="Longview"></div>
      <div class="field"><label for="a-state">State</label>
        <select id="a-state" name="property_state">
          <option value="">Choose one…</option>
          {"".join(f'<option value="{ab}">{n}</option>' for n, ab in
                   [("Texas","TX"),("Louisiana","LA"),("Michigan","MI"),
                    ("North Dakota","ND"),("Alabama","AL")])}
        </select>
        <p class="help">We are licensed in these {S.STATE_COUNT_WORD} states.</p></div>
    </div>
    <div class="frow">
      {sel("a-price", "price_band", "Price range (rough)",
           ["Under $150,000", "$150,000 – $250,000", "$250,000 – $400,000",
            "$400,000 – $650,000", "Over $650,000", "Not sure"])}
      {sel("a-time2", "timeline", "Timeline",
           ["As soon as possible", "1–3 months", "3–6 months",
            "6+ months", "Just exploring"])}
    </div>
  </fieldset>

  <fieldset style="margin-bottom:34px">
    <legend>3 &mdash; A little context</legend>
    <p class="sub" style="margin-top:0">Rough answers are fine. Nothing here is checked
    against anything, and none of it is a commitment.</p>
    <div class="frow">
      {sel("a-emp", "employment", "Employment",
           ["W-2 employee", "Self-employed", "Retired", "Military / VA",
            "Mix of the above", "Other"])}
      {sel("a-credit", "credit_band", "Credit, roughly",
           ["Excellent (740+)", "Good (680–739)", "Fair (620–679)",
            "Rebuilding (under 620)", "No idea"],
           help_="Your own estimate. We are not pulling anything.")}
    </div>
    <div class="field"><label>Anything that applies</label>
      <div class="choices two">
        <label class="choice"><input type="checkbox" name="veteran" value="yes">
          <span>I am a veteran or service member<small>Or a surviving spouse</small></span></label>
        <label class="choice"><input type="checkbox" name="first_time_buyer" value="yes">
          <span>This is my first home</span></label>
        <label class="choice"><input type="checkbox" name="working_with_agent" value="yes">
          <span>I am working with a realtor</span></label>
      </div></div>
    <div class="field"><label for="a-notes">Anything we should know?</label>
      <textarea id="a-notes" name="notes" rows="4" maxlength="4000"></textarea></div>
  </fieldset>

  <fieldset>
    <legend>4 &mdash; Permission to contact you</legend>
    <div class="consent">
      <input type="checkbox" id="a-tcpa" name="tcpa_consent" value="yes">
      <label for="a-tcpa">{TCPA_TEXT}</label>
    </div>
    <p class="disclose">Leave that unticked and we will reply by email only. Your application
    is handled either way &mdash; ticking it is not a condition of anything.</p>

    <div class="cta"><button class="btn go lg" type="submit">Send my application</button></div>
    <p class="formstatus" role="status" aria-live="polite"></p>
    <p class="disclose">Submitting this is not an application for credit and is
    <strong>not a commitment to lend</strong>. This step does not involve a credit
    inquiry of any kind. Any loan is subject to credit approval and underwriting, and only a licensed loan officer can quote
    a rate or confirm eligibility, after a complete application.</p>
  </fieldset>
</form>
</div></div></section>

<section class="dark"><div class="wrap">
<div class="split">
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>What happens next</p>
  <h2>You will hear from a person, once.</h2>
  <div class="steps">
    <div class="step"><h3>It reaches our team, not an inbox</h3><p>Your application lands in
    our pipeline and is assigned to someone by name. Nobody has to notice an email for it to
    get picked up.</p></div>
    <div class="step"><h3>A licensed loan officer calls</h3><p>Within one business day. Once
    &mdash; not six times in an hour.</p></div>
    <div class="step"><h3>We shop it</h3><p>Your file goes to a network of lenders rather than
    one bank's menu, and you get the options side by side.</p></div>
    <div class="step"><h3>The formal application</h3><p>If it makes sense to proceed, we send
    you a secure link to our loan origination system for the full application. That is the
    only place your Social Security number is ever asked for.</p></div>
  </div>
</div>
<div>
  <div class="callout">
    <h3>Already know you want the full application?</h3>
    <p>You can go straight to our secure loan origination system and start the formal 1003
    now. It runs under Kenneth Travis's own NMLS license.</p>
    <p style="margin-top:14px"><a href="{S.LOS_APPLY}" rel="noopener">
      Go to the secure application &nearr;</a></p>
  </div>
  <div class="callout">
    <h3>Rather talk first?</h3>
    <p>Plenty of people do. Call <a href="tel:{S.PHONE_HREF}">{S.PHONE}</a> and skip the form
    entirely.</p>
  </div>
</div>
</div>
</div></section>
"""
    return S.page(
        path="/apply",
        title="Start Your Mortgage Application | Greenlight Mortgage — Longview, TX",
        desc="Begin your mortgage application with Greenlight Mortgage in Longview, Texas. "
             "About three minutes, no credit inquiry, and no Social Security number needed "
             "to start. Powered by Co/LAB Lending. Equal Housing Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/apply", "Apply")],
        scripts='<script src="/forms.js" defer></script>',
    )


# ==========================================================================
# LEGAL
# ==========================================================================

def privacy():
    body = f"""{S.hero(
        eyebrow="Legal",
        h1="Privacy Policy",
        lede="What we collect, why, who we share it with, and how to tell us to stop.",
        trail=[("/", "Home"), (None, "Privacy Policy")])}

<section><div class="wrap"><div class="prose">
<p class="updated">Last updated 1 August 2026 &middot;
<span class="todo">Draft — requires legal review before launch</span></p>

<div class="callout">
  <h3>Build note, to be deleted before launch</h3>
  <p>This is a working draft written to cover what this website actually does. It is not
  legal advice and it has not been reviewed by counsel. Greenlight is a financial institution
  under the Gramm-Leach-Bliley Act, which means the GLBA Privacy Rule applies and an annual
  privacy notice may be required in a prescribed format. A lawyer needs to review this and
  confirm the notice obligations before the site goes live.</p>
</div>

<p>{S.COMPANY} (&ldquo;Greenlight,&rdquo; &ldquo;we,&rdquo; &ldquo;us&rdquo;) operates this
website. This policy explains how we handle information collected <strong>through this
website</strong>. Information you provide during an actual loan application is handled under
our loan-application privacy notice, which you receive as part of that process.</p>

<h2>What we collect</h2>
<p><strong>Information you give us.</strong> When you send the contact form, request a home
value report, complete the Estimated Savings tool, or submit a testimonial or survey, we
collect what you type &mdash; typically your name, email address, phone number, and details
about your property or loan situation.</p>
<p><strong>Information collected automatically.</strong> Pages viewed, the site that referred
you, approximate location derived from your IP address, and general device type. We use this
to understand which pages are useful.</p>
<p><strong>Consent records.</strong> If you tick the box agreeing to be contacted by phone or
text, we record the exact wording you agreed to, the date and time, your IP address, and your
browser's user agent string. We keep this so we can demonstrate what you agreed to.</p>

<h2>What we do not collect here</h2>
<p>This website does not ask for your Social Security number, date of birth, account numbers,
or income documentation, and you should not send them through any form on it. The loan
application itself is hosted on a separate, licensed loan origination system. Please do not
email sensitive documents &mdash; your loan officer will send a secure link.</p>

<h2>Why we use it</h2>
<ul>
<li>To answer your question and follow up about your inquiry</li>
<li>To prepare the estimate or report you asked for</li>
<li>To meet our record-keeping obligations as a licensed mortgage broker</li>
<li>To understand which parts of the site are working</li>
</ul>

<h2>Who we share it with</h2>
<p>We share your information with service providers who help us operate: our customer
relationship management system, our database and hosting providers, and our email delivery
provider. They act on our instructions.</p>
<p>Where you are pursuing a loan, we share what is necessary with lenders and settlement
service providers to place and close it.</p>
<p>We may disclose information where required by law or by a regulator, including the Texas
Department of Savings and Mortgage Lending.</p>
<p><strong>We do not sell your personal information.</strong></p>

<h2>Calls and texts</h2>
<p>We only call or text you about your inquiry, and we only use an autodialer or send
marketing texts if you gave express written consent by ticking the box. That consent is never
a condition of getting a loan. Reply <strong>STOP</strong> to any text to opt out, tell any
caller to remove you, or email us. We honour opt-outs across all our systems.</p>

<h2>Cookies</h2>
<p>This site uses a small number of first-party cookies and similar storage for basic
analytics. There are no third-party advertising trackers on this site, no advertising
retargeting pixels, and no data broker integrations. Your browser settings can block cookies;
the site will still work.</p>

<h2>How long we keep it</h2>
<p>Inquiries are retained while we are in contact and afterwards for as long as our
record-keeping obligations as a licensed mortgage broker require. Consent records are kept for
at least as long as required to evidence the consent.</p>

<h2>Your choices</h2>
<p>Ask us for a copy of what we hold, ask us to correct it, ask us to delete it, or withdraw
consent to calls and texts. Write to us at the address below and we will respond. Some records
we are legally required to retain.</p>

<h2>Security</h2>
<p>Information is transmitted over encrypted connections and stored in access-controlled
systems. No method of transmission over the internet is completely secure, which is exactly
why this site does not ask for the sensitive material a full application requires.</p>

<h2>Children</h2>
<p>This site is not directed at children under 13 and we do not knowingly collect their
information.</p>

<h2>Changes</h2>
<p>If we change this policy we will update the date at the top of this page.</p>

<h2>Contact us</h2>
<p>{S.COMPANY}<br>{S.STREET}, {S.CITY}, {S.STATE} {S.ZIP}<br>
<a href="tel:{S.PHONE_HREF}">{S.PHONE}</a></p>
<p>Company NMLS #{S.NMLS_CO}. Equal Housing Opportunity.</p>
</div></div></section>
"""
    return S.page(
        path="/privacy",
        title="Privacy Policy | Greenlight Mortgage — Longview, TX",
        desc="How Greenlight Mortgage collects, uses and protects information submitted "
             "through www.glmtg.com, including call and text consent records.",
        body=body,
        trail=[("/", "Home"), ("/privacy", "Privacy Policy")],
    )


def accessibility():
    body = f"""{S.hero(
        eyebrow="Legal",
        h1="Accessibility",
        lede="This site should work for everyone, including people using a screen reader, a "
             "keyboard, or a magnified display. Here is where we stand and how to tell us we "
             "got it wrong.",
        trail=[("/", "Home"), (None, "Accessibility")])}

<section><div class="wrap"><div class="prose">
<p class="updated">Last updated 1 August 2026</p>

<p>{S.COMPANY} is committed to making this website usable by as many people as possible. We
aim to meet <strong>WCAG 2.1 Level AA</strong>.</p>

<h2>What we have done</h2>
<ul>
<li>Every page is navigable by keyboard alone, with a visible focus outline on each
interactive element and a skip-to-content link</li>
<li>Text and interface colors are tested for contrast, including the small print &mdash;
disclosure text is set at a legible size with real contrast, never gray-on-gray</li>
<li>Headings are used in order so screen reader users can navigate by structure</li>
<li>Images that carry meaning have alternative text; decorative marks are hidden from
assistive technology</li>
<li>Forms have real labels, and errors are announced rather than only shown in color</li>
<li>Animation is subtle and respects the operating system's reduce-motion setting; no content
depends on a script running successfully</li>
<li>Layouts reflow to narrow and magnified screens without horizontal scrolling</li>
<li>The video player has visible controls and does not autoplay</li>
</ul>

<h2>Where we know we fall short</h2>
<p>Being honest is more useful than claiming full conformance:</p>
<ul>
<li>The homepage video does not yet have captions or a transcript. It should have both. This
is the most significant known gap.</li>
<li>The loan application is hosted on a third-party origination system we do not control, so
we cannot warrant its accessibility. If you have difficulty with it, call us on
{S.PHONE} and we will take your application over the phone.</li>
<li>This site has not yet had a formal third-party accessibility audit.</li>
</ul>

<h2>If something does not work</h2>
<p>Tell us and we will fix it, and we will help you get what you needed in the meantime. No
one should have to fight a website to ask about a mortgage.</p>
<p><a href="tel:{S.PHONE_HREF}">{S.PHONE}</a><br>
{S.COMPANY}, {S.STREET}, {S.CITY}, {S.STATE} {S.ZIP}</p>
<p>We aim to respond within two business days. If you need information from this site in a
different format &mdash; large print, or read to you over the phone &mdash; just ask.</p>

<p class="disclose">Equal Housing Opportunity. We do business in accordance with the Federal
Fair Housing Act and the Equal Credit Opportunity Act.</p>
</div></div></section>
"""
    return S.page(
        path="/accessibility",
        title="Accessibility | Greenlight Mortgage — Longview, TX",
        desc="Greenlight Mortgage's accessibility commitment, what we have done to meet WCAG "
             "2.1 AA, where we currently fall short, and how to report a problem.",
        body=body,
        trail=[("/", "Home"), ("/accessibility", "Accessibility")],
    )


# ==========================================================================

def build():
    print("content pages")
    write("/", homepage())
    write("/buy", buy_page())
    write("/about", about())
    write("/testimonials", testimonials())
    write("/reviews", reviews())
    write("/contact", contact())
    write("/apply", apply_page())
    write("/learn", learn())
    write("/resources", resources())
    write("/blog", blog_index())
    for p in POSTS:
        write(f"/blog/{p['slug']}", blog_post(**p))
    write("/survey", survey())
    write("/privacy", privacy())
    write("/accessibility", accessibility())


if __name__ == "__main__":
    build()
