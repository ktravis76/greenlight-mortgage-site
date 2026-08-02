#!/usr/bin/env python3
"""Generates the Longview real-estate professional archive.

    /archive                      hub, all 20 categories
    /archive/<category>           every business in that trade
    /archive/<category>/<slug>    the individual listing

Data comes from data/directory.json — refresh it with `python3 fetch-directory.py`.

WHY THIS IS ON THE MORTGAGE SITE
Two reasons, and the second is the real one.

1. It is genuinely useful. Someone buying a house in Longview needs an inspector,
   an appraiser, a title company, a roofer and an insurance agent, usually in
   that order and usually in a hurry.
2. It is 161 pages of local content on a domain with roughly ten indexed pages,
   competing against brokers with fifty or more. Every listing is a page that can
   rank for a Longview trade search, and every professional in it is someone
   Greenlight wants referring business back.

EDITORIAL POSITION: these are independent businesses, not partners, not paid
placements, and not vetted by Greenlight. The pages say so. Implying a lender has
endorsed a contractor it has no relationship with is both untrue and the kind of
thing that becomes somebody's complaint later.
"""
import json
import os
import re

import sitegen as S

ARROW = S.ARROW


def write(path, html_out):
    rel = path.strip("/") + "/index.html"
    os.makedirs(os.path.dirname(rel), exist_ok=True)
    with open(rel, "w") as f:
        f.write(html_out)
    return len(html_out)


def load():
    with open("data/directory.json") as f:
        return json.load(f)


def tel(phone):
    return re.sub(r"[^0-9]", "", phone or "")


def host(url):
    return re.sub(r"^https?://(www\.)?", "", url or "").rstrip("/")


DISCLAIMER = (
    "Listings in this archive are independent local businesses. They are not "
    "affiliated with, endorsed by, vetted by, or paying Greenlight Mortgage for "
    "inclusion, and no listing here is a recommendation. Details are compiled from "
    "public sources and may be out of date &mdash; check with the business directly. "
    "If your business is listed and you would like it corrected or removed, tell us "
    "and we will do it."
)

# One mark per trade, reusing the shared icon vocabulary rather than inventing
# twenty new glyphs nobody will look at closely.
CAT_ACCENT = {
    "real-estate-brokers": "#0f7a4d", "real-estate-attorneys": "#7a4fa3",
    "title-companies": "#1f8fa8", "home-inspectors": "#8a6d1f",
    "appraisers": "#2f8f3f", "insurance-agents": "#1f8fa8",
    "mortgage-lenders": "#0f7a4d", "custom-builders": "#8a6d1f",
    "home-builders": "#8a6d1f", "roofing": "#a34f4f",
    "foundation-repair": "#6b5b3f", "hvac": "#1f8fa8",
    "plumbing": "#1f6fa8", "electrical": "#a3862f",
    "landscaping-outdoor": "#2f8f3f", "moving-storage": "#5b6b7a",
    "cleaning-make-ready": "#2f8f8f", "property-management": "#0f7a4d",
    "staging-photography": "#a34f7a", "surveyors": "#6b7a3f",
}


def accent(slug):
    return CAT_ACCENT.get(slug, "#0f7a4d")


# ---------------------------------------------------------------------- cards

def biz_card(b, cat_slug):
    bits = []
    if b.get("phone"):
        bits.append(f'<span>{S.esc(b["phone"])}</span>')
    if b.get("year_founded"):
        bits.append(f'<span>Since {b["year_founded"]}</span>')
    meta = " &middot; ".join(bits)
    return (f'<a class="lcard" href="/archive/{cat_slug}/{b["slug"]}" '
            f'style="--accent:{accent(cat_slug)}">'
            f'<h3>{S.esc(b["name"])}</h3>'
            f'<p>{S.esc(b.get("tagline") or "")}</p>'
            f'{f"<p class=bmeta>{meta}</p>" if meta else ""}'
            f'<span class="go">Details {ARROW}</span></a>')


# ------------------------------------------------------------------ hub page

