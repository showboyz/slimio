#!/usr/bin/env python3
"""Point every /asset.js|css?v=... reference in public/**/*.html at the asset's current content hash.

Cloudflare caches .js/.css for hours, so the ?v= must change whenever the file does.
Run after editing any JS/CSS:  python3 tools/bump_versions.py
"""
import glob, hashlib, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public")
REF = re.compile(r'((?:src|href)=")(/[^"?#]+\.(?:js|css))\?v=[a-z0-9]+(")')

def digest(path, cache={}):
    if path not in cache:
        with open(os.path.join(ROOT, path.lstrip("/")), "rb") as f:
            cache[path] = hashlib.sha1(f.read()).hexdigest()[:8]
    return cache[path]

changed = 0
for page in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
    s = open(page).read()
    new = REF.sub(lambda m: f"{m.group(1)}{m.group(2)}?v={digest(m.group(2))}{m.group(3)}", s)
    if new != s:
        open(page, "w").write(new)
        changed += 1
print(f"updated {changed} page(s)")
