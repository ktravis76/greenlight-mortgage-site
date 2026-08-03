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

# Licensed states, corrected by KT on 2026-08-01.
#
# The old kennethtravis.com footer listed six: TX, AL, LA, ND, MI. That is
# wrong. The correct list is five — Texas, Louisiana, Michigan, North Dakota,
# Alabama. Florida and South Carolina are OUT; Michigan is IN and was never on
# the old site at all.
#
# ⚠️ The Michigan license number is NOT KNOWN and has not been invented. Until KT
# supplies it, the page says so in plain sight rather than showing a plausible
# number. Advertising a state license with a wrong number is worse than
# advertising it with none.
#
# Only states with a license number we can point at are advertised.
LICENSES = [
    ("Texas", "2426021"),
    ("Louisiana", "2426021"),
    ("North Dakota", "ML104832"),
    ("Alabama", "23417"),
]

# ⚠️ MICHIGAN IS HELD BACK, DELIBERATELY, AND THIS IS NOT ME OVERRULING KT.
#
# KT gave the list as Texas, Louisiana, Michigan, North Dakota, Alabama. Four of
# those check out against license numbers carried over from the old site.
# Michigan does not: there is no number for it, and it appears in no source we
# can find. Every public listing — and every web search result — traces back to
# the old kennethtravis.com footer, which is the very document KT says is wrong,
# so it corroborates nothing in either direction.
#
# The asymmetry decides it. Advertising a state license the company does not
# hold is a licensing violation with a regulator attached. Omitting one it does
# hold costs a line of marketing copy for as long as it takes to check. So
# Michigan stays out of the count, out of the footer, and out of the schema
# until somebody reads it off NMLS Consumer Access — which takes about thirty
# seconds in a browser and is the only source that actually settles it.
#
# Put it back by moving the tuple up into LICENSES with its number.
PENDING_LICENSES = [
    ("Michigan", "no license number, and not corroborated by any source we can "
                 "reach — confirm on nmlsconsumeraccess.org under company NMLS "
                 f"2426021"),
]

STATE_COUNT = len(LICENSES)
STATE_COUNT_WORD = "four"
STATE_NAMES = ", ".join(n for n, _ in LICENSES[:-1]) + f" and {LICENSES[-1][0]}"

# Apply Online now points at OUR intake form, per KT.
#
# LOS_APPLY is where the FULL 1003 still happens — a licensed loan origination
# system under Kenneth's own NMLS. /apply collects enough to start a real
# conversation and route the file to the right person, then hands off there for
# the parts that carry a Social Security number. See db/2026-08-01-applications-
# pipeline.sql for why that line is drawn where it is.
APPLY = "/apply"
LOS_APPLY = "https://greenlight.my1003app.com/233918/register"

ORIGIN = "https://www.glmtg.com"

# Local intent targets. Towns are real places we serve; districts came from KT directly.
TOWNS     = ["Longview", "Gilmer", "Kilgore", "Hallsville",
             "White Oak", "Tyler", "Marshall", "Jefferson"]
DISTRICTS = ["Spring Hill ISD", "Pine Tree ISD", "Hallsville ISD"]

# ------------------------------------------------------------------- the team
# Names supplied by KT on 2026-08-01. Names ONLY — no job titles and no NMLS
# numbers came with them, so none are shown.
#
# This matters more here than on a normal About page. On a mortgage broker's
# site, a name beside an NMLS number reads as "this person is a licensed loan
# originator". Guessing a title would either invent a licence that does not
# exist or quietly strip one from someone who has it. Both are worse than a gap.
# So each card shows the real name and says plainly what is still missing.
#
# KT also said there are probably more people than this.

