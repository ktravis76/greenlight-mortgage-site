#!/usr/bin/env python3
"""Shared chrome for every page on the site.

(Named sitegen, not site: Python imports a stdlib module called `site` at startup,
so a local site.py here would be shadowed by it and never load.)

Every page — homepage, loan programs, content pages, tools — is rendered through
`page()` here. That is deliberate: the header, the footer, and the compliance block
are legally load-bearing, and the last thing this project needs is three copies of
the license list drifting apart. Change it once, rebuild, it is right everywhere.

Nothing in this file is a fact we invented. Names, numbers, licenses and addresses
come from MIGRATION-MAP.md and the verified-facts block in START-HERE.md.
"""
import html
import re

# ---------------------------------------------------------------- verified facts

COMPANY   = "Greenlight Mortgage, LLC"
SHORT     = "Greenlight Mortgage"
POWERED   = "Powered by Co/LAB Lending"
TAGLINE   = "Green means GO! Drive home with Greenlight Mortgage."
FOUNDED   = "2008"

STREET    = "4523 Judson Rd"
CITY      = "Longview"
STATE     = "TX"
ZIP       = "75605"
PHONE     = "903-331-0892"
PHONE_HREF = "9033310892"

NMLS_CO   = "2426021"
NMLS_KT   = "233918"

# Six states, in the order the current site lists them.
LICENSES = [
    ("Texas", "2426021"),
    ("Alabama", "23417"),
    ("Florida", "MBR6235"),
    ("Louisiana", "2426021"),
    ("North Dakota", "ML104832"),
    ("South Carolina", "2426021"),
]

# External licensed LOS. We do not rebuild the 1003 — it collects SSNs.
APPLY = "https://greenlight.my1003app.com/233918/register"

ORIGIN = "https://greenlightmortgage.com"

# Local intent targets. Towns are real places we serve; districts came from KT directly.
TOWNS     = ["Longview", "Gilmer", "Kilgore", "Hallsville",
             "White Oak", "Tyler", "Marshall", "Jefferson"]
DISTRICTS = ["Spring Hill ISD", "Pine Tree ISD", "Hallsville ISD"]

LOAN_NAV = [("va", "VA"), ("conventional", "Conventional"), ("fha", "FHA"),
            ("usda", "USDA"), ("jumbo", "Jumbo"), ("refinance", "Refinancing")]

TOOL_NAV = [("/tools/estimate", "Estimated Savings"),
            ("/tools/calculator", "Mortgage Calculator"),
            ("/tools/home-value", "Home Value Report")]

LEARN_NAV = [("/learn", "Learning Center"), ("/resources", "Resources"),
             ("/blog", "Blog"), ("/survey", "Client Survey")]

# ------------------------------------------------------------- the 7 testimonials
# Verbatim from the current site. Do not paraphrase these — they are real people.

TESTIMONIALS = [
    ("Tim", "Longview, TX",
     "They got us closed! That's the bottom line. Good group and a total team effort. "
     "Give them a challenge to get you closed. They are more than capable. Will "
     "definitely use them again in the future."),
    ("Jason", "Gilmer, TX",
     "Greenlight Mortgage was referred to me and I couldn't be happier. As a first time "
     "buyer, I had a lot of questions and concerns. The entire team was always available "
     "and kept me informed the entire time. A very nice closure was Kenneth being at my "
     "closing just to congratulate me and thank me in person."),
    ("Maxwell", "Jefferson, TX",
     "The Kenneth Travis Team was wonderful to work with. They made the whole process run "
     "smooth. Candice and Anna made sure we stayed informed throughout and helped whenever "
     "and wherever along the way. I would recommend this group to everyone!"),
    ("John", "Longview, TX",
     "Kenneth and his team have helped with my refinance and buying a home now. Very "
     "effective, efficient, and welcoming to every need. Even when the wife started "
     "freaking out during parts of the transaction, they stayed calm and professional. "
     "They also do not stop when the closing is done. Best lender in East Texas."),
    ("Robyn", "Longview, TX",
     "I cannot express enough how pleased I am with every member of the Kenneth Travis "
     "team. What could have been an extremely stressful process was not stressful at all. "
     "What's even better is that they also offer a moving truck free of charge."),
    ("Jasper", "Longview, TX",
     "Hands down the best lending team in East Texas. They were there for me throughout "
     "the whole process and handled any issues promptly. If they can't get it done then "
     "no one can!"),
    ("Brent", "Longview, TX",
     "Kenneth and his team made the process simple and kept us in the loop the whole way "
     "through. Straight answers every time we asked a question."),
]

