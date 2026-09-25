#!/usr/bin/env python3
"""Every SlimIO.t("...") key used in public/ JS must have a Korean entry in public/i18n/ko.js."""
import glob, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public")
used = set()
for f in glob.glob(os.path.join(ROOT, "js", "*.js")) + [os.path.join(ROOT, n) for n in ("lib.js", "target.js")]:
    s = open(f).read()
    for m in re.finditer(r'\bt\((["\'])(.*?)(?<!\\)\1', s):
        used.add(m.group(2).replace('\\"', '"').replace("\\'", "'"))
    for m in re.finditer(r'\bt\([^()]*?\? "(.*?)" : "(.*?)"', s):
        used.update(m.groups())
used = {k for k in used if " : " not in k}

ko = open(os.path.join(ROOT, "i18n", "ko.js")).read()
have = set()
for m in re.finditer(r'^\s*(["\'])(.*?)(?<!\\)\1\s*:', ko, re.M):
    have.add(m.group(2).replace('\\"', '"').replace("\\'", "'"))

missing, unused = sorted(used - have), sorted(have - used)
for k in missing: print("MISSING:", k)
for k in unused: print("unused:", k)
print(f"{len(used)} keys used, {len(missing)} missing")
sys.exit(1 if missing else 0)