TEAM = [
    dict(name="Kenneth Travis", role="President & CEO", nmls=NMLS_KT,
         note="Founded Greenlight in 2008. Eight years in the United States "
              "Marine Corps, discharged as a Sergeant.",
         photo="/assets/from-old-site/kenneth-travis-headshot.png", confirmed=True),
    dict(name="Julia Forrester", role=None, nmls=None, note=None, confirmed=False),
    dict(name="Kimberly Langford", role=None, nmls=None, note=None, confirmed=False),
    dict(name="Ryan Nichols", role=None, nmls=None, note=None, confirmed=False),
    dict(name="Preston Travis", role=None, nmls=None, note=None, confirmed=False),
    dict(name="Jared Rangel", role=None, nmls=None, note=None, confirmed=False),
    dict(name="Lisa", role=None, nmls=None, confirmed=False,
         note="Surname still to come."),
]

LOAN_NAV = [("va", "VA"), ("va-irrrl", "VA IRRRL"), ("conventional", "Conventional"),
            ("fha", "FHA"), ("usda", "USDA"), ("jumbo", "Jumbo"),
            ("refinance", "Refinancing")]

TOOL_NAV = [("/tools/estimate", "Estimated Savings"),
            ("/tools/calculator", "Mortgage Calculator"),
            ("/tools/affordability", "What Can I Afford?"),
            ("/tools/net-proceeds", "Seller Net Proceeds"),
            ("/tools/rent-vs-buy", "Rent vs Buy"),
            ("/tools/home-value", "Home Value Report")]

LEARN_NAV = [("/learn", "Learning Center"), ("/why-a-broker", "Why a Broker"),
             ("/resources", "Resources"),
             ("/archive", "Longview Archive"), ("/blog", "Blog"),
             ("/survey", "Client Survey")]

# ------------------------------------------------------------- client reviews
#
# ⚠️ CORRECTION, 2026-08-01. An earlier pass of this build shipped a SEVENTH
# testimonial attributed to "Brent" whose text was written by the builder, not by
# Brent. MIGRATION-MAP.md listed seven names but the old homepage carried only
# six quotes, and the gap was filled instead of flagged. That is fabrication of a
# client testimonial on a regulated site and it should never have happened.
#
# Brent's real review has since been retrieved from its permalink on the live
# site and is below, verbatim, with its published date. Maxwell's stored text had
# also been tidied and truncated; it is now the verbatim original.
#
# THE RULE FROM HERE: a review only renders with `verified=True` if its exact
# wording has been read from a source we can link to. Everything else renders
# with a visible provenance note. Never write words and put a client's name on
# them.
#
# Fields: name, place, text, date (as published), source, url, verified.

