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


# =============================================================================
# THE FUNNEL — /loans/* as Facebook lead-ad destinations
# =============================================================================
# Visitors arrive from a Facebook Lead Ad having ALREADY given name/phone/email
# on Facebook's native form. So these pages never open with a lead-capture
# form. The job is: confirm the click was smart, put a live estimator in their
# hands within one scroll, and drive exactly ONE next action.
#
#   Refi pages (va-irrrl, refinance)  ->  send your mortgage statement
#   Purchase pages (the other five)   ->  call / request a callback
#
# All chrome, math and analytics live in shared files: /assets/funnel.js,
# /assets/rates.js (the ONLY place a sample rate exists), and the funnel
# section of style.css. Pages stay generated — never hand-fork one.
#
# Compliance lines that hold on every funnel page:
#   - "quote" never appears as something we offer; estimates only
#   - no rate figure in copy — funnel.js injects the sample from rates.js,
#     labeled a sample, so the number lives in exactly one file
#   - the estimate footnote sits directly under every rendered number
#   - VA pages keep the 36-month recoupment / net tangible benefit language
#   - no countdown timers, no scarcity, no "guaranteed", ever

FUNNEL = {
    # ------------------------------------------------------------- refi pages
    "va-irrrl": dict(
        mode="refi",
        kicker="VA IRRRL &middot; Streamline refinance",
        hook="The refinance so streamlined the VA made it a word: <em>IRRRL</em>.",
        sub="Interest Rate Reduction Refinance Loan. Built for veterans already in a "
            "VA loan. Usually no appraisal, far less paperwork, one purpose: a lower "
            "payment. Thirty seconds on the dials below tells you if it's worth a real look.",
        rig_h2="Drag the dials. Watch the number.",
        rig_sub="Set them to what you pay now. The green number is what a streamline "
                "could put back in your pocket each month &mdash; an estimate, not a promise. "
                "And the VA rule applies here first: the refinance has to produce a real "
                "net tangible benefit and recoup its costs within 36 months, or it "
                "shouldn't be written at all.",
        steps=[
            ("Send your statement",
             "It already has every number that matters &mdash; balance, rate, payment. "
             "No forms. No interview. One upload.",
             ("#cta", "Send it now")),
            ("We run the real math",
             "A licensed loan officer prices your actual file &mdash; usually same day. "
             "If it doesn't clear the VA's 36-month recoupment test, the answer is no, "
             "and we'll be the ones to say it.",
             ("tel:__PHONE__", "Rather talk first? Call us")),
            ("You decide",
             "Your current loan and the new one, side by side, in plain English. "
             "If the math doesn't work, we leave you alone. Options win &mdash; "
             "including the option of doing nothing.",
             ("#cta", "Send my statement")),
        ],
        objections=[
            ("&ldquo;I hate paperwork.&rdquo;",
             "So does everybody. An IRRRL is the least-paperwork loan in the business: "
             "usually no appraisal, usually no new certificate of eligibility. Your "
             "statement does most of the talking."),
            ("&ldquo;I get refi junk mail every week.&rdquo;",
             "Those letters aren't us. The VA polices this loan hard: it must produce a "
             "real net tangible benefit and its costs must come back within 36 months "
             "&mdash; or it can't be written. That rule protects you. We apply it before "
             "anything else."),
            ("The 10% detail nobody asks about",
             "A service-connected disability rating of 10% or more waives the VA funding "
             "fee entirely. That one fact regularly flips a marginal file into a clear "
             "win. If you're rated, say so early."),
        ],
        why=dict(
            va=True,
            h2="Why veterans actually do this.",
            sub="An IRRRL is the VA saying: you already proved yourself on this loan "
                "&mdash; so skip the obstacle course and keep more of your money. "
                "Here's what that means in practice, and the one test every file has "
                "to pass.",
            ticks=[
                ("Fast by design.",
                 "Usually no appraisal and far less credit paperwork than a full "
                 "refinance. Clean files have closed in as little as eight business "
                 "days &mdash; every file sets its own pace, but &ldquo;streamline&rdquo; "
                 "is the VA's word, not our marketing."),
                ("The six-month box.",
                 "Paid your VA loan on time for the last six months? That's the "
                 "biggest qualification box, already checked. This program was built "
                 "for exactly where you're standing."),
                ("A rate swap, not a new adventure.",
                 "Same house, same VA loan &mdash; just at a lower cost. No cash out, "
                 "no equity games. The IRRRL exists for one reason: reducing what the "
                 "loan costs you."),
                ("The 36-month rule works for you.",
                 "Federal requirement: the costs must pay for themselves within 36 "
                 "months or the loan shouldn't be written. That's a consumer "
                 "protection, and it's the first math we run &mdash; watch it work "
                 "on the meter."),
            ]),
        cta_head="Your statement has the exact numbers.",
        cta_sub="Send it over and a licensed loan officer runs the real math &mdash; "
                "usually same day. No robots. No spam. One call.",
        cta_label="Send my statement",
    ),

    "refinance": dict(
        mode="refi",
        kicker="Refinance &middot; Longview, TX",
        hook="Your rate isn't a <em>life sentence</em>.",
        sub="You signed at whatever the market was doing that week. Markets move. "
            "Stop guessing whether yours is still the right number &mdash; the dials "
            "below take thirty seconds.",
        rig_h2="What are you paying that you don't have to?",
        rig_sub="Set the dials to your current loan. The green number is the monthly "
                "difference a refinance could make &mdash; an estimate to start a real "
                "conversation, not the end of one.",
        steps=[
            ("Send your statement",
             "Balance, rate, payment &mdash; it's all on page one. One upload beats "
             "twenty form fields.",
             ("#cta", "Send it now")),
            ("We shop it",
             "We're brokers. Your file goes to a network of lenders, not one bank's "
             "menu, and a licensed loan officer brings back what's actually available.",
             ("tel:__PHONE__", "Questions first? Call us")),
            ("You decide",
             "Sometimes the math says refinance. Sometimes it says stay put &mdash; "
             "and if it does, we'll tell you that for free. The math matters more "
             "than the deal.",
             ("#cta", "Send my statement")),
        ],
        objections=[
            ("&ldquo;Refinancing costs money.&rdquo;",
             "It does &mdash; and it's only worth it if the savings pay those costs back "
             "before you'd move. That break-even math is the first thing we run, and if "
             "it doesn't clear, we say so."),
            ("&ldquo;I don't want to restart 30 years.&rdquo;",
             "Then don't. A refinance can keep your remaining term, shorten it, or drop "
             "mortgage insurance without touching the clock. The lowest payment isn't "
             "always the win &mdash; we show you both numbers."),
            ("&ldquo;My credit's taken a hit since I bought.&rdquo;",
             "Maybe it matters, maybe it doesn't &mdash; different lenders draw the line "
             "in different places, which is exactly why we shop a network instead of "
             "asking one bank. Finding out costs nothing and starts with no hard pull."),
        ],
        why=dict(
            va=False,
            h2="The only refinance math that matters.",
            sub="A refinance is worth doing when what it saves you outruns what it "
                "costs you &mdash; before you'd move. That's the whole test, and you "
                "can watch it run on your own dials.",
            ticks=[
                ("Break-even is the whole game.",
                 "Every refinance has costs. Divide them by the monthly saving and "
                 "you get your break-even month. If you'll still own the house past "
                 "that point, the math works. If not, don't do it &mdash; and we'll "
                 "say exactly that."),
                ("Your term is negotiable.",
                 "Keep your remaining term, shorten it, or drop mortgage insurance "
                 "without touching the clock. The lowest payment isn't automatically "
                 "the win &mdash; we show you the total cost either way."),
                ("A network beats a menu.",
                 "We're brokers. The same file prices differently across lenders, "
                 "and we shop it instead of quoting you one bank's answer."),
            ]),
        cta_head="Your statement has the exact numbers.",
        cta_sub="Send it over and a licensed loan officer runs the real math &mdash; "
                "usually same day. No robots. No spam. One call.",
        cta_label="Send my statement",
    ),

    # --------------------------------------------------------- purchase pages
    "va": dict(
        mode="purchase",
        kicker="VA loans &middot; Longview, TX",
        hook="You earned this benefit. <em>Most veterans never use it.</em>",
        sub="No down payment in many cases. No monthly mortgage insurance. That's not "
            "a promo &mdash; it's your benefit, and it's usually the strongest option "
            "on the table for anyone eligible.",
        price=(80000, 900000, 250000, 5000),
        down=(0, 25, 0, 0.5),
        rig_h2="See what a VA payment looks like.",
        rig_sub="Start the down payment dial at zero &mdash; that's the point of the "
                "benefit. The number below is principal and interest on a sample figure, "
                "so you have somewhere real to start.",
        steps=[
            ("Play with the dials",
             "Get a feel for what East Texas prices turn into as a monthly payment "
             "with nothing down. No mortgage insurance is the quiet superpower here.",
             ("#estimator", "Back to the dials")),
            ("Talk to a human",
             "Five minutes with a licensed loan officer &mdash; and a veteran-owned "
             "team that runs VA files every week. We check your entitlement and what "
             "it's actually worth. No hard credit pull to start.",
             ("tel:__PHONE__", "Call 903-331-0892")),
            ("We handle the VA part",
             "Appraisal logistics, seller conversations, the funding-fee math "
             "&mdash; including whether a disability rating waives it for you. "
             "You house-hunt. We carry the file.",
             ("#cta", "Let's run my real numbers")),
        ],
        objections=[
            ("&ldquo;I heard VA loans are hard to close.&rdquo;",
             "Outdated. A VA loan closes on the same calendar as any other when the "
             "lender knows the program &mdash; and we close them every week. Seller "
             "hesitation is a communication problem, and handling it is our job, not "
             "yours."),
            ("&ldquo;I don't have anything saved.&rdquo;",
             "In many cases you don't need a down payment at all. Closing costs are a "
             "separate, smaller conversation &mdash; and there are ways to handle those "
             "too. Don't rule yourself out from your couch."),
            ("&ldquo;I'm not even sure I'm eligible.&rdquo;",
             "Veterans, active duty, Guard, Reserve, and many surviving spouses. "
             "Entitlement can often be restored or reused &mdash; even if you've used "
             "it before. Checking takes minutes and costs nothing."),
        ],
        cta_head="Let's find out what your benefit is worth.",
        cta_sub="One call with a licensed loan officer. Straight answers about "
                "eligibility, the funding fee, and your real numbers &mdash; no hard "
                "credit pull to start.",
        cta_label="Let&rsquo;s run my real numbers",
    ),

    "fha": dict(
        mode="purchase",
        kicker="FHA loans &middot; Longview, TX",
        hook="Your credit doesn't have to be perfect. <em>That's the whole point of FHA.</em>",
        sub="Built for real people with real credit histories. Lower down payment, "
            "more forgiving guidelines, and the most common first step into a first "
            "house in East Texas.",
        price=(80000, 900000, 220000, 5000),
        down=(3.5, 25, 3.5, 0.5),
        rig_h2="See what an FHA payment looks like.",
        rig_sub="The down payment dial starts at 3.5% &mdash; FHA's floor for "
                "qualifying buyers. The number below is principal and interest on a "
                "sample figure, so you have somewhere real to start.",
        steps=[
            ("Play with the dials",
             "That house you keep driving past &mdash; put its price on the dial and "
             "see what it turns into monthly. Knowing beats wondering.",
             ("#estimator", "Back to the dials")),
            ("Talk to a human",
             "A licensed loan officer looks at your actual situation &mdash; credit, "
             "income, the gift from your folks &mdash; and tells you where you stand. "
             "No hard credit pull to start.",
             ("tel:__PHONE__", "Call 903-331-0892")),
            ("Get a real plan",
             "Ready now? We move. Six months out? You leave with a punch list that "
             "gets you there. Either answer is a win.",
             ("#cta", "Let's run my real numbers")),
        ],
        objections=[
            ("&ldquo;My credit isn't good enough.&rdquo;",
             "Says who? FHA guidelines are more forgiving than conventional, and "
             "different lenders draw different lines on top of them. One lender's no "
             "is not the answer &mdash; it's one data point. We shop a network."),
            ("&ldquo;I can't save a down payment.&rdquo;",
             "FHA starts at 3.5% down for qualifying buyers &mdash; and it can come "
             "from an eligible gift. On a lot of East Texas homes that's less than "
             "people burn on rent deposits and moving twice."),
            ("&ldquo;I got turned down once already.&rdquo;",
             "Then you talked to one lender with one rulebook. Files that get declined "
             "at a bank get written somewhere else every single week. That's the whole "
             "reason brokers exist."),
        ],
        cta_head="Stop guessing about your credit.",
        cta_sub="Five minutes with a licensed loan officer tells you where you actually "
                "stand &mdash; and what to fix if the answer is &ldquo;not yet.&rdquo; "
                "No hard credit pull to start.",
        cta_label="Let&rsquo;s run my real numbers",
    ),

    "conventional": dict(
        mode="purchase",
        kicker="Conventional loans &middot; Longview, TX",
        hook="The 20% down rule is a myth. <em>Let's talk about what's real.</em>",
        sub="Twenty percent was never the price of admission &mdash; it's just where "
            "one insurance cost falls away. Qualifying first-time buyers see programs "
            "starting far lower. The math matters more than the folklore.",
        price=(80000, 900000, 280000, 5000),
        down=(3, 30, 5, 0.5),
        rig_h2="See the payment at YOUR down payment.",
        rig_sub="Drag the down payment dial and watch what actually changes. The "
                "number below is principal and interest on a sample figure &mdash; "
                "somewhere real to start.",
        steps=[
            ("Play with the dials",
             "Compare 5% down against 20% and look at the real monthly difference. "
             "Most people are surprised how small the gap is &mdash; and how many "
             "years of saving it doesn't justify.",
             ("#estimator", "Back to the dials")),
            ("Talk to a human",
             "A licensed loan officer prices your actual file &mdash; credit, income, "
             "property &mdash; and lays the options side by side. No hard credit pull "
             "to start.",
             ("tel:__PHONE__", "Call 903-331-0892")),
            ("Pick your lane",
             "Sometimes conventional wins. Sometimes FHA genuinely beats it. We're "
             "brokers &mdash; we don't care which one you pick, only that it's the "
             "right one.",
             ("#cta", "Let's run my real numbers")),
        ],
        objections=[
            ("&ldquo;I need 20% down, right?&rdquo;",
             "No. That number is where private mortgage insurance falls away on a "
             "conventional loan &mdash; not the cost of entry. Qualifying first-time "
             "buyers can see programs starting at 3%. Waiting years to hit 20% has "
             "its own price tag: rent."),
            ("&ldquo;I don't want to pay PMI forever.&rdquo;",
             "On conventional loans you don't. PMI comes off once you've built enough "
             "equity &mdash; unlike FHA, where it usually rides for the life of the "
             "loan. That difference is exactly why this program exists."),
            ("&ldquo;My income is complicated.&rdquo;",
             "Self-employed, commission, two jobs &mdash; complicated isn't a no, it's "
             "a documentation question. And when one lender's box doesn't fit, we have "
             "a network of others. Options win."),
        ],
        cta_head="Find out what down payment actually makes sense.",
        cta_sub="Five minutes with a licensed loan officer. Real numbers on your real "
                "situation &mdash; not folklore. No hard credit pull to start.",
        cta_label="Let&rsquo;s run my real numbers",
    ),

    "usda": dict(
        mode="purchase",
        kicker="USDA loans &middot; East Texas",
        hook="Zero down &mdash; and more of East Texas qualifies <em>than you think</em>.",
        sub="The most overlooked loan in the region. If the address is eligible and "
            "your household income fits, the down payment is zero. Not low. Zero.",
        price=(80000, 900000, 200000, 5000),
        down=(0, 20, 0, 0.5),
        rig_h2="See what zero-down actually costs monthly.",
        rig_sub="Leave the down payment dial on zero &mdash; that's the program. The "
                "number below is principal and interest on a sample figure, so you "
                "have somewhere real to start.",
        towns=["Gilmer", "Hallsville", "White Oak", "Diana", "Ore City", "Jefferson"],
        towns_h2="Is your town on the map?",
        towns_sub="Tap the area you're looking in. These are East Texas communities "
                  "where homes regularly qualify &mdash; but USDA runs on the exact "
                  "address, so the real check is a two-minute conversation, not a "
                  "guess.",
        steps=[
            ("Check your town",
             "USDA eligibility is drawn by address, not by county &mdash; and the map "
             "covers far more of East Texas than people assume. Don't rule yourself "
             "out from your couch.",
             ("#towns", "Tap your town")),
            ("Talk to a human",
             "Two things have to line up: the property and your household income. A "
             "licensed loan officer checks both against the current limits in minutes. "
             "No hard credit pull to start.",
             ("tel:__PHONE__", "Call 903-331-0892")),
            ("Buy the house, keep the savings",
             "Zero down doesn't mean zero planning &mdash; closing costs still exist. "
             "But it changes what's possible right now, this year, not five years of "
             "saving from now.",
             ("#cta", "Let's run my real numbers")),
        ],
        objections=[
            ("&ldquo;I'm too close to town to qualify.&rdquo;",
             "People assume that constantly, and they're wrong constantly. Eligibility "
             "is drawn address by address, and communities just outside Longview "
             "qualify all the time. Check before you assume."),
            ("&ldquo;I don't earn enough &mdash; or too much.&rdquo;",
             "USDA has household income limits set by area and family size, revised "
             "periodically. The only way to know is to check yours against the current "
             "figures &mdash; which takes us about two minutes."),
            ("&ldquo;Zero down sounds too good to be true.&rdquo;",
             "It's a federal rural-development program that's been running for decades "
             "&mdash; one of exactly two zero-down loans in America, and the other one "
             "requires military service. The catch is simply that the address and your "
             "income both have to fit."),
        ],
        cta_head="Two minutes settles it.",
        cta_sub="Give us the address and we'll check the map and the income limits "
                "with you. If USDA fits, it's zero down. If not, we'll tell you what "
                "does fit. No hard credit pull to start.",
        cta_label="Let&rsquo;s run my real numbers",
    ),

    "jumbo": dict(
        mode="purchase",
        kicker="Jumbo loans &middot; Longview, TX",
        hook="Big loan? The bank gave you one answer. <em>We ask a whole network.</em>",
        sub="Above the conforming limit, every lender writes its own rules &mdash; "
            "which means the spread between one answer and the best answer is wider "
            "here than anywhere else in lending. This is where a broker earns it.",
        price=(800000, 3000000, 1100000, 25000),
        down=(10, 40, 10, 1),
        rig_h2="Size the payment before you size the house.",
        rig_sub="Dial in the price range you're actually shopping. The number below "
                "is principal and interest on a sample figure &mdash; jumbo pricing "
                "varies more between lenders than any other product, which is exactly "
                "the point.",
        steps=[
            ("Play with the dials",
             "Get the monthly shape of the purchase before you fall for a property. "
             "At this size, structure decisions move real money.",
             ("#estimator", "Back to the dials")),
            ("Talk to a human",
             "A licensed loan officer maps your file &mdash; income structure, assets, "
             "reserves &mdash; against a network of jumbo lenders with genuinely "
             "different appetites. No hard credit pull to start.",
             ("tel:__PHONE__", "Call 903-331-0892")),
            ("We run the competition",
             "One file, shopped across lenders that actually want it. You see the "
             "options side by side and pick. That's it. That's the pitch.",
             ("#cta", "Let's run my real numbers")),
        ],
        objections=[
            ("&ldquo;My bank already said no.&rdquo;",
             "One bank, one rulebook, one no. Jumbo guidelines vary enormously between "
             "lenders &mdash; the same file gets declined at one desk and written at "
             "another every week. A no is a data point, not a verdict."),
            ("&ldquo;I'm self-employed &mdash; my income looks weird on paper.&rdquo;",
             "In jumbo lending, complex income is normal, not a red flag. It means "
             "more documentation, not a worse outcome &mdash; and knowing which lender "
             "reads your kind of file well is precisely the job."),
            ("&ldquo;I'll need 20% down and a vault of cash.&rdquo;",
             "Requirements vary more on jumbo than on any other loan &mdash; down "
             "payment, reserves, all of it. That variation is the reason to shop it "
             "instead of accepting the first answer."),
        ],
        cta_head="Make the lenders compete for it.",
        cta_sub="One conversation with a licensed loan officer, one file, a network "
                "of answers. No hard credit pull to start.",
        cta_label="Let&rsquo;s run my real numbers",
    ),
}

