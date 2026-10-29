#!/usr/bin/env python3
"""Links from the tool pages and the home pages to the guides (public/guides/, public/ko/guides/).

Google only found most guides through the sitemap and the footer link, and left them
unindexed. Every tool page now lists the guides that explain its subject, and each home
page lists the newest guides, so the guides sit one click from the pages people visit.

Guides exist in one language only, so unlike the cross-link blocks this one is written
per language: English pages link English guides and Korean pages link Korean guides.
gen_ko.py calls prepare() before it builds the Korean pages (an empty marker pair goes
into each English page and is copied across) and fill() afterwards. Running either twice
changes nothing.

    python3 tools/gen_guides.py && python3 tools/gen_ko.py && python3 tools/gen_llms.py && python3 tools/bump_versions.py
"""
import html, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_guides   # load() reads content/guides; its build() only runs as a script
import gen_related  # PAGES: every page that carries the cross-link blocks

ROOT = os.path.join(HERE, "..", "public")
START, END = "<!-- guide-links:start -->", "<!-- guide-links:end -->"
TOOL_ANCHOR = "<!-- more-tools:start -->"
HOME_ANCHOR = "<!-- pricing -->"

# page -> guide slugs, in the order shown. Pages not listed here get no block.
E_PDF = ["compress-pdf-without-losing-quality", "reduce-pdf-size-iphone-mac", "kb-pixels-cm-dpi-explained"]
E_SIG = ["signature-image-for-online-forms", "india-exam-photo-signature-size", "ugc-net-photo-signature-size"]
E_PHOTO = ["kb-pixels-cm-dpi-explained", "india-exam-photo-signature-size", "us-visa-photo-requirements"]
K_PDF = ["pdf-compression-explained", "iphone-mac-pdf-size", "mail-attachment-size-limit"]
K_DOC = ["multiple-photos-to-pdf", "pdf-compression-explained", "mail-attachment-size-limit"]
K_VISA = ["us-visa-photo-size", "china-visa-photo", "india-visa-photo", "passport-photo-online"]

GUIDES = {
    "en": {
        "default_pdf": E_PDF,
        "sign-pdf.html": E_SIG, "signature-image.html": ["ssc-signature-photo-size", *E_SIG],
        "bank-exam-photo-signature.html": ["india-exam-photo-signature-size", "ssc-signature-photo-size", "ugc-net-photo-signature-size", "signature-image-for-online-forms"],
        "us-visa-photo.html": ["us-visa-photo-requirements", "india-e-visa-photo-requirements", "kb-pixels-cm-dpi-explained"],
        "compress-id-photo.html": [*E_PHOTO, "india-e-visa-photo-requirements"],
        **{p: E_PHOTO for p in gen_related.SIZE_IMG},
        "heic-to-jpg.html": ["kb-pixels-cm-dpi-explained", "us-visa-photo-requirements", "india-e-visa-photo-requirements"],
    },
    "ko": {
        "default_pdf": K_DOC,
        **{p: K_PDF for p in gen_related.SIZE_PDF}, "compress-pdf-for-email.html": ["mail-attachment-size-limit", "pdf-compression-explained", "iphone-mac-pdf-size"],
        "sign-pdf.html": ["pdf-sign-free", "pdf-stamp-seal", "pdf-compression-explained"],
        "merge.html": ["gov24-pdf-save", "multiple-photos-to-pdf", "pdf-compression-explained"],
        "jpg-to-pdf.html": ["phone-scan-to-pdf", "multiple-photos-to-pdf", "pdf-compression-explained"],
        "receipt-to-pdf.html": ["phone-scan-to-pdf", "multiple-photos-to-pdf", "mail-attachment-size-limit"],
        "signature-image.html": ["pdf-stamp-seal", "exam-application-photo-size", "resume-photo-size"],
        "us-visa-photo.html": K_VISA,
        "compress-id-photo.html": ["exam-application-photo-size", "passport-photo-online", "mobile-id-photo", "resume-photo-size",
                                   "university-application-photo", "driver-license-photo", "kuksiwon-photo", "youth-id-photo"],
        "compress-image.html": ["exam-application-photo-size", "computer-certificate-photo-size", "language-test-photo"],
        "compress-image-to-20kb.html": ["exam-application-photo-size", "resume-photo-size", "computer-certificate-photo-size"],
        "compress-image-to-50kb.html": ["exam-application-photo-size", "university-application-photo", "kuksiwon-photo"],
        "compress-image-to-100kb.html": ["china-visa-photo", "language-test-photo", "resume-photo-size"],
        "compress-image-to-200kb.html": ["passport-photo-online", "driver-license-photo", "exam-application-photo-size"],
        "heic-to-jpg.html": ["language-test-photo", "resume-photo-size", "passport-photo-online"],
    },
}
TEXT = {
    "en": dict(h="Related guides", home_h="Guides", home_sub="Size rules for application forms, with the official numbers and how to meet them.", all="All guides →"),
    "ko": dict(h="관련 가이드", home_h="가이드", home_sub="원서·서류 제출에서 막히는 사진, 서명, PDF 규격을 공식 기준과 함께 정리했어요.", all="가이드 전체 보기 →"),
}
HOME_COUNT = 6