REVIEWS = [
    dict(name="Brent", place="Longview, TX", date="2021-10-01",
         source="kennethtravis.com",
         url="https://www.kennethtravis.com/review/a-great-lender-knowledgeable-and-friendly/",
         verified=True,
         text="From pre-approval right through to closing on my home the Kenneth Travis "
              "team at Greenlight Mortgage did a great job. All the staff were extremely "
              "friendly, helpful and knowledgeable. The whole process was very smooth and "
              "helped remove a lot of potential stress. I would definitely use them again."),

    dict(name="Maxwell", place="Jefferson, TX", date="2021-10-01",
         source="kennethtravis.com",
         url="https://www.kennethtravis.com/review/maxwell/",
         verified=True,
         text="The Kenneth Travis Team was wonderful to work with they made the whole "
              "process run smooth. Candice and Anna made sure we stayed informed throughout "
              "the whole process and helped whenever and wherever along the way. I would "
              "recommend this group to everyone! Thank Ya'll So Much!!"),

    # --- The five below came across from the old site's homepage. Their opening
    # lines match what is published today, but the full stored wording has not
    # been read from a permalink, and at least one other review in this set was
    # found to have been silently tidied. Treated as unverified until each one's
    # source page is retrieved. They render with a provenance note.
    dict(name="Tim", place="Longview, TX", date=None,
         source="kennethtravis.com", url="https://www.kennethtravis.com/reviews/",
         verified=False,
         text="They got us closed! That's the bottom line. Good group and a total team "
              "effort. Give them a challenge to get you closed. They are more than capable. "
              "Will definitely use them again in the future."),
    dict(name="Jason", place="Gilmer, TX", date=None,
         source="kennethtravis.com", url="https://www.kennethtravis.com/reviews/",
         verified=False,
         text="Greenlight Mortgage was referred to me and I couldn't be happier. As a first "
              "time buyer, I had a lot of questions and concerns. The entire team was always "
              "available and kept me informed the entire time. A very nice closure was "
              "Kenneth being at my closing just to congratulate me and thank me in person."),
    dict(name="John", place="Longview, TX", date=None,
         source="kennethtravis.com", url="https://www.kennethtravis.com/reviews/",
         verified=False,
         text="Kenneth and his team have helped with my refinance and buying a home now. "
              "Very effective, efficient, and welcoming to every need. Even when the wife "
              "started freaking out during parts of the transaction, they stayed calm and "
              "professional. They also do not stop when the closing is done. Best lender in "
              "East Texas."),
    dict(name="Robyn", place="Longview, TX", date=None,
         source="kennethtravis.com", url="https://www.kennethtravis.com/reviews/",
         verified=False,
         text="I cannot express enough how pleased I am with every member of the Kenneth "
              "Travis team. What could have been an extremely stressful process was not "
              "stressful at all. What's even better is that they also offer a moving truck "
              "free of charge."),
    dict(name="Jasper", place="Longview, TX", date=None,
         source="kennethtravis.com", url="https://www.kennethtravis.com/reviews/",
         verified=False,
         text="Hands down the best lending team in East Texas. They were there for me "
              "throughout the whole process and handled any issues promptly. If they can't "
              "get it done then no one can!"),
]

# ------------------------------------------------------- external review profiles
# Real, checked 2026-08-01. Ratings move, so each carries the date it was read and
# the page links out — we do not present a stale number as current.
#
# ⚠️ Birdeye lists the address as 1328 Heritage Blvd, Longview TX 75605, which is
# NOT the 4523 Judson Rd address used everywhere else on this site. One of the two
# is out of date. KT needs to confirm which, and the wrong one needs correcting at
# the source — a mismatched NAP across listings also costs local search ranking.

REVIEW_PROFILES = [
    dict(platform="Experience.com", rating="4.85", count="398",
         url="https://www.experience.com/reviews/kenneth-12682826",
         checked="1 August 2026", verified=True,
         note="Kenneth Travis, Greenlight Mortgage, NMLS #2426021, Longview TX."),
    dict(platform="Birdeye", rating="4.8", count="197",
         url="https://birdeye.com/greenlight-mortgage-168122712651937",
         checked="1 August 2026", verified=True,
         note="Aggregates Google reviews. Address on this listing does not match "
              "4523 Judson Rd — see note in sitegen.py."),
    dict(platform="Zillow", rating=None, count=None,
         url="https://www.zillow.com/lender-profile/glmortgagelender/",
         checked=None, verified=False,
         note="Profile found in search but could not be read to confirm it is "
              "Greenlight's. KT to confirm before this links out."),
    dict(platform="Google Business Profile", rating=None, count=None, url=None,
         checked=None, verified=False,
         note="KT to supply the profile URL."),
    dict(platform="Facebook", rating=None, count=None, url=None,
         checked=None, verified=False,
         note="The @glmtg page exists; review-tab URL to be supplied by KT."),
]

# Back-compat for callers that just want (name, place, text).
TESTIMONIALS = [(r["name"], r["place"], r["text"]) for r in REVIEWS]

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
    "text message, about my mortgage inquiry. Message and data rates may apply. "
    "<strong>Consent is not a condition of obtaining a loan or any other service.</strong> "
    "I can opt out at any time by replying STOP to a text, asking the caller to remove me, or "
    'emailing us &mdash; see our <a href="/privacy">Privacy Policy</a>.'
)