# The one-line footnote that sits directly under every rendered number.
FUNNEL_FOOTNOTE = ("*Estimate only &mdash; not a quote, offer, or approval. Subject to "
                   "credit approval and underwriting. Your actual rate and payment will "
                   "differ.")


def _funnel_hero(slug, f):
    """Hook hero: dark forest, serif hook, Kenneth's media slot. The kicker
    carries data-fb-kicker so funnel.js can swap it for ?src=fb traffic."""
    return f"""<div class="hero funnel"><div class="wrap">
<nav class="crumb" aria-label="Breadcrumb"><a href="/">Home</a> <span>/</span> <a href="/loans">Loan options</a> <span>/</span> <span>{esc(f["kicker"].split("&middot;")[0].strip())}</span></nav>
<div class="funnelgrid">
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span><span data-fb-kicker>{f["kicker"]}</span></p>
  <h1>{f["hook"]}</h1>
  <p class="lede">{f["sub"]}</p>
  <div class="cta"><a class="btn go lg" href="#estimator">See your number <span class="bounce">&darr;</span></a></div>
</div>
<div>
  <div class="adhero-media">
    <video controls preload="none" playsinline
           poster="/assets/from-old-site/kenneth-travis-headshot.png">
      <source src="/assets/from-old-site/kt-video.mp4" type="video/mp4">
      Your browser cannot play this video.
    </video>
  </div>
  <p class="vidcap" style="color:rgba(233,244,237,.6)">Kenneth Travis &middot; President &amp; CEO &middot; Loan Originator NMLS #{NMLS_KT}</p>
</div>
</div>
</div></div>"""