def tool_pages():
    """Pages that hold the more-tools block, minus the home page."""
    return [p for p in gen_related.PAGES if p != "index.html"]


def slugs_for(lang, page):
    g = GUIDES[lang]
    if page in g:
        return g[page]
    # every other PDF tool: the general PDF guides. Photo pages without an entry get none.
    tool = gen_related.PAGES[page][0]
    return g["default_pdf"] if tool in gen_related.PDF_TOOLS else None


def path_of(lang, page):
    return os.path.join(ROOT, page) if lang == "en" else os.path.join(ROOT, "ko", page)


def cards(lang, arts, page):
    a_ = "tool-guide"
    out = ""
    for a in arts:
        out += (f'      <a class="guide-card" href="{gen_guides.art_path(lang, a["slug"])}" data-umami-event="{a_}" '
                f'data-umami-event-guide="{a["slug"]}" data-umami-event-page="{page}"><b>{a["title"]}</b><small>{a["desc"]}</small></a>\n')
    return out


def tool_block(lang, arts, page):
    t = TEXT[lang]
    return (f'{START}\n<section class="more guide-links">\n      <h2 class="more-h">{t["h"]}</h2>\n'
            f'      <div class="guide-list">\n{cards(lang, arts, page)}      </div>\n</section>\n{END}')


def home_block(lang, arts):
    t = TEXT[lang]
    hub = gen_guides.hub_path(lang)
    return (f'{START}\n     <section class="steps" id="guides">\n          <div class="wrap">\n'
            f'              <h2 class="sec">{t["home_h"]}</h2>\n              <p class="sec-sub">{t["home_sub"]}</p>\n'
            f'              <div class="guide-list">\n{cards(lang, arts, "index.html")}              </div>\n'
            f'              <p class="sec-sub"><a href="{hub}">{t["all"]}</a></p>\n          </div>\n     </section>\n{END}')


def put(s, block):
    """Replace what sits between the markers; the pair is always there after prepare()."""
    return re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: block, s, count=1, flags=re.S)


def prepare():
    """Leave an empty marker pair in each English page, so the Korean build copies no English cards."""
    for page in gen_related.PAGES:
        f = path_of("en", page)
        s = open(f).read()
        if START not in s:
            anchor = HOME_ANCHOR if page == "index.html" else TOOL_ANCHOR
            assert s.count(anchor) == 1, f"{page}: expected one {anchor}"
            indent = re.search(r"([ \t]*)" + re.escape(anchor), s).group(1)
            s = s.replace(indent + anchor, f"{indent}{START}\n{indent}{END}\n\n{indent}{anchor}", 1)
        s = put(s, f"{START}\n{END}")
        open(f, "w").write(s)


def fill():
    arts = gen_guides.load()
    shown = {"en": set(), "ko": set()}
    for lang in ("en", "ko"):
        mine = {a["slug"]: a for a in arts if a["lang"] == lang}
        newest = sorted(mine.values(), key=lambda a: (a["updated"], a["published"]), reverse=True)[:HOME_COUNT]
        for page in gen_related.PAGES:
            f = path_of(lang, page)
            if not os.path.exists(f):
                continue   # not every English tool has a Korean page
            if page == "index.html":
                block, used = home_block(lang, newest), newest
            else:
                slugs = slugs_for(lang, page)
                if not slugs:
                    block, used = f"{START}\n{END}", []
                else:
                    used = [mine[s] for s in slugs]   # KeyError = a slug that no longer exists
                    block = tool_block(lang, used, page)
            s = open(f).read()
            new = put(s, block)
            assert new != s or block in s, f"{f}: guide-links markers missing"
            if new != s:
                open(f, "w").write(new)
            shown[lang].update(a["slug"] for a in used)
    for lang in ("en", "ko"):
        every = {a["slug"] for a in arts if a["lang"] == lang}
        left = every - shown[lang]
        if left:
            print(f"warning: {lang} guides not linked from any tool or home page: {sorted(left)}")
    return shown


def run():
    prepare()
    return fill()


if __name__ == "__main__":
    s = run()
    print(f"guide links: en {len(s['en'])} guides, ko {len(s['ko'])} guides linked from tool/home pages")
