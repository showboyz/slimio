#!/usr/bin/env python3
"""What the seven "Compress PDF to N" pages really do to one test file (tools/measured.json).

Every size page used to share about two thirds of its text with its siblings, and none of
it came from running the tool. This adds a short section with numbers we measured: one made-up
3-page phone-scan PDF (3.61 MB) run through each page's real flow (server + browser) with
tools/measure_pdf_sizes.mjs. Each page gets its own result line and a paragraph about its own
target; the full table and the picture live in one guide (content/guides/*/pdf-size-test.html),
so the pages do not repeat each other.

gen_ko.py calls prepare() before it builds the Korean pages (an empty marker pair goes into
each English page and is copied across) and fill() afterwards, the same way as gen_guide_links.
Running either twice changes nothing.

    python3 tools/gen_guides.py && python3 tools/gen_ko.py && python3 tools/gen_llms.py && python3 tools/bump_versions.py
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "public")
START, END = "<!-- measured:start -->", "<!-- measured:end -->"
ANCHOR = '<div class="related">'   # after the FAQ: gen_ko reads the text between the content block and the FAQ as one piece
SLUG = "compress-pdf-to-{}.html"
ORDER = ["50kb", "100kb", "200kb", "300kb", "500kb", "1mb", "2mb"]
LABEL = {"50kb": "50KB", "100kb": "100KB", "200kb": "200KB", "300kb": "300KB", "500kb": "500KB", "1mb": "1MB", "2mb": "2MB"}

# how the text looked in the result (judged by eye on the crops, see the picture)
LOOK = {
    "en": {"50kb": "Body text blurry, heading fine", "100kb": "Readable, a little soft", "200kb": "Clear", "300kb": "Clear",
           "500kb": "Sharp", "1mb": "Readable, slightly rough", "2mb": "Sharp"},
    "ko": {"50kb": "본문 글씨가 뭉개짐, 제목은 보임", "100kb": "읽을 수 있지만 조금 흐림", "200kb": "선명", "300kb": "선명",
           "500kb": "아주 선명", "1mb": "읽을 수 있지만 가장자리가 거침", "2mb": "아주 선명"},
}
HOW = {
    "en": {"images": "Pages turned into images, about {dpi} dpi", "kept": "Pages kept, pictures recompressed"},
    "ko": {"images": "쪽을 이미지로 바꿈, 약 {dpi}dpi", "kept": "쪽은 그대로, 안의 그림만 다시 압축"},
}
# one paragraph per page, about its own target; {n} is the measured size
NOTE = {
    "en": {
        "50kb": "At 50KB the three pages came to {n}, about 15 KB a page. SlimIO had to turn them into images at about 40 dpi, so the text can no longer be selected, and the body text blurred while the large heading stayed readable. That is why this page suggests keeping only the page the form needs.",
        "100kb": "At 100KB the same three pages came to {n} (about 32 KB a page) at about 50 dpi. The body text is readable but a little soft, so for a form where you have to read small print or a number back, one or two pages are safer than three.",
        "200kb": "At 200KB we got {n} at about 72 dpi. The body text is clearly readable and all three pages fit, which makes 200KB a comfortable size for a short scanned document.",
        "300kb": "At 300KB the result was {n} at about 90 dpi, with clean text on all three pages. Mark sheets and certificates that run to two or three pages are what this size is for.",
        "500kb": "At 500KB the result was only {n}. SlimIO kept the three pages as they are and recompressed the pictures inside, so nothing was turned into a lower-resolution image, and it came out sharper than the 300KB result. When the pages fit without being rebuilt, SlimIO leaves them alone.",
        "1mb": "At 1MB this file took the other route: the pages were turned into images at about 108 dpi, giving {n}. The text stayed readable, though it is a little rougher than the 500KB result. Your own file may go either way, and the result box tells you which one happened.",
        "2mb": "At 2MB the pages were kept and only the pictures were recompressed: {n}, down from 3.61 MB, a saving of about half, with sharp text. A limit this large leaves room, so SlimIO does not lower the quality more than it has to.",
    },
    "ko": {
        "50kb": "50KB로 줄이니 3쪽이 {n}, 한 쪽에 15KB쯤이 됐어요. 이 크기에 맞추려고 쪽을 약 40dpi 이미지로 바꿔서 글자를 선택할 수 없게 됐고, 큰 제목은 읽히지만 본문 글씨는 뭉개졌어요. 그래서 이 페이지는 원서가 요구하는 쪽만 남기라고 안내해요.",
        "100kb": "100KB로 줄인 같은 3쪽은 약 50dpi에서 {n}로 줄었어요(한 쪽에 32KB쯤). 본문은 읽을 수 있지만 조금 흐려서, 작은 글씨나 숫자를 읽어야 하는 서류라면 3쪽보다 1~2쪽으로 줄이는 쪽이 안전해요.",
        "200kb": "200KB에서는 약 72dpi에서 {n}로 줄었어요. 본문이 선명하게 읽히고 3쪽이 모두 들어가서, 짧은 스캔 서류에는 여유 있는 크기예요.",
        "300kb": "300KB에서는 약 90dpi에서 {n}로 줄었고, 3쪽 모두 글씨가 깨끗해요. 2~3쪽짜리 성적표나 증명서에 맞는 크기예요.",
        "500kb": "500KB에서는 결과가 {n}밖에 안 됐어요. 쪽은 그대로 두고 안의 그림만 다시 압축해서 해상도가 낮은 이미지로 바꾸지 않았고, 300KB 결과보다 오히려 선명해요. 쪽을 새로 만들지 않고도 들어가면 그렇게 해요.",
        "1mb": "1MB에서는 이 파일이 다른 방법을 탔어요. 쪽을 약 108dpi 이미지로 바꿔서 {n}가 됐고, 글씨는 읽히지만 500KB 결과보다 가장자리가 조금 거칠어요. 내 파일은 어느 쪽이 될지 달라서, 어떤 방법이 쓰였는지는 결과 상자에 표시돼요.",
        "2mb": "2MB에서는 쪽을 그대로 두고 그림만 다시 압축해서 3.61MB가 {n}로 반쯤 줄었고 글씨는 아주 선명해요. 이만큼 여유가 있으면 필요 이상으로 화질을 낮추지 않아요.",
    },
}
TEXT = {
    "en": dict(
        h="We tested it: what {t} did to a 3-page scan",
        line="On 30 October 2026 we ran one made-up 3-page scan (3.61 MB) through every size page. At {t} it came out at <b>{n}</b>: {how}. Text: {look}.",
        more='See all seven sizes side by side, with a picture of each: <a href="{url}">{title}</a>.',
        title="We compressed one scanned PDF to 50KB, 100KB, 200KB, 300KB, 500KB, 1MB and 2MB",
    ),
    "ko": dict(
        h="직접 돌려 봤어요: {t}로 줄이면 3쪽 스캔이 어떻게 되나",
        line="2026년 10월 30일에 가상의 3쪽 스캔(3.61MB) 하나를 모든 크기 페이지에 넣어 봤어요. {t}에서는 <b>{n}</b>로 줄었어요: {how}. 글씨 상태: {look}.",
        more='일곱 가지 용량을 그림과 함께 나란히 보려면: <a href="{url}">{title}</a>.',
        title="스캔 PDF 하나를 50KB·100KB·200KB·300KB·500KB·1MB·2MB로 줄여 봤어요",
    ),
}
GUIDE = {"en": "/guides/pdf-size-test.html", "ko": "/ko/guides/pdf-size-test.html"}


def data():
    return json.load(open(os.path.join(HERE, "measured.json")))


def size_text(b, lang):
    kb = b / 1024
    return f"{kb / 1024:.2f}MB" if kb >= 1000 else f"{kb:.1f}KB"


def block(lang, key):
    r, t = data()["pdf"][key], TEXT[lang]
    how = HOW[lang]["images"].format(dpi=r["dpi"]) if r["mode"] == "images" else HOW[lang]["kept"]
    n = size_text(r["bytes"], lang)
    how = how[0].lower() + how[1:] if lang == "en" else how
    return (f'{START}\n<div class="content measured">\n      <h2>{t["h"].format(t=LABEL[key])}</h2>\n'
            f'      <p>{t["line"].format(t=LABEL[key], n=n, how=how, look=LOOK[lang][key].lower() if lang == "en" else LOOK[lang][key])}</p>\n'
            f'      <p>{NOTE[lang][key].format(n=n)}</p>\n'
            f'      <p>{t["more"].format(url=GUIDE[lang], title=t["title"])}</p>\n</div>\n{END}')


def path_of(lang, key):
    f = SLUG.format(key)
    return os.path.join(ROOT, f) if lang == "en" else os.path.join(ROOT, "ko", f)


def put(s, b):
    return re.sub(re.escape(START) + r".*?" + re.escape(END), lambda m: b, s, count=1, flags=re.S)


def prepare():
    """Leave an empty marker pair after the FAQ of each English size page, so the Korean build copies no English text."""
    for key in ORDER:
        f = path_of("en", key)
        s = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\n*", "", open(f).read(), flags=re.S)   # a pair placed elsewhere earlier
        assert s.count(ANCHOR) == 1, f"{f}: expected one {ANCHOR}"
        open(f, "w").write(s.replace(ANCHOR, f"{START}\n{END}\n\n{ANCHOR}", 1))


def fill():
    for lang in ("en", "ko"):
        for key in ORDER:
            f = path_of(lang, key)
            s = open(f).read()
            new = put(s, block(lang, key))
            assert START in new, f"{f}: measured markers missing"
            if new != s:
                open(f, "w").write(new)


def run():
    prepare()
    fill()


if __name__ == "__main__":
    run()
    print(f"measured: {len(ORDER)} size pages x 2 languages")