def _funnel_rig(slug, f):
    """The centerpiece. Static markup; /assets/funnel.js wires the behavior.
    With JS off (or broken) CSS swaps in the .frig-fallback block instead."""
    if f["mode"] == "refi":
        cap = "Estimated monthly savings"
        sliders = f"""
      <div class="fslider">
        <div class="flabel"><label for="f-pay">Your current monthly payment (P&amp;I)</label><output data-for="pay" for="f-pay">$1,850</output></div>
        <input type="range" id="f-pay" data-var="pay" data-fmt="money" min="500" max="4000" step="25" value="1850" aria-label="Your current monthly principal and interest payment, dollars">
        <p class="fhint">Principal &amp; interest &mdash; the part before taxes and insurance.</p>
      </div>
      <div class="fslider">
        <div class="flabel"><label for="f-cur">Your current rate</label><output data-for="cur" for="f-cur">6.875%</output></div>
        <input type="range" id="f-cur" data-var="cur" data-fmt="pct" min="3" max="9" step="0.125" value="6.875" aria-label="Your current interest rate, percent">
        <p class="fhint">It's on page one of your statement.</p>
      </div>
      <details class="fbal" data-balance>
        <summary>Know your balance? Dial it in for a tighter estimate</summary>
        <div class="fslider">
          <div class="flabel"><label for="f-bal">Loan balance</label><output data-for="bal" for="f-bal">$250,000</output></div>
          <input type="range" id="f-bal" data-var="bal" data-fmt="money" min="50000" max="800000" step="5000" value="250000" aria-label="Your current loan balance, dollars">
        </div>
      </details>"""
    else:
        pmin, pmax, pval, pstep = f["price"]
        dmin, dmax, dval, dstep = f["down"]
        cap = "Estimated monthly payment (P&amp;I)"
        sliders = f"""
      <div class="fslider">
        <div class="flabel"><label for="f-price">Home price</label><output data-for="price" for="f-price">${pval:,}</output></div>
        <input type="range" id="f-price" data-var="price" data-fmt="money" min="{pmin}" max="{pmax}" step="{pstep}" value="{pval}" aria-label="Home price, dollars">
      </div>
      <div class="fslider">
        <div class="flabel"><label for="f-down">Down payment</label><output data-for="down" for="f-down">{dval:g}%</output></div>
        <input type="range" id="f-down" data-var="down" data-fmt="pct" min="{dmin}" max="{dmax}" step="{dstep}" value="{dval}" aria-label="Down payment, percent of price">
      </div>"""

    return f"""<section class="frig-wrap" id="estimator"><div class="wrap">
<div class="frig" data-funnel data-mode="{f["mode"]}" data-slug="{slug}">
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>The estimator</p>
  <h2>{f["rig_h2"]}</h2>
  <p class="sub">{f["rig_sub"]}</p>
  <div class="frig-live">
    <div class="fresult">
      <p class="fcap">{cap}</p>
      <p class="fnum" data-out>&mdash;</p>
      <p class="fsub" data-out-sub></p>
      <p class="fnote">{FUNNEL_FOOTNOTE}</p>
      <p class="fsample" data-sample-label></p>
      <span class="sr-only" role="status" aria-live="polite" data-out-live></span>
      <div class="yesrow">
        <p class="yesq">{"Do you want this saving?" if f["mode"] == "refi" else "Want to see your real number?"}</p>
        <button type="button" class="btn-yes" data-yes-btn>{"YES &mdash; I want <span data-yes-amount>this</span>/mo back" if f["mode"] == "refi" else "YES &mdash; run my real numbers"} <span class="arrow">&rarr;</span></button>
        <p class="yessmall">30 seconds. No credit inquiry at this step. One call from a licensed loan officer.</p>
      </div>
    </div>
    <div class="fsliders">{sliders}
    </div>
  </div>
  <div class="frig-fallback">
    <p>The interactive estimator needs JavaScript &mdash; but the people don't.
    A licensed loan officer can run your real numbers on one call.</p>
    <a class="btn go" href="tel:{PHONE_HREF}">Call {PHONE}</a>
    <p class="fnote" style="max-width:52ch;margin-inline:auto">{FUNNEL_FOOTNOTE}</p>
  </div>
</div>
</div></section>"""