# ----------------------------------------------------------- loan program marks
# One per program, each with its own accent, so the six cards stop reading as one
# card repeated. Accents stay inside the brand's green-to-teal-to-gold range —
# they differentiate without turning the page into a paint chart.
#
# The "who" line is deliberately blunt: most visitors do not know which program
# they need, and a label they can match themselves against beats a product name.

def _m(body):
    return (f'<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" '
            f'stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{body}</svg>')


LOAN_MARKS = {
    # Conventional — a straightforward house on a level base.
    "conventional": ("#0f7a4d", "Steady income, solid credit",
                     _m('<path d="M4 14 16 5l12 9"/><path d="M7 12.5V26h18V12.5"/>'
                        '<path d="M13 26v-7h6v7"/><path d="M3 28h26"/>')),
    # FHA — a key, the first door.
    "fha": ("#1f8fa8", "First house, or credit still healing",
            _m('<circle cx="11" cy="12" r="6"/><path d="m15.4 16.4 10 10"/>'
               '<path d="m22 23 2.6-2.6M24.6 25.6 27 23"/>')),
    # VA — a service chevron inside a shield.
    "va": ("#8a6d1f", "You served, or your spouse did",
           _m('<path d="M16 3.5 6 7.5v8.8c0 6.2 4.1 11.4 10 12.9 5.9-1.5 10-6.7 10-12.9V7.5z"/>'
              '<path d="m11 16 5-4.5 5 4.5M11 21.5l5-4.5 5 4.5"/>')),
    # USDA — a field horizon with a sun. Rural, literally.
    "usda": ("#2f8f3f", "Just outside town, or nothing saved",
             _m('<circle cx="16" cy="12" r="4.5"/>'
                '<path d="M16 3.5v2M16 18.5v2M7.5 12h-2M28.5 12h-2'
                'M10 6l-1.4-1.4M23.4 19.4 22 18M10 18l-1.4 1.4M23.4 4.6 22 6"/>'
                '<path d="M3 25h26M6 28h20"/>')),
    # Jumbo — stacked tiers, a bigger building.
    "jumbo": ("#7a4fa3", "Above the conforming limit",
              _m('<path d="M6 28V13l10-6 10 6v15"/><path d="M3 28h26"/>'
                 '<path d="M11 28v-6h10v6M11 17h4M17 17h4"/>')),
    # Refinance — a loop, going around again.
    "refinance": ("#0f7a4d", "Tired of the payment you have",
                  _m('<path d="M27 16a11 11 0 0 1-18.8 7.8"/>'
                     '<path d="M5 16A11 11 0 0 1 23.8 8.2"/>'
                     '<path d="M23.8 3.5v4.7h-4.7M8.2 28.5v-4.7h4.7"/>')),
}


def review_card(r, cls=""):
    """A review with its provenance attached. Anything we cannot link to says so
    on the page rather than borrowing the credibility of the ones we can."""
    when = ""
    if r.get("date"):
        y, m, d = r["date"].split("-")
        months = ("January February March April May June July August September "
                  "October November December").split()
        when = f'<time datetime="{r["date"]}">{int(d)} {months[int(m)-1]} {y}</time>'

    if r.get("verified") and r.get("url"):
        prov = (f'<a class="prov ok" href="{r["url"]}" rel="nofollow noopener" '
                f'target="_blank">Verified on {esc(r["source"])} &nearr;</a>')
    else:
        prov = ('<span class="prov pending">Carried over from the previous site &mdash; '
                'wording not yet re-checked against its source</span>')

    return (f'<figure class="quote {cls}">'
            f'<blockquote>{esc(r["text"])}</blockquote>'
            f'<figcaption><span class="who">{esc(r["name"])} &middot; {esc(r["place"])}</span>'
            f'{when}{prov}</figcaption></figure>')