# ------------------------------------------------------------------ tiny templater
# Token syntax is {{name}} rather than str.format, because these templates carry
# inline CSS and JS full of literal braces.

_TOKEN = re.compile(r"\{\{(\w+)\}\}")


def render(tpl, **kw):
    def sub(m):
        key = m.group(1)
        if key not in kw:
            raise KeyError(f"template token {{{{{key}}}}} has no value")
        return str(kw[key])
    return _TOKEN.sub(sub, tpl)


def esc(s):
    return html.escape(str(s), quote=True)


def jstr(s):
    """JSON string literal, for hand-built ld+json."""
    return '"' + (str(s).replace("\\", "\\\\").replace('"', '\\"')
                  .replace("\n", " ")) + '"'


# --------------------------------------------------------------- TCPA consent
# The consent sentence, in one place. Every surface that asks for a phone number
# reads this constant, and the stored consent record copies it verbatim, so we can
# always show exactly what a given person agreed to on a given day.
#
# ⚠️ COMPLIANCE MUST APPROVE THIS WORDING BEFORE THE SITE TAKES A PHONE NUMBER.
# It is drafted to meet the usual express-written-consent requirements — it names
# Greenlight, covers autodialed and pre-recorded calls plus texts, states consent is
# not a condition of obtaining credit, and explains opt-out — but it was drafted by a
# builder, not a lawyer, and the planned 50,000-lead SMS campaign runs on top of
# whatever it says. Change it here and it changes everywhere.

TCPA_TEXT = (
    "I agree that Greenlight Mortgage, LLC (NMLS #2426021) and its loan officers may contact "
    "me at the phone number I provided, including by autodialed or pre-recorded calls and by "
    "text message, about my mortgage enquiry. Message and data rates may apply. "
    "<strong>Consent is not a condition of obtaining a loan or any other service.</strong> "
    "I can opt out at any time by replying STOP to a text, asking the caller to remove me, or "
    'emailing us &mdash; see our <a href="/privacy">Privacy Policy</a>.'
)

# Small inline arrow used on card links throughout the site.
ARROW = ('<svg viewBox="0 0 14 9" aria-hidden="true"><path d="M9.2.8 13 4.5 9.2 8.2M13 4.5H1"'
         ' fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"'
         ' stroke-linejoin="round"/></svg>')


# ------------------------------------------------------------------------ snippets