def _funnel_towns(slug, f):
    """USDA only: static list of known-eligible East Texas area names.
    Deliberately not an eligibility API — the real check is by exact address."""
    if not f.get("towns"):
        return ""
    chips = "".join(
        f'<button type="button" data-town="{esc(t)}" aria-pressed="false">{esc(t)}</button>'
        for t in f["towns"])
    return f"""<section class="frig-wrap" id="towns"><div class="wrap">
<div class="frig">
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>The map</p>
  <h2>{f["towns_h2"]}</h2>
  <p class="sub">{f["towns_sub"]}</p>
  <div class="townchips" data-town-picker>{chips}</div>
  <p class="townout" data-town-out aria-live="polite">Tap a town to see where it stands.</p>
  <p class="fsample">Area names listed because homes there commonly qualify &mdash; USDA
  eligibility is set by exact address and current USDA maps, so nothing here is a
  determination. We check the actual property with you.</p>
</div>
</div></section>"""


def _funnel_yes(slug, f):
    """The YES moment's landing spot: a walk-through card that already knows
    their dials. funnel.js keeps the hidden fields and recap chips synced with
    the estimator, so what they played with is what the loan officer sees.
    Posts through forms.js to the existing submit-lead Edge Function."""
    refi = f["mode"] == "refi"
    if refi:
        facts = ('<span class="yfact">You pay<b data-yes-fact="pay">&mdash;</b></span>'
                 '<span class="yfact">Your rate<b data-yes-fact="cur">&mdash;</b></span>'
                 '<span class="yfact">Estimated saving<b data-yes-fact="saving">&mdash;</b></span>')
        hidden = ('<input type="hidden" name="current_payment" value="">'
                  '<input type="hidden" name="current_rate" value="">'
                  '<input type="hidden" name="mortgage_balance" value="">'
                  '<input type="hidden" name="estimated_monthly_savings" value="">'
                  '<input type="hidden" name="goal" value="refinance">')
        h2 = "Yes? Then let&rsquo;s make it real."
        sub = ("Thirty seconds. Your dials ride along with it, a licensed loan officer "
               "checks them against your actual loan, and you get one call &mdash; not a "
               "call center.")
        btn = 'YES &mdash; I want <span data-yes-amount>this</span>/mo back <span class="arrow">&rarr;</span>'
        nxt = f"""<div class="yesnext">
  <h3>That&rsquo;s a YES. Here&rsquo;s how to make it fast.</h3>
  <p>A licensed loan officer picks this up and calls once &mdash; usually same day.
  Two ways to speed it up while you're here:
  <a href="#cta">send your statement now</a> (it has every number we need), or jump
  straight into <a href="{LOS_APPLY}" rel="noopener">the full secure application</a>
  if you already know you're in.</p>
</div>"""
    else:
        facts = ('<span class="yfact">Home price<b data-yes-fact="price">&mdash;</b></span>'
                 '<span class="yfact">Down payment<b data-yes-fact="down">&mdash;</b></span>'
                 '<span class="yfact">Estimated payment<b data-yes-fact="pi">&mdash;</b></span>')
        hidden = ('<input type="hidden" name="home_price" value="">'
                  '<input type="hidden" name="down_payment_pct" value="">'
                  '<input type="hidden" name="estimated_payment" value="">'
                  '<input type="hidden" name="goal" value="purchase">')
        h2 = "Like that number? Let&rsquo;s check it for real."
        sub = ("Thirty seconds. Your dials ride along, and a licensed loan officer runs "
               "your actual numbers &mdash; credit, income, program &mdash; and calls "
               "once with real answers.")
        btn = 'YES &mdash; run my real numbers <span class="arrow">&rarr;</span>'
        nxt = f"""<div class="yesnext">
  <h3>That&rsquo;s a YES. Here&rsquo;s what happens next.</h3>
  <p>A licensed loan officer calls within one business day &mdash; once, not six times
  in an hour. Want to move faster? Call <a href="tel:{PHONE_HREF}">{PHONE}</a> now, or
  start <a href="{LOS_APPLY}" rel="noopener">the full secure application</a>.</p>
</div>"""

    return f"""<section class="yeswrap alt" id="yes"><div class="wrap">
<p class="eyebrow" style="text-align:center;justify-content:center"><span class="tick" aria-hidden="true"></span>The next step</p>
<h2 style="text-align:center;margin-inline:auto">{h2}</h2>
<p class="sub" style="text-align:center;margin-inline:auto;max-width:52ch">{sub}</p>
<div class="yescard">
  <div class="yesbeats"><span>1 &middot; Your numbers ride along</span><span>2 &middot; 30 seconds of contact info</span><span>3 &middot; One call from a licensed loan officer</span></div>
  <div class="yesfacts" aria-label="What you set on the estimator">{facts}</div>
  <form data-yes-form data-glm-form="funnel_yes" data-glm-keep novalidate>
    <input type="hidden" name="loan_type" value="{slug}">
    {hidden}
    <div class="yesfields">
      <div class="frow">
        <div class="field"><label for="y-name">Your name</label>
          <input id="y-name" name="name" type="text" autocomplete="name" required maxlength="120">
          <p class="err">Please enter your name.</p></div>
        <div class="field"><label for="y-phone">Phone</label>
          <input id="y-phone" name="phone" type="tel" autocomplete="tel" required maxlength="32">
          <p class="err">Please enter a phone number.</p></div>
      </div>
      <div class="field"><label for="y-email">Email</label>
        <input id="y-email" name="email" type="email" autocomplete="email" required maxlength="254">
        <p class="err">Please enter a valid email.</p></div>
      <div class="consent">
        <input type="checkbox" id="y-tcpa" name="tcpa_consent" value="yes">
        <label for="y-tcpa">{TCPA_TEXT}</label>
      </div>
      <button class="btn-yes" type="submit" data-funnel-cta="yes_submit">{btn}</button>
      <p class="formstatus" role="status" aria-live="polite"></p>
      <p class="disclose">Sending this is not an application for credit and is
      <strong>not a commitment to lend</strong>. No credit inquiry happens at this step.
      Your estimate is only an estimate &mdash; a licensed loan officer confirms real
      figures after a complete application, subject to credit approval and underwriting.</p>
    </div>
    {nxt}
  </form>
</div>
</div></section>"""