def loan_card(slug, nav, blurb, cls=""):
    accent, who, mark = LOAN_MARKS[slug]
    return (f'<a class="lcard {cls}" href="/loans/{slug}" style="--accent:{accent}">'
            f'<span class="lmark">{mark}</span>'
            f'<span class="who">{esc(who)}</span>'
            f'<h3>{esc(nav)}</h3><p>{blurb}</p>'
            f'<span class="go">Read more {ARROW}</span></a>')


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

def lic_num(num):
    """Render a state license number, or a visible gap where we do not have one."""
    if num:
        return num
    return '<em class="todo">number pending &mdash; KT to confirm</em>'


LICENSE_SENTENCE = (
    f"{COMPANY} is a licensed Mortgage Broker in the state of Texas. "
    + "NMLS " + NMLS_CO + ". "
    + " ".join(f"{name} &mdash; {lic_num(num)}." for name, num in LICENSES)
)

# Why there are two NMLS numbers on this site. Consumers notice, and an
# unexplained mismatch reads like an error or worse. It is neither — a company
# and each individual loan originator are licensed separately.
NMLS_EXPLAINER = (
    f"You will see two NMLS numbers on this site, and both are correct. "
    f"<strong>#{NMLS_CO}</strong> licenses the company, {COMPANY}. "
    f"<strong>#{NMLS_KT}</strong> licenses Kenneth Travis personally as a loan originator. "
    f"Federal law licenses the business and the individual separately, so a broker will "
    f"always have both. You can look either of them up at "
    f'<a href="https://www.nmlsconsumeraccess.org">nmlsconsumeraccess.org</a>.'
)


# ------------------------------------------------------------------ trust marks
# The EHO and NMLS artwork rescued off the old multisite is 44x45px of hairline
# black line art. Scaled into a trust bar it renders as an empty smudge, which is
# exactly how it looked — KT reported seeing no mark at all beside "Equal Housing
# Opportunity". Drawn as vector here instead: crisp at any size, correct on dark.

MARK_EHO = """<svg class="mark" viewBox="0 0 40 40" role="img" aria-label="Equal Housing Opportunity">
<path d="M20 5 3.5 18.2h4.2V35h24.6V18.2h4.2z" fill="currentColor" opacity=".14"/>
<path d="M20 5 3.5 18.2h4.2V35h24.6V18.2h4.2z" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linejoin="round"/>
<rect x="14" y="21.5" width="12" height="2.7" rx="1.35" fill="currentColor"/>
<rect x="14" y="27" width="12" height="2.7" rx="1.35" fill="currentColor"/>
</svg>"""

MARK_NMLS = """<svg class="mark" viewBox="0 0 40 40" role="img" aria-label="NMLS Consumer Access">
<circle cx="20" cy="20" r="15.6" fill="none" stroke="currentColor" stroke-width="2.1"/>
<path d="M20 11.4 27 15v5.2c0 4.4-2.9 7.6-7 8.8-4.1-1.2-7-4.4-7-8.8V15z"
      fill="currentColor" opacity=".16"/>
<path d="M20 11.4 27 15v5.2c0 4.4-2.9 7.6-7 8.8-4.1-1.2-7-4.4-7-8.8V15z"
      fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
<path d="m16.9 20.2 2.3 2.3 4.1-4.3" fill="none" stroke="currentColor"
      stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

# Echoes the gaslight in the real logo: finial, pitched cap, tapered glass cage
# with a lit pane, and a base. Not a battery.
MARK_LANTERN = """<svg class="mark" viewBox="0 0 40 40" role="img" aria-label="Greenlight">
<path d="M20 2.5v2.6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
<path d="M20 5.2 27.8 12H12.2z" fill="currentColor"/>
<path d="M14 13.5h12l1.6 15.2H12.4z" fill="currentColor" opacity=".22"/>
<path d="M14 13.5h12l1.6 15.2H12.4z" fill="none" stroke="currentColor"
      stroke-width="2" stroke-linejoin="round"/>
