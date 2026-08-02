#!/usr/bin/env python3
"""Pre-flight checks. Exits non-zero if anything fails.

    python3 check.py

Two gates:

1. LINKS. Every internal href and src is resolved against the built tree, the
   way Vercel would serve it. A previous pass shipped nav pointing at /loans/va
   while the files sat at /loans/va.html, and every link on the site 404'd. That
   is the specific failure this exists to make impossible to repeat.

2. COMPLIANCE. Greps the rendered HTML for language that must never appear on a
   consumer mortgage page — guarantees, superlative rate claims, and stated APR
   or rate figures. Checks the required disclosures are present on every page.

Neither gate is advisory. Do not report the site as done until this is clean.
"""
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = {".git", "assets", "supabase", "db", "__pycache__", "node_modules"}

RED = "\033[31m"; YEL = "\033[33m"; GRN = "\033[32m"; DIM = "\033[2m"; OFF = "\033[0m"


def pages():
    for root, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if fn.endswith(".html"):
                yield os.path.join(root, fn)


def url_of(path):
    rel = os.path.relpath(path, HERE)
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("/index.html")]
    return "/" + rel[:-len(".html")]


# ---------------------------------------------------------------- link check

REF = re.compile(r'(?:href|src)\s*=\s*"([^"]+)"', re.I)


def resolves(target):
    """Would Vercel serve this? Mirrors static-hosting resolution order."""
    t = target.split("#")[0].split("?")[0]
    if not t or t == "/":
        return os.path.exists(os.path.join(HERE, "index.html"))
    p = t.lstrip("/")
    candidates = [
        os.path.join(HERE, p),                    # exact file
        os.path.join(HERE, p, "index.html"),      # directory index
        os.path.join(HERE, p + ".html"),          # extensionless
    ]
    return any(os.path.exists(c) for c in candidates)


def check_links():
    broken, checked = [], 0
    for path in pages():
        src = url_of(path)
        text = open(path, encoding="utf-8").read()
        for raw in REF.findall(text):
            ref = html.unescape(raw).strip()
            if not ref or ref.startswith((
                    "http://", "https://", "mailto:", "tel:", "#", "data:", "javascript:")):
                continue
            if not ref.startswith("/"):
                continue          # nothing on this site uses relative paths
            checked += 1
            if not resolves(ref):
                broken.append((src, ref))

    print(f"links      {checked} internal references checked")
    if broken:
        print(f"{RED}  {len(broken)} BROKEN:{OFF}")
        for src, ref in sorted(set(broken)):
            print(f"{RED}    {ref}{OFF}  {DIM}(from {src}){OFF}")
        return False
    print(f"{GRN}  all resolve{OFF}")
    return True


# --------------------------------------------------------- compliance check

# Words that are only a problem when asserted, not when denied. "We guarantee a
# rate" is a violation; "this is not a guarantee of a rate" is the disclaimer we
# are required to carry. Matching on the bare word flags every disclosure on the
# site and trains everyone to ignore the checker, so negation is handled first.
NEGATORS = re.compile(
    r"\b(?:not|no|never|nor|without|cannot|can't|don't|does not|do not|isn't|is not|"
    r"aren't|are not|won't|will not|neither)\b", re.I)


def negated(flat, start):
    """Is there a negation in the clause immediately before this match?"""
    window = flat[max(0, start - 90):start]
    # Only look back to the start of the current clause — a full stop or
    # semicolon ends the scope of an earlier "not".
    clause = re.split(r"[.;]\s", window)[-1]
    return bool(NEGATORS.search(clause))


# Phrases that must never appear in consumer-facing copy.
# (pattern, description, negation_matters)
BANNED = [
    (r"\bguarantee[sd]?\b", "guarantee language"),
    (r"\bI guarantee\b", "'I guarantee' — the phrase flagged on the old site"),
    (r"\blowest rate", "'lowest rate' — unsubstantiated superlative"),
    (r"\bbest rate", "'best rate' — unsubstantiated superlative"),
    (r"\blowest price", "unsubstantiated superlative"),
    (r"\bpre-?approved\s+(?:today|now|instantly)", "implies approval"),
    (r"\bapproval guaranteed", "implies approval"),
    (r"\brisk[- ]free\b", "unsubstantiated claim"),
    (r"\bno credit check\b", "misleading for a mortgage"),
    (r"business professionals only", "the Reg Z §226.2 line that must not carry forward"),
]

# A stated rate or APR figure. Matches "6.75% APR", "APR of 6.75%", "rate: 6.75%".
RATE_FIGURE = re.compile(
    r"(\d+(?:\.\d+)?\s*%\s*APR)"
    r"|(APR\s*(?:of|:)?\s*\d+(?:\.\d+)?\s*%)"
    r"|(?:interest\s+)?rate\s*(?:of|:|is|at)\s*\d+(?:\.\d+)?\s*%",
    re.I)