def _funnel_why(slug, f):
    """Refi pages: why the swap makes sense — benefit cards plus the live
    36-month recoupment meter, fed by the estimator's dials."""
    w = f.get("why")
    if not w:
        return ""
    ticks = "".join(f"<li><strong>{t}</strong> {b}</li>" for t, b in w["ticks"])
    va_attr = " data-va" if w.get("va") else ""
    return f"""<section id="why"><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Why this works</p>
<h2>{w["h2"]}</h2>
<p class="sub">{w["sub"]}</p>
<div class="whygrid">
<div><ul class="ticks">{ticks}</ul></div>
<div>
  <div class="recoupcard" data-recoup{va_attr}>
    <h3>The 36-month test, live</h3>
    <p class="rc-sub">Your dials, plus a sample cost allowance{" and the 0.5% VA funding fee" if w.get("va") else ""}.
    Real costs come from a real loan estimate.</p>
    <div class="recoupbar"><div class="fill"></div><span class="cap36" aria-hidden="true"></span></div>
    <p class="recoupread">About <b data-recoup-months>&mdash;</b> months to break even
    &mdash; the rule allows 36.</p>
    <p class="recoupverdict" data-recoup-verdict aria-live="polite"></p>
    <p class="fnote">{FUNNEL_FOOTNOTE}</p>
  </div>
</div>
</div>
</div></section>"""


