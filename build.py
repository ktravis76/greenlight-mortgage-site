#!/usr/bin/env python3
"""Build the whole site.

    python3 build.py

Runs the three generators, then writes sitemap.xml and robots.txt from the pages
that were actually produced — so the sitemap cannot list a page that does not
exist, which is the usual way these drift.
"""
import datetime
import importlib
import os
import subprocess
import sys

import sitegen as S

HERE = os.path.dirname(os.path.abspath(__file__))

# Pages that exist but should stay out of the index. Keep this list short and
# justified — anything here is a page we are choosing not to rank.
NOINDEX = {
    "/survey",              # feedback form, no search value
    "/tools/va-refi-screener",   # internal sales tool, not for consumers
}

# The archive is the bulk of the site's indexable surface — 161 pages against a
# domain that currently has about ten indexed. Listings sit below the money
# pages but well above nothing.
ARCHIVE_PRIORITY = "0.5"

# Priority hints. The estimator is the primary CTA across the whole site, so it
# sits with the homepage rather than in with the legal pages.
PRIORITY = {
    "/": "1.0",
    "/tools/estimate": "0.9",
    "/pros": "0.8",
    "/tools/affordability": "0.8",
    "/tools/net-proceeds": "0.8",
    "/tools/rent-vs-buy": "0.7",
    "/buy": "0.9",
    "/loans": "0.9",
    "/loans/va": "0.9",
    "/loans/va-irrrl": "0.9",
    "/why-a-broker": "0.8",
    "/contact": "0.8",
    "/about": "0.8",
}


def load(modname):
    """build-loans.py etc. are not importable by name because of the hyphen."""
    import importlib.util
    path = os.path.join(HERE, modname + ".py")
    spec = importlib.util.spec_from_file_location(modname.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def discover():
    """Every index.html in the tree, as a site URL."""
    urls = []
    for root, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs
                   if d not in {".git", "assets", "supabase", "db", "__pycache__"}]
        if "index.html" not in files:
            continue
        rel = os.path.relpath(root, HERE)
        urls.append("/" if rel == "." else "/" + rel.replace(os.sep, "/"))
    return sorted(set(urls))


def sitemap(urls):
    today = datetime.date.today().isoformat()
    body = "\n".join(
        f"  <url><loc>{S.ORIGIN}{'' if u == '/' else u}</loc>"
        f"<lastmod>{today}</lastmod>"
        f"<priority>{PRIORITY.get(u, ARCHIVE_PRIORITY if u.startswith('/archive/') else '0.6')}</priority></url>"
        for u in urls if u not in NOINDEX)
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           f"{body}\n</urlset>\n")
    with open(os.path.join(HERE, "sitemap.xml"), "w") as f:
        f.write(xml)
    return len([u for u in urls if u not in NOINDEX])


def robots():
    txt = f"""# {S.COMPANY} — {S.ORIGIN}
User-agent: *
Allow: /

# Feedback form and the internal sales tool have no business in search results.
Disallow: /survey
Disallow: /tools/va-refi-screener

Sitemap: {S.ORIGIN}/sitemap.xml
"""
    with open(os.path.join(HERE, "robots.txt"), "w") as f:
        f.write(txt)


def prune(expected):
    """Delete generated pages nothing produces any more.

    Renaming a page used to leave the old directory behind, still served and
    still in the sitemap — /learn/closing-costs-itemised outlived its British
    spelling by exactly one build. Anything under a generated path that this
    run did not write gets removed.
    """
    keep = {os.path.normpath(os.path.join(HERE, "index.html"))}
    for u in expected:
        rel = "index.html" if u == "/" else u.strip("/") + "/index.html"
        keep.add(os.path.normpath(os.path.join(HERE, rel)))

    removed = []
    for root, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs
                   if d not in {".git", "assets", "supabase", "db", "__pycache__", "data"}]
        for fn in files:
            if fn != "index.html":
                continue
            full = os.path.normpath(os.path.join(root, fn))
            if full not in keep:
                os.remove(full)
                removed.append(os.path.relpath(full, HERE))
                try:
                    os.rmdir(root)
                except OSError:
                    pass
    return removed


def main():
    for mod in ("build-loans", "build-pages", "build-tools", "build-archive", "build-pros", "build-guides"):
        load(mod).build()

    urls = discover()
    stale = prune(urls)
    if stale:
        print(f"\npruned {len(stale)} stale page(s): " + ", ".join(stale[:5]))
        urls = discover()
    n = sitemap(urls)
    robots()
    print(f"\nsitemap.xml  ({n} urls)  ·  robots.txt")
    print(f"{len(urls)} pages total")

    # The link check is not optional. A previous pass shipped nav pointing at
    # /loans/va while the files were at /loans/va.html and every link 404'd.
    print()
    rc = subprocess.call([sys.executable, os.path.join(HERE, "check.py")])
    sys.exit(rc)


if __name__ == "__main__":
    main()