def hub(cats, biz):
    by_cat = {}
    for b in biz:
        by_cat.setdefault(b["category"], []).append(b)

    cards = "".join(
        f'<a class="lcard" href="/archive/{c["slug"]}" style="--accent:{accent(c["slug"])}">'
        f'<span class="who">{len(by_cat.get(c["slug"], []))} listed</span>'
        f'<h3>{S.esc(c["name"])}</h3>'
        f'<p>{S.esc(c.get("description") or "")}</p>'
        f'<span class="go">Browse {ARROW}</span></a>'
        for c in cats)

    body = f"""{S.hero(
        eyebrow="The Longview archive",
        h1="Everyone you need to buy a house here",
        lede=f"{len(biz)} real estate professionals across {len(cats)} trades in Longview "
             "and East Texas &mdash; inspectors, appraisers, title companies, roofers, "
             "attorneys, builders and the rest. Free to browse, nothing gated.",
        ctas=[("/archive#categories", "Browse the trades", "go"),
              ("/contact", "Suggest a business", "ghost")],
        trail=[("/", "Home"), (None, "Archive")])}

<section id="categories"><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>{len(cats)} trades</p>
<h2>Start with what you need.</h2>
<p class="sub">Closing on a house takes more people than anyone expects. This is the list we
keep because we work with this market every week.</p>
<div class="lgrid">{cards}</div>
</div></section>

<section class="dark"><div class="wrap">
<div class="split">
<div>
  <p class="eyebrow"><span class="tick" aria-hidden="true"></span>Why we built it</p>
  <h2>Because we get asked ten times a week.</h2>
  <p class="sub">&ldquo;Do you know a good inspector?&rdquo; &ldquo;Who does foundation work
  around here?&rdquo; &ldquo;Which title company is quickest?&rdquo; We answer those calls
  anyway. This is the answer, written down and free to anybody.</p>
  <p class="sub">It also happens to be how we would like to be treated by the other
  professionals in this town &mdash; useful first, and asking for nothing.</p>
</div>
<div>
  <div class="callout">
    <h3>These are not our partners</h3>
    <p>Nobody paid to be in here and nobody is endorsed by us. It is a list of businesses that
    exist and serve this area, compiled from public sources. Do your own checking before you
    hire anyone.</p>
  </div>
  <div class="callout">
    <h3>Own one of these?</h3>
    <p>If a listing is wrong, out of date, or you would rather not be included, tell us and
    we will fix it or take it down.</p>
  </div>
</div>
</div>
</div></section>

{S.cta_band(head="While you are here.",
            sub="If a house is what all these people are for, the financing is the part we "
                "actually do. Two minutes for a real number.")}
"""
    return S.page(
        path="/archive",
        title=f"Longview TX Real Estate Professionals — {len(biz)} Local Businesses | Greenlight Mortgage",
        desc=f"A free directory of {len(biz)} real estate professionals in Longview and East "
             f"Texas: inspectors, appraisers, title companies, roofers, attorneys, builders "
             f"and more. Compiled by Greenlight Mortgage. Equal Housing Opportunity.",
        body=body,
        trail=[("/", "Home"), ("/archive", "Archive")],
    )


# ------------------------------------------------------------- category page

def category_page(c, items):
    cards = "".join(biz_card(b, c["slug"]) for b in items)
    body = f"""{S.hero(
        eyebrow="Longview archive",
        h1=S.esc(c["name"]) + " in Longview, TX",
        lede=S.esc(c.get("description") or "")
             or f"{len(items)} businesses serving Longview and East Texas.",
        trail=[("/", "Home"), ("/archive", "Archive"), (None, c["name"])])}

<section><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>{len(items)} listed</p>
<h2>{S.esc(c["name"])}</h2>
<div class="lgrid">{cards}</div>
<p class="disclose">{DISCLAIMER}</p>
</div></section>

{S.cta_band()}
"""
    return S.page(
        path=f"/archive/{c['slug']}",
        title=f"{c['name']} in Longview, TX — {len(items)} Local Businesses | Greenlight Mortgage",
        desc=(c.get("description") or
              f"{len(items)} {c['name'].lower()} serving Longview and East Texas.")[:300],
        body=body,
        trail=[("/", "Home"), ("/archive", "Archive"), (f"/archive/{c['slug']}", c["name"])],
    )


# ------------------------------------------------------------- listing page