<path d="M20 13.5v15.2M13.2 21h13.6" stroke="currentColor" stroke-width="1.3" opacity=".55"/>
<path d="M12 30.5h16" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>
<path d="M17 32.6h6v2.4h-6z" fill="currentColor"/>
</svg>"""


def trust_bar():
    """EHO / NMLS / Co-LAB, presented the way a bank shows FDIC.
    A design element that happens to satisfy a disclosure requirement."""
    return f"""<div class="trustbar"><div class="wrap"><div class="trustrow">
<div class="trust">{MARK_EHO}
<span><strong>Equal Housing Opportunity</strong><small>We lend without regard to race, color,
religion, sex, handicap, familial status or national origin.</small></span></div>
<div class="trust">{MARK_NMLS}
<span><strong>Company NMLS #{NMLS_CO}</strong><small>Kenneth Travis, loan originator, is
separately licensed as NMLS #{NMLS_KT}. Both are real &mdash; look either up at
nmlsconsumeraccess.org.</small></span></div>
<div class="trust">{MARK_LANTERN}
<span><strong>{POWERED}</strong><small>Licensed in {STATE_COUNT_WORD} states:
{STATE_NAMES}.</small></span></div>
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
  <img src="/assets/from-old-site/logo-header.png" alt="{SHORT} — The Kenneth Travis Team"
       width="217" height="76" fetchpriority="high">
</a>
<nav class="links" aria-label="Main">
  {_dropdown("Loan Options", loans)}
  {_dropdown("Tools", TOOL_NAV)}
  {_dropdown("Learn", LEARN_NAV)}
  <a class="navlink" href="/archive">Archive</a>
  <a class="navlink" href="/pros">For Pros</a>
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
    <p class="dh">For professionals</p>
    <a href="/pros">Tools to share</a><a href="/archive">Longview Archive</a>
    <p class="dh">Company</p>
    <a href="/about">About</a><a href="/reviews">Reviews</a><a href="/testimonials">Testimonials</a><a href="/contact">Contact</a>
    <a class="btn" href="{APPLY}" style="margin-top:18px">Apply Online</a>
    <a class="phone big" href="tel:{PHONE_HREF}">{PHONE}</a>
  </div>
</div>
</header>"""


# --------------------------------------------------------------------- the footer
# The footer carries the compliance weight. Small and quiet, but legible —
# 13px with real contrast, not 6pt gray-on-gray.

def footer():
    lic = " &middot; ".join(f"{n} {lic_num(num)}" for n, num in LICENSES)
    loans = "".join(f'<a href="/loans/{s}">{n}</a>' for s, n in LOAN_NAV)
    tools = "".join(f'<a href="{h}">{t}</a>' for h, t in TOOL_NAV)
    learn = "".join(f'<a href="{h}">{t}</a>' for h, t in LEARN_NAV)
    towns = " &middot; ".join(TOWNS)
    return f"""<footer><div class="wrap">
<div class="fg">
<div class="fbrand">
  <a class="brand" href="/">
    <img src="/assets/from-old-site/logo-header.png" alt="{SHORT} — The Kenneth Travis Team"
         width="217" height="76" loading="lazy">
  </a>
  <p>A mortgage brokerage serving Longview and East Texas since {FOUNDED}. We shop a network
  of lenders instead of selling one bank's menu.</p>
  <p class="fnap"><strong>{COMPANY}</strong><br>{STREET}, {CITY}, {STATE} {ZIP}<br>
  <a href="tel:{PHONE_HREF}">{PHONE}</a></p>
  <div class="fbadges">{MARK_EHO}{MARK_NMLS}</div>
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
Licensed in {STATE_COUNT_WORD} states &mdash; {lic}.
{STREET}, {CITY}, {STATE} {ZIP} &middot; {PHONE}.</p>

<p>{NMLS_EXPLAINER}</p>

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
<!-- Meta Pixel -->
<script>
!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '828760880613908');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=828760880613908&ev=PageView&noscript=1"/></noscript>
<!-- End Meta Pixel -->
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
<script src="/partner.js" defer></script>
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
