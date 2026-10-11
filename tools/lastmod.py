#!/usr/bin/env python3
"""Real <lastmod> dates for sitemap.xml.

Every build rewrites every page (asset version hashes, the shared tool links, the footer), so "today"
would be the date of every URL, and Google ignores lastmod that is never accurate. Here a page's date
moves only when its own content changes: title, description and body text, without the nav, the
shared "More free tools" block, the "More guides" list under articles, the footer and scripts.

Dates are kept in tools/lastmod.json (gen_ko.py updates it when it writes the sitemap).
`python3 tools/lastmod.py` rebuilds that file from git history.
"""
import datetime, hashlib, html, json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..")
ROOT = os.path.join(REPO, "public")
STORE = os.path.join(HERE, "lastmod.json")
SHARED = re.compile(r'(?s)<head>.*?</head>|<nav>.*?</nav>|<!-- more-tools:start -->.*?<!-- more-tools:end -->'
                    r'|<section class="content">\s*<h2>[^<]*</h2>\s*<div class="guide-list">.*?</section>'
                    r'|<footer>.*?</footer>|<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->')


def fingerprint(page):
    title = re.search(r"(?s)<title>(.*?)</title>", page)
    desc = re.search(r'<meta name="description" content="([^"]*)"', page)
    text = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", SHARED.sub(" ", page))).split())
    return hashlib.sha1("\n".join([title.group(1) if title else "", desc.group(1) if desc else "", text]).encode()).hexdigest()[:16]


def file_of(url):
    p = url.lstrip("/")
    return os.path.join(ROOT, p + "index.html" if p == "" or p.endswith("/") else p)


def save(store):
    with open(STORE, "w") as f:
        json.dump(dict(sorted(store.items())), f, indent=1, ensure_ascii=False)
        f.write("\n")


def dates(urls, today):
    """{url: lastmod}; a page whose content changed since the last build gets today's date."""
    old = json.load(open(STORE)) if os.path.exists(STORE) else {}
    store = {}
    for u in urls:
        h = fingerprint(open(file_of(u)).read())
        store[u] = old[u] if old.get(u, [None])[0] == h else [h, today]
    save(store)
    return {u: d for u, (h, d) in store.items()}


def from_git(urls, today):
    """Date each page by the oldest commit in the run of commits that already had its current content."""
    store = {}
    for u in urls:
        rel = os.path.relpath(file_of(u), REPO)
        h = fingerprint(open(file_of(u)).read())
        log = subprocess.run(["git", "log", "--format=%H %ad", "--date=short", "--", rel], cwd=REPO, capture_output=True, text=True).stdout.split()
        date = None
        for sha, d in zip(log[::2], log[1::2]):   # newest first
            if fingerprint(subprocess.run(["git", "show", f"{sha}:{rel}"], cwd=REPO, capture_output=True, text=True).stdout) != h:
                break
            date = d
        store[u] = [h, date or today]   # uncommitted content counts as changed today
    save(store)
    return store


if __name__ == "__main__":
    urls = re.findall(r"<loc>https://pdfslimio\.com(/[^<]*)</loc>", open(os.path.join(ROOT, "sitemap.xml")).read())
    store = from_git(urls, datetime.date.today().isoformat())
    for u, (h, d) in store.items():
        print(d, u)