def business_page(b, c):
    rows = []
    if b.get("address"):
        loc = ", ".join(x for x in [b.get("address"), b.get("city"),
                                    f'{b.get("state","")} {b.get("zip","")}'.strip()] if x)
        rows.append(("Address", S.esc(loc)))
    if b.get("phone"):
        rows.append(("Phone", f'<a href="tel:{tel(b["phone"])}">{S.esc(b["phone"])}</a>'))
    if b.get("website"):
        rows.append(("Website", f'<a href="{S.esc(b["website"])}" rel="nofollow noopener" '
                                f'target="_blank">{S.esc(host(b["website"]))} &nearr;</a>'))
    if b.get("year_founded"):
        rows.append(("Founded", str(b["year_founded"])))
    if b.get("owner_name"):
        rows.append(("Owner", S.esc(b["owner_name"])))

    detail = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows)

    schema = (
        '{"@context":"https://schema.org","@type":"LocalBusiness","name":%s,'
        '"description":%s,"address":{"@type":"PostalAddress","streetAddress":%s,'
        '"addressLocality":%s,"addressRegion":%s,"postalCode":%s,"addressCountry":"US"}%s%s}'
    ) % (S.jstr(b["name"]), S.jstr(b.get("tagline") or ""), S.jstr(b.get("address") or ""),
         S.jstr(b.get("city") or "Longview"), S.jstr(b.get("state") or "TX"),
         S.jstr(b.get("zip") or ""),
         f',"telephone":{S.jstr(b["phone"])}' if b.get("phone") else "",
         f',"url":{S.jstr(b["website"])}' if b.get("website") else "")

    # Attributed, and marked as third-party prose.
    #
    # Some of these descriptions repeat the business's own marketing — "100%
    # satisfaction guarantee", "fixed right or it's free". Those are claims that
    # company makes about itself. Publishing them unattributed on a lender's site
    # reads as Greenlight vouching for them, which we explicitly are not. The
    # attribution line makes whose claim it is unambiguous, and data-thirdparty
    # tells check.py to hold this block to a different standard than our own copy.
    write_up = (
        f'<p class="attrib">How {S.esc(b["name"])} describes itself, from public sources:</p>'
        f'<blockquote class="thirdparty" data-thirdparty>{S.esc(b["write_up"])}</blockquote>'
    ) if b.get("write_up") else ""

    body = f"""{S.hero(
        eyebrow=S.esc(c["name"]),
        h1=S.esc(b["name"]),
        lede=S.esc(b.get("tagline") or ""),
        trail=[("/", "Home"), ("/archive", "Archive"),
               (f"/archive/{c['slug']}", c["name"]), (None, b["name"])])}

<section><div class="wrap">
<div class="split">
<div class="prose" style="max-width:none">
  {write_up}
  <p class="disclose">{DISCLAIMER}</p>
</div>
<div>
  <div class="estcard">
    <h2 style="font-size:22px">Contact</h2>
    <div class="tablewrap" style="margin-top:16px">
      <table class="deets"><tbody>{detail or '<tr><td>No contact details on file.</td></tr>'}</tbody></table>
    </div>
  </div>
  <div class="callout">
    <h3>Buying or selling in Longview?</h3>
    <p>Whoever you hire from this list, the financing still has to work. Two minutes for a
    real number, no hard credit pull.</p>
    <p style="margin-top:12px"><a href="/tools/estimate"
      style="color:var(--g);font-weight:700">See what you could save {ARROW}</a></p>
  </div>
</div>
</div>
</div></section>

<section class="alt"><div class="wrap">
<p class="eyebrow"><span class="tick" aria-hidden="true"></span>More in this trade</p>
<h2>Other {S.esc(c["name"].lower())} nearby</h2>
<div class="cta"><a class="btn ghost" href="/archive/{c['slug']}">
See all {S.esc(c["name"].lower())} {ARROW}</a>
<a class="btn ghost" href="/archive">Browse the whole archive</a></div>
</div></section>
"""
    return S.page(
        path=f"/archive/{c['slug']}/{b['slug']}",
        title=f"{b['name']} — {c['name']} in {b.get('city') or 'Longview'}, TX | Greenlight Mortgage",
        desc=(b.get("tagline") or b.get("write_up") or b["name"])[:300],
        body=body,
        trail=[("/", "Home"), ("/archive", "Archive"),
               (f"/archive/{c['slug']}", c["name"]),
               (f"/archive/{c['slug']}/{b['slug']}", b["name"])],
        extra_schema=schema,
    )


def build():
    data = load()
    cats, biz = data["categories"], data["businesses"]
    by_cat = {}
    for b in biz:
        by_cat.setdefault(b["category"], []).append(b)
    cat_by_slug = {c["slug"]: c for c in cats}

    print("archive")
    n = write("/archive", hub(cats, biz))
    print(f"  archive/index.html  ({n:,} bytes)")

    pages = 1
    for c in cats:
        items = by_cat.get(c["slug"], [])
        write(f"/archive/{c['slug']}", category_page(c, items))
        pages += 1
        for b in items:
            write(f"/archive/{c['slug']}/{b['slug']}", business_page(b, cat_by_slug[b["category"]]))
            pages += 1
    print(f"  {len(cats)} category pages + {len(biz)} listings  ({pages} total)")


if __name__ == "__main__":
    build()
