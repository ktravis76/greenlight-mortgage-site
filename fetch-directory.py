#!/usr/bin/env python3
"""Pull the Longview real-estate professional archive out of Supabase into a
local JSON cache, so the page build stays offline and dependency-free.

    python3 fetch-directory.py       ->  data/directory.json

Reads through the public REST API with the publishable key, which can only see
rows where status = 'published' — the same view a visitor's browser would get.
Re-run it whenever the directory changes; commit the JSON so a build never needs
network access.
"""
import json
import os
import urllib.request

URL = "https://athovwknbwbbqworsbrm.supabase.co/rest/v1"
KEY = "sb_publishable_2ajY5o6EJyVEiNpWD_HL0Q_3HLzxmXr"

FIELDS = ("slug,name,tagline,write_up,year_founded,owner_name,address,city,state,zip,"
          "phone,email,website,socials,category_id,status,verified_at")


def get(path):
    req = urllib.request.Request(
        f"{URL}/{path}",
        headers={"apikey": KEY, "Authorization": f"Bearer {KEY}",
                 "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main():
    cats = get("categories?select=id,slug,name,description&order=name")
    biz = get(f"businesses?select={FIELDS}&status=eq.published&order=name&limit=1000")

    by_id = {c["id"]: c for c in cats}
    for b in biz:
        cat = by_id.get(b.pop("category_id"))
        b["category"] = cat["slug"] if cat else None

    # Drop categories that ended up with nothing published — an empty category
    # page is a thin page, and thin pages are the opposite of the point here.
    used = {b["category"] for b in biz}
    cats = [c for c in cats if c["slug"] in used]

    out = {"categories": cats, "businesses": biz}
    os.makedirs("data", exist_ok=True)
    with open("data/directory.json", "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)

    print(f"  {len(cats)} categories, {len(biz)} businesses -> data/directory.json")
    missing_phone = sum(1 for b in biz if not b.get("phone"))
    missing_site = sum(1 for b in biz if not b.get("website"))
    print(f"  {missing_phone} without a phone, {missing_site} without a website")

    # Data quality: an out-of-state area code on a Longview listing usually means
    # the record was scraped from a national directory. Worth a look, not a block.
    odd = [b["name"] for b in biz
           if b.get("phone") and not any(
               a in b["phone"] for a in ("903", "430", "214", "469", "972", "817", "682"))]
    if odd:
        print(f"  {len(odd)} with a non-East-Texas area code: {', '.join(odd[:6])}"
              + (" …" if len(odd) > 6 else ""))


if __name__ == "__main__":
    main()
