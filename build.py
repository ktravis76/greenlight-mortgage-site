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

# Priority hints. The estimator is the primary CTA across the whole site, so it
# sits with the homepage rather than in with the legal pages.
PRIORITY = {
    "/": "1.0",
    "/tools/estimate": "0.9",
    "/loans": "0.9",
    "/loans/va": "0.9",
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
        f"<priority>{PRIORITY.get(u, '0.6')}</priority></url>"
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


def main():
    for mod in ("build-loans", "build-pages", "build-tools"):
        load(mod).build()

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