def phone_link(cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<a href="tel:{PHONE_HREF}"{c}>{PHONE}</a>'


def disclosure(text="Estimate only. Subject to credit approval and underwriting."):
    """One short line beside a number. Never a paragraph, never a modal."""
    return f'<p class="disclose">{esc(text)}</p>'


# ⚠️ PLACEHOLDER — COMPLIANCE MUST SUPPLY THE EXACT WORDING BEFORE LAUNCH.
# Texas Finance Code requires a specific SML complaint/recovery-fund notice, and the
# statutory text includes the department's current mailing address and toll-free number.
# We are not inventing either one. Greenlight's compliance contact provides the verbatim
# block; paste it here and rebuild. Until then the page links to the department directly,
# which is accurate but is NOT the full required notice.
TX_SML_NOTICE = (
    "Texas Department of Savings and Mortgage Lending: consumers wishing to file a complaint "
    "against a mortgage broker should follow the complaint process published by the department "
    'at <a href="https://www.sml.texas.gov">sml.texas.gov</a>, where complaint forms and '
    "instructions are available. "
    '<em class="todo">[Compliance: replace with the verbatim statutory SML complaint and '
    "Recovery Fund notice, including the department's current address and toll-free number, "
    "before launch.]</em>"
)

LICENSE_SENTENCE = (
    f"{COMPANY} is a licensed Mortgage Broker in the state of Texas. "
    + "NMLS " + NMLS_CO + ". "
    + " ".join(f"{name} &mdash; {num}." for name, num in LICENSES)
)


def trust_bar():
    """EHO / NMLS / Co-LAB / six states, presented the way a bank shows FDIC.
    A design element that happens to satisfy a disclosure requirement."""
    return f"""<div class="trustbar"><div class="wrap"><div class="trustrow">
<div class="trust"><img src="/assets/from-old-site/badge-ehl.png" alt="" width="28" height="28" loading="lazy">
<span><strong>Equal Housing Opportunity</strong><small>We lend without regard to race, color, religion, sex, handicap, familial status or national origin.</small></span></div>
<div class="trust"><img src="/assets/from-old-site/badge-nmls.png" alt="" width="28" height="28" loading="lazy">
<span><strong>NMLS #{NMLS_CO}</strong><small>Kenneth Travis, individual NMLS #{NMLS_KT}. Verify us at nmlsconsumeraccess.org.</small></span></div>
<div class="trust"><span class="dot" aria-hidden="true"></span>
<span><strong>{POWERED}</strong><small>Licensed in six states: Texas, Alabama, Florida, Louisiana, North Dakota, South Carolina.</small></span></div>
</div></div></div>"""


def cta_band(head="Let's find out where you stand.",
             sub="A short conversation, a straight answer either way, and no hard credit pull to begin.",
             primary=("/tools/estimate", "See what you could save"),
             secondary=("/contact", "Talk to a person")):
    return f"""<section class="band-wrap"><div class="wrap"><div class="ctaband">
<span class="signal" aria-hidden="true"><i></i><i></i><i></i></span>
<h2>{esc(head)}</h2>
<p>{esc(sub)}</p>
<div class="cta">
<a class="btn go" href="{primary[0]}">{esc(primary[1])}</a>
<a class="btn onDark" href="{secondary[0]}">{esc(secondary[1])}</a>
</div>
<p class="bandnote">Not a commitment to lend. Subject to credit approval and underwriting.</p>
</div></div></section>"""


# --------------------------------------------------------------------- the header

def _dropdown(label, items, base=""):
    links = "".join(f'<a href="{base}{h}">{esc(t)}</a>' for h, t in items)
    return f"""<div class="has-menu">
<button class="navlink" aria-expanded="false" aria-haspopup="true">{esc(label)}<svg class="chev" viewBox="0 0 10 6" aria-hidden="true"><path d="M1 1l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg></button>
<div class="menu"><div class="menuinner">{links}</div></div>
</div>"""


def header():
    loans = [(f"/loans/{s}", n) for s, n in LOAN_NAV] + [("/loans", "All loan options")]
    return f"""<a class="skip" href="#main">Skip to content</a>
<header id="siteheader"><div class="wrap nav">
<a class="brand" href="/" aria-label="{SHORT} home">
  <span class="light" aria-hidden="true"><i></i></span>
  <span class="bname">{SHORT}<small>{POWERED}</small></span>
</a>
<nav class="links" aria-label="Main">
  {_dropdown("Loan Options", loans)}
  {_dropdown("Tools", TOOL_NAV)}
  {_dropdown("Learn", LEARN_NAV)}
  <a class="navlink" href="/about">About</a>
  <a class="navlink" href="/reviews">Reviews</a>
  <a class="navlink" href="/contact">Contact</a>
</nav>
<div class="navcta">
  <a class="phone" href="tel:{PHONE_HREF}"><svg viewBox="0 0 16 16" aria-hidden="true" width="14" height="14"><path d="M3 1.5h2.2l1.1 3-1.5 1.1a9 9 0 0 0 4.6 4.6l1.1-1.5 3 1.1V12a2.5 2.5 0 0 1-2.6 2.5A11.6 11.6 0 0 1 1.5 4.1 2.5 2.5 0 0 1 3 1.5z" fill="currentColor"/></svg>{PHONE}</a>
  <a class="btn sm" href="{APPLY}">Apply Online</a>
  <button class="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span><span></span></button>
</div>
</div>
<div class="drawer" hidden>
  <div class="wrap">
    <p class="dh">Loan Options</p>
    {"".join(f'<a href="/loans/{s}">{n}</a>' for s, n in LOAN_NAV)}
    <a href="/loans">All loan options</a>
    <p class="dh">Tools</p>
    {"".join(f'<a href="{h}">{t}</a>' for h, t in TOOL_NAV)}
    <p class="dh">Learn</p>
    {"".join(f'<a href="{h}">{t}</a>' for h, t in LEARN_NAV)}
    <p class="dh">Company</p>
    <a href="/about">About</a><a href="/reviews">Reviews</a><a href="/testimonials">Testimonials</a><a href="/contact">Contact</a>
    <a class="btn" href="{APPLY}" style="margin-top:18px">Apply Online</a>
    <a class="phone big" href="tel:{PHONE_HREF}">{PHONE}</a>
  </div>
</div>
</header>"""


# --------------------------------------------------------------------- the footer
# The footer carries the compliance weight. Small and quiet, but legible —
# 13px with real contrast, not 6pt grey-on-grey.

def footer():
    lic = " &middot; ".join(f"{n} {num}" for n, num in LICENSES)
    loans = "".join(f'<a href="/loans/{s}">{n}</a>' for s, n in LOAN_NAV)
    tools = "".join(f'<a href="{h}">{t}</a>' for h, t in TOOL_NAV)
    learn = "".join(f'<a href="{h}">{t}</a>' for h, t in LEARN_NAV)
    towns = " &middot; ".join(TOWNS)
    return f"""<footer><div class="wrap">
<div class="fg">
<div class="fbrand">
  <a class="brand" href="/"><span class="light" aria-hidden="true"><i></i></span>
  <span class="bname">{SHORT}<small>{POWERED}</small></span></a>
  <p>A mortgage brokerage serving Longview and East Texas since {FOUNDED}. We shop a network
  of lenders instead of selling one bank's menu.</p>
  <p class="fnap"><strong>{COMPANY}</strong><br>{STREET}, {CITY}, {STATE} {ZIP}<br>
  <a href="tel:{PHONE_HREF}">{PHONE}</a></p>
  <div class="fbadges">
    <img src="/assets/from-old-site/badge-ehl.png" alt="Equal Housing Opportunity" width="34" height="34" loading="lazy">
    <img src="/assets/from-old-site/badge-nmls.png" alt="NMLS Consumer Access" width="34" height="34" loading="lazy">
  </div>
</div>
<div><h4>Loan options</h4>{loans}</div>
<div><h4>Tools</h4>{tools}</div>
<div><h4>Learn</h4>{learn}</div>
<div><h4>Company</h4>
  <a href="/about">About &amp; team</a><a href="/reviews">Reviews</a>
  <a href="/testimonials">Testimonials</a><a href="/contact">Contact</a>
  <a href="/privacy">Privacy Policy</a><a href="/accessibility">Accessibility</a>
</div>
</div>

<p class="fareas"><strong>Serving East Texas:</strong> {towns} &middot; and the {", ".join(DISTRICTS)} communities.</p>

<div class="legal">
<p><strong>{COMPANY}</strong> is a licensed Mortgage Broker in the state of Texas.
Company NMLS #{NMLS_CO} &middot; Kenneth Travis, individual NMLS #{NMLS_KT}.
State licenses: {lic}.
{STREET}, {CITY}, {STATE} {ZIP} &middot; {PHONE}.
Consumers may verify licensing at <a href="https://www.nmlsconsumeraccess.org">nmlsconsumeraccess.org</a>.</p>

<p data-compliance="tx-sml-notice">{TX_SML_NOTICE}</p>

<p>This website is for general information about our mortgage brokerage services and is
<strong>not a commitment to lend</strong> and not an offer of credit. All loans are subject to
credit approval, underwriting, income and asset verification, and a satisfactory property
appraisal. Program availability, rates, and terms are subject to change without notice and vary
based on loan amount, credit profile, occupancy, property type, and other factors. Any figures,
examples, or estimates shown anywhere on this site are illustrative only and are not an offer or
guarantee of a specific interest rate, APR, monthly payment, or loan term. Rate quotes,
eligibility determinations, and loan approvals are made only by a licensed loan officer following
a complete application.</p>

<p>We do not provide legal, accounting, or tax advice; please consult a qualified professional
about your situation. We do business in accordance with the Federal Fair Housing Act and the
Equal Credit Opportunity Act. Equal Housing Opportunity.</p>

<p class="copy">&copy; 2026 {COMPANY}. All rights reserved. &middot;
<a href="/privacy">Privacy</a> &middot; <a href="/accessibility">Accessibility</a></p>
</div>
</div></footer>"""


# ------------------------------------------------------------------------- schema

def breadcrumbs(trail):
    """trail: [(url, name), ...] including Home."""
    items = ",".join(
        '{"@type":"ListItem","position":%d,"name":%s,"item":%s}'
        % (i + 1, jstr(name), jstr(ORIGIN + url))
        for i, (url, name) in enumerate(trail))
    return '{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[%s]}' % items


def faq_schema(faqs):
    if not faqs:
        return ""
    items = ",".join(
        '{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
        % (jstr(q), jstr(a)) for q, a in faqs)
    return '{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[%s]}' % items


ORG_SCHEMA = (
    '{"@context":"https://schema.org","@type":"MortgageBroker",'
    '"name":%s,"@id":%s,"url":%s,"telephone":"+1-903-331-0892",'
    '"image":%s,"logo":%s,"priceRange":"$$",'
    '"address":{"@type":"PostalAddress","streetAddress":%s,"addressLocality":%s,'
    '"addressRegion":%s,"postalCode":%s,"addressCountry":"US"},'
    '"areaServed":[%s],'
    '"founder":{"@type":"Person","name":"Kenneth Travis","jobTitle":"President & CEO"},'
    '"foundingDate":"2008","slogan":%s}'
) % (jstr(COMPANY), jstr(ORIGIN), jstr(ORIGIN),
     jstr(ORIGIN + "/assets/from-old-site/logo-header.png"),
     jstr(ORIGIN + "/assets/from-old-site/logo-header.png"),
     jstr(STREET), jstr(CITY), jstr(STATE), jstr(ZIP),
     ",".join(jstr(f"{t}, TX") for t in TOWNS), jstr(TAGLINE))


# ----------------------------------------------------------------------- the page

_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{title}}</title>
<meta name="description" content="{{desc}}">
<link rel="canonical" href="{{canonical}}">
<meta name="theme-color" content="#0b3a29">
<meta property="og:site_name" content="Greenlight Mortgage">
<meta property="og:title" content="{{ogtitle}}">
<meta property="og:description" content="{{desc}}">
<meta property="og:type" content="website">
<meta property="og:url" content="{{canonical}}">
<meta property="og:image" content="{{origin}}/assets/from-old-site/logo-header.png">
<meta name="twitter:card" content="summary">
{{robots}}
<link rel="preconnect" href="https://athovwknbwbbqworsbrm.supabase.co">
<script>document.documentElement.className+=" js"</script>
<link rel="stylesheet" href="/style.css">
{{schema}}
</head>
<body{{bodyattr}}>
{{header}}
<main id="main">
{{body}}
</main>
{{trust}}
{{footer}}
<script src="/config.js" defer></script>
<script src="/site.js" defer></script>
{{scripts}}
</body>
</html>
"""


def page(path, title, desc, body, *, trail=None, faqs=None, extra_schema=None,
         scripts="", body_class="", noindex=False, show_trust=True, org=False):
    """Render a complete page. `path` is the site-absolute URL ('/about')."""
    blocks = []
    if org:
        blocks.append(ORG_SCHEMA)
    if trail:
        blocks.append(breadcrumbs(trail))
    if faqs:
        blocks.append(faq_schema(faqs))
    if extra_schema:
        blocks.append(extra_schema)
    schema = "\n".join(
        f'<script type="application/ld+json">{b}</script>' for b in blocks)

    canonical = ORIGIN + ("" if path == "/" else path)
    return render(
        _PAGE,
        title=esc(title),
        ogtitle=esc(title.split(" | ")[0]),
        desc=esc(desc),
        canonical=canonical,
        origin=ORIGIN,
        robots='<meta name="robots" content="noindex,nofollow">' if noindex else "",
        schema=schema,
        header=header(),
        body=body,
        trust=trust_bar() if show_trust else "",
        footer=footer(),
        scripts=scripts,
        bodyattr=f' class="{body_class}"' if body_class else "",
    )


def hero(eyebrow, h1, lede, ctas=None, trail=None, variant=""):
    """Standard interior-page hero.

    `eyebrow`, `h1` and `lede` are treated as trusted HTML so callers can use
    entities and <em>; escape any dynamic value with esc() on the way in.
    `ctas` is [(href, label, cls), ...]."""
    crumb = ""
    if trail:
        parts = " <span>/</span> ".join(
            (f'<a href="{u}">{esc(n)}</a>' if u else f"<span>{esc(n)}</span>")
            for u, n in trail)
        crumb = f'<nav class="crumb" aria-label="Breadcrumb">{parts}</nav>'
    btns = ""
    if ctas:
        btns = '<div class="cta">' + "".join(
            f'<a class="btn {c}" href="{h}">{esc(t)}</a>' for h, t, c in ctas) + "</div>"
    return f"""<div class="hero {variant}"><div class="wrap">
{crumb}
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>{eyebrow}</p>
<h1>{h1}</h1>
<p class="lede">{lede}</p>
{btns}
</div></div>"""