def _funnel_steps(f):
    steps = "".join(
        f"""<div class="step"><h3>{s[0]}</h3><p>{s[1]}</p>
<a class="microcta" href="{s[2][0].replace("__PHONE__", PHONE_HREF)}"{' data-funnel-cta="step_call"' if s[2][0].startswith("tel:") else ""}>{s[2][1]} {ARROW}</a></div>"""
        for s in f["steps"])
    return f"""<section><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>How this works</p>
<h2>Three steps. No fluff.</h2>
<div class="steps fsteps">{steps}</div>
</div></section>"""


def _funnel_objections(f):
    cards = "".join(
        f'<div class="card reveal"><span class="num">0{i+1}</span><h3>{o[0]}</h3><p>{o[1]}</p></div>'
        for i, o in enumerate(f["objections"]))
    return f"""<section class="alt"><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>The honest part</p>
<h2>What's actually stopping you?</h2>
<div class="grid g3">{cards}</div>
</div></section>"""


def _funnel_proof():
    """Two verified reviews + the trust marks. Verified only — a funnel page is
    the last place to lean on wording we have not re-checked at its source."""
    quotes = "".join(review_card(r, cls="reveal") for r in REVIEWS[:2])
    return f"""<section><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>East Texas talks</p>
<h2>People we've already walked home.</h2>
<div class="grid g2">{quotes}</div>
<div class="trustrow fproof-trust">
  <div class="trust">{MARK_EHO}<span><strong>Equal Housing Opportunity</strong></span></div>
  <div class="trust">{MARK_NMLS}<span><strong>NMLS #{NMLS_CO}</strong><small>Kenneth Travis, NMLS #{NMLS_KT}</small></span></div>
  <div class="trust">{MARK_LANTERN}<span><strong>{POWERED}</strong></span></div>
</div>
</div></section>"""


