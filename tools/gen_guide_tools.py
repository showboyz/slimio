#!/usr/bin/env python3
"""The ID photo tool inside Korean photo guides (content/guides/ko/<slug>.html with "tool": [...]).

gen_guides.py leaves an empty marker pair under the guide's intro. fill() copies the tool box of
the freshly built /ko/compress-id-photo.html into it: the drop area, the size and KB controls, the
crop frame and the result list. The size tiles go, the exam chips are cut down to the guide's
sizes, and the first size is preselected (compress-image.js reads data-preset). The tool page's
scripts come along, so a change to the tool reaches the guides on the next build.

gen_ko.py calls fill() at the end, after it has built the Korean tool page. Running it twice
changes nothing.

    python3 tools/gen_guides.py && python3 tools/gen_ko.py && python3 tools/gen_llms.py && python3 tools/bump_versions.py
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_guides   # load() reads content/guides; its build() only runs as a script

ROOT = os.path.join(HERE, "..", "public")
TOOL_PAGE = "/ko/compress-id-photo.html"


def tool_block(src, sizes):
    """The tool box of the Korean ID photo page, set up for `sizes` (preset keys, first preselected)."""
    box = src[src.index('<div class="tool" data-live>'):src.index("<!-- next-steps:start -->")].rstrip()
    box = box.replace('<div class="tool" data-live>', f'<div class="tool" data-live data-preset="{sizes[0]}">', 1)
    # the three size tiles (3×4, passport, custom) would pull readers off their exam's size;
    # custom sizes stay in the Resize list
    box = re.sub(r'\n\s*<div class="presets"[^>]*>.*?</div>', "", box, count=1, flags=re.S)
    row = re.search(r'(<div class="exams"[^>]*>)<span>[^<]*</span>(.*?)</div>', box)
    chips = {k: c for c, k in re.findall(r'(<button type="button" class="preset" data-resize="([^"]+)".*?</button>)', row.group(2))}
    missing = [s for s in sizes if s not in chips]
    assert not missing, f"no exam chip on {TOOL_PAGE} for {missing}"
    box = box.replace(row.group(0), row.group(1) + "<span>사진 규격</span>" + "".join(chips[s] for s in sizes) + "</div>")
    scripts = re.findall(r'<script (?:defer|type="module") src="[^"]+"></script>', src[src.index("</footer>"):])
    more = f'<p class="guide-tool-more">다른 규격은 <a href="{TOOL_PAGE}">증명사진 도구</a>에서 골라요.</p>'
    return "\n".join([box, more, *scripts])


def fill():
    src = open(os.path.join(ROOT, TOOL_PAGE.lstrip("/"))).read()
    for a in gen_guides.load():
        if not a.get("tool"):
            continue
        assert a["lang"] == "ko", f'{a["slug"]}: the tool box is copied from the Korean page, so "tool" is for Korean guides only'
        p = os.path.join(ROOT, "ko", "guides", a["slug"] + ".html")
        s = open(p).read()
        i, j = s.index(gen_guides.TOOL_START) + len(gen_guides.TOOL_START), s.index(gen_guides.TOOL_END)
        open(p, "w").write(s[:i] + "\n" + tool_block(src, a["tool"]) + "\n" + s[j:])
        print("tool", a["slug"], " ".join(a["tool"]))


if __name__ == "__main__":
    fill()