# US English. This is a Longview, Texas mortgage broker — British spellings read
# as an outsider wrote the page, and "neighbourhood" shipped to production once
# already. Failing the build is cheaper than KT finding it again.
BRITISH = [
    (r"\bneighbourhood(s)?\b", "neighborhood"),
    (r"\benquir(y|ies|e|ed|ing)\b", "inquir-"),
    (r"\blicence(s|d)?\b", "license"),
    (r"\bcolour(s|ed|ing)?\b", "color"),
    (r"\bmaths\b", "math"),
    (r"\bcentre(s)?\b", "center"),
    (r"\bgrey\b", "gray"),
    (r"\bwhilst\b", "while"),
    (r"\bfavour(s|ed|ite)?\b", "favor"),
    (r"\borganis(e|ed|ation|ing)\b", "organiz-"),
    (r"\brealis(e|ed|ing)\b", "realiz-"),
    (r"\brecognis(e|ed|ing)\b", "recogniz-"),
    (r"\bbehaviour(s)?\b", "behavior"),
    (r"\bprogramme(s)?\b", "program"),
    (r"\bapologis(e|ed)\b", "apologiz-"),
    (r"\banalys(e|ed)\b", "analyz-"),
    (r"\bdefence\b", "defense"),
    (r"\btravelling\b", "traveling"),
    (r"\bcancelled\b", "canceled"),
]

# Disclosures required on every consumer page.
REQUIRED = [
    ("Powered by Co/LAB Lending", "Co/LAB attribution"),
    ("Equal Housing Opportunity", "EHO"),
    ("not a commitment to lend", "not-a-commitment-to-lend"),
    ("2426021", "company NMLS"),
    ("233918", "individual NMLS"),
]

TAGS = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.S | re.I)
STRIP = re.compile(r"<[^>]+>")


def visible_text(raw):
    """Rendered copy only — script/style bodies and attributes are not read by
    a consumer and would produce false positives (e.g. 'rate' in a JS var)."""
    return html.unescape(STRIP.sub(" ", TAGS.sub(" ", raw)))


def check_compliance():
    problems, warnings = [], []

    for path in pages():
        url = url_of(path)
        raw = open(path, encoding="utf-8").read()
        text = visible_text(raw)
        flat = re.sub(r"\s+", " ", text)

        for pattern, why in BANNED:
            for m in re.finditer(pattern, flat, re.I):
                if negated(flat, m.start()):
                    continue     # a disclaimer, not a claim
                ctx = flat[max(0, m.start() - 60):m.end() + 60].strip()
                problems.append((url, why, ctx))

        for m in RATE_FIGURE.finditer(flat):
            if negated(flat, m.start()):
                continue
            ctx = flat[max(0, m.start() - 70):m.end() + 70].strip()
            problems.append((url, "stated rate/APR figure", ctx))

        for pattern, us in BRITISH:
            for m in re.finditer(pattern, flat, re.I):
                ctx = flat[max(0, m.start() - 50):m.end() + 50].strip()
                problems.append((url, f"British spelling '{m.group(0)}' — use '{us}'", ctx))

        # A rate pre-filled into an input is invisible to the text scan above but
        # perfectly visible to a visitor, who has no reason to read it as anything
        # other than our rate. Rate fields must ship empty.
        for m in re.finditer(r"<input[^>]*\bid=\"[^\"]*rate[^\"]*\"[^>]*>", raw, re.I):
            tag = m.group(0)
            val = re.search(r'\bvalue="([^"]*)"', tag)
            if val and re.search(r"\d", val.group(1)):
                problems.append((url, "rate input ships with a pre-filled value",
                                 tag[:120]))

        # The internal screener is a staff tool, not a consumer page.
        if "va-refi-screener" in url:
            continue
        for needle, label in REQUIRED:
            if needle not in raw:
                warnings.append((url, f"missing {label}"))

    print(f"compliance {len(list(pages()))} pages scanned")

    if problems:
        print(f"{RED}  {len(problems)} PROHIBITED PHRASE(S):{OFF}")
        for url, why, ctx in problems:
            print(f"{RED}    {url}{OFF}  {why}")
            print(f"{DIM}      …{ctx}…{OFF}")
    else:
        print(f"{GRN}  no prohibited phrasing{OFF}")

    if warnings:
        print(f"{YEL}  {len(warnings)} missing disclosure(s):{OFF}")
        for url, w in warnings:
            print(f"{YEL}    {url}  {w}{OFF}")
    else:
        print(f"{GRN}  required disclosures present on every page{OFF}")

    return not problems and not warnings


# ------------------------------------------------------------------- todos

def report_todos():
    """Unconfirmed facts are deliberately visible in the markup. Count them so
    nobody ships thinking the site is finished."""
    hits = []
    for path in pages():
        raw = open(path, encoding="utf-8").read()
        for m in re.finditer(r'<[^>]*class="todo"[^>]*>(.*?)</', raw, re.S):
            hits.append((url_of(path), re.sub(r"\s+", " ", STRIP.sub("", m.group(1))).strip()))
    if hits:
        print(f"\n{YEL}open items — unconfirmed facts marked on the live pages ({len(hits)}){OFF}")
        for url, what in sorted(set(hits)):
            print(f"{DIM}    {url}  ·  {what[:90]}{OFF}")


if __name__ == "__main__":
    print()
    ok_links = check_links()
    print()
    ok_comp = check_compliance()
    report_todos()
    print()
    if ok_links and ok_comp:
        print(f"{GRN}PASS{OFF}\n")
        sys.exit(0)
    print(f"{RED}FAIL{OFF}\n")
    sys.exit(1)