def _funnel_bigband(slug, f):
    """The Big Button. ONE action: refi pages take the statement right here;
    purchase pages put a phone number and a callback form behind one button."""
    if f["mode"] == "refi":
        action = f"""
<div class="fupload" data-statement-upload>
  <label class="fuppick">
    <input type="file" accept="application/pdf,image/jpeg,image/png,image/heic,image/webp">
    <strong>Choose your statement</strong> &mdash; a PDF from your servicer, or a photo of page one
    <span data-upload-picked></span>
  </label>
  <button type="button" class="btn go xl" data-upload-btn data-big-cta
          data-short-label="Send my statement" data-funnel-cta="statement_send">{f["cta_label"]} &rarr;</button>
  <p class="fupstatus" data-upload-status role="status" aria-live="polite"></p>
  <p class="bandnote">Sent over an encrypted connection and visible only to our licensed
  team. Sending a statement starts a conversation &mdash; it is not an application for
  credit and <strong>not a commitment to lend</strong>.</p>
</div>
<noscript><p class="bandalt">The upload needs JavaScript &mdash; call
<a href="tel:{PHONE_HREF}">{PHONE}</a> or start at <a href="/apply">glmtg.com/apply</a> instead.</p></noscript>
<p class="bandalt">Rather talk first? Call <a href="tel:{PHONE_HREF}" data-funnel-cta="band_call">{PHONE}</a>.</p>"""
    else:
        action = f"""
<a class="btn go xl" href="tel:{PHONE_HREF}" data-big-cta
   data-short-label="Let&rsquo;s run my real numbers" data-funnel-cta="call">{f["cta_label"]} &rarr;</a>
<p class="bandalt">Or have us call you &mdash; one call, no spam:</p>
<form class="fcallback" data-glm-form="funnel_callback" novalidate>
  <input type="hidden" name="loan_type" value="{slug}">
  <div class="frow">
    <div class="field"><label class="sr-only" for="cb-name">Your name</label>
      <input id="cb-name" name="name" type="text" autocomplete="name" placeholder="Your name" required maxlength="120"></div>
    <div class="field"><label class="sr-only" for="cb-phone">Phone number</label>
      <input id="cb-phone" name="phone" type="tel" autocomplete="tel" placeholder="Phone number" required maxlength="32"></div>
  </div>
  <div class="consent">
    <input type="checkbox" id="cb-tcpa" name="tcpa_consent" value="yes">
    <label for="cb-tcpa">{TCPA_TEXT}</label>
  </div>
  <button class="btn onDark" type="submit" data-funnel-cta="callback_submit">Request a callback</button>
  <p class="formstatus" role="status" aria-live="polite"></p>
</form>"""

    return f"""<section class="band-wrap bigband" id="cta"><div class="wrap"><div class="ctaband">
<span class="signal" aria-hidden="true"><i></i><i></i><i></i></span>
<h2>{f["cta_head"]}</h2>
<p>{f["cta_sub"]}</p>
{action}
<p class="bandnote">Not a commitment to lend. Subject to credit approval and underwriting.
Only a licensed loan officer can confirm your rate, payment, or eligibility, after a
complete application.</p>
</div></div></section>"""


def funnel_body(slug, faqs):
    """Assemble a complete funnel page body: hook hero, slider rig, three
    steps, objection cards, proof, the Big Button, and the page's FAQ."""
    f = FUNNEL[slug]
    faq_html = "".join(
        f'<details><summary>{esc(q)}</summary><div class="a"><p>{esc(a)}</p></div></details>'
        for q, a in faqs)
    return "".join([
        _funnel_hero(slug, f),
        _funnel_rig(slug, f),
        _funnel_towns(slug, f),
        _funnel_why(slug, f),
        _funnel_yes(slug, f),
        _funnel_steps(f),
        _funnel_objections(f),
        _funnel_proof(),
        _funnel_bigband(slug, f),
        f"""<section id="faq"><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>Questions</p>
<h2>Straight answers</h2>
<div class="faq">{faq_html}</div>
</div></section>""",
    ])


# Scripts every funnel page loads (beyond the base chrome). forms.js handles
# the purchase callback form; harmless on refi pages, so it ships everywhere
# for one less thing to vary.
FUNNEL_SCRIPTS = ('<script src="/forms.js" defer></script>'
                  '<script src="/assets/rates.js" defer></script>'
                  '<script src="/assets/funnel.js" defer></script>')
