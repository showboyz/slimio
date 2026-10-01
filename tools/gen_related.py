#!/usr/bin/env python3
"""Cross-links between tools, written into every English tool page:

- "Next steps": three tool cards that appear (lib.js) once the visitor downloads a result.
- "More tools" at the bottom: one feature banner for a tool from the other category,
  then every tool as a card, grouped into PDF tools and photo & signature tools.

Tool names, icons and blurbs live in TOOLS (English and Korean); gen_ko.py imports
ko_pairs() to translate the blocks, and runs this script first, so the usual

    python3 tools/gen_ko.py && python3 tools/bump_versions.py

keeps everything in sync. Running it twice changes nothing (blocks sit between markers).
"""
import html, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public")

# key: (href, icon, (English name, blurb), (Korean name, blurb))
TOOLS = {
    "compress": ("/", "🗜️", ("Compress PDF", "Smaller files, text kept sharp"), ("PDF 압축", "글자는 선명하게, 용량은 작게")),
    "merge": ("/merge.html", "➕", ("Merge PDF", "Combine multiple PDFs into one"), ("PDF 합치기", "여러 PDF를 하나로")),
    "split": ("/split.html", "✂️", ("Split PDF", "Extract pages or split by range"), ("PDF 나누기", "페이지별로 나누거나 범위 추출")),
    "delete-pages": ("/delete-pages.html", "🗑️", ("Remove Pages", "Delete pages from a PDF"), ("페이지 삭제", "필요 없는 페이지 빼기")),
    "rotate": ("/rotate.html", "🔄", ("Rotate PDF", "Turn pages 90/180/270°"), ("PDF 회전", "90° · 180° · 270° 돌리기")),
    "organize": ("/organize.html", "🗂️", ("Organize PDF", "Reorder, rotate or delete pages"), ("페이지 순서 변경", "순서 바꾸기 · 회전 · 삭제")),
    "add-page-numbers": ("/add-page-numbers.html", "🔢", ("Page Numbers", "Number every page of a PDF"), ("페이지 번호", "모든 페이지에 쪽번호")),
    "watermark": ("/watermark.html", "💧", ("Watermark PDF", "Stamp text on every page"), ("워터마크", "대외비 · 사본 문구 넣기")),
    "sign-pdf": ("/sign-pdf.html", "✍️", ("Sign PDF", "Put your signature on any page"), ("PDF 서명", "원하는 위치에 서명 · 도장")),
    "pdf-to-jpg": ("/pdf-to-jpg.html", "🖼️", ("PDF to JPG", "Convert pages to images"), ("PDF → JPG", "페이지를 이미지로 변환")),
    "jpg-to-pdf": ("/jpg-to-pdf.html", "📷", ("JPG to PDF", "Turn photos into one PDF"), ("JPG → PDF", "사진을 PDF 하나로 묶기")),
    "compress-id-photo": ("/compress-id-photo.html", "🪪", ("ID Photo", "Passport & ID sizes, under the KB limit"), ("증명사진", "여권·반명함 규격 + 용량 맞추기")),
    "signature-image": ("/signature-image.html", "🖋️", ("Signature Image", "Clean JPG or transparent PNG"), ("서명 이미지", "깨끗한 JPG · 투명 PNG")),
    "compress-image": ("/compress-image.html", "📸", ("Compress Image", "Shrink photos to any KB"), ("사진 용량 줄이기", "사진을 원하는 KB로")),
}
PDF_TOOLS = ["compress", "merge", "split", "delete-pages", "rotate", "organize", "add-page-numbers",
             "watermark", "sign-pdf", "pdf-to-jpg", "jpg-to-pdf"]
PHOTO_TOOLS = ["compress-id-photo", "signature-image", "compress-image"]

# Feature banners: a tool from the *other* category, with a real example image.
FEATURES = {
    "id": dict(href="/compress-id-photo.html",
               imgs=[("/img/id-sample-3x4.webp", 354, 472), ("/img/id-sample-passport.webp", 413, 531)],
               en=("New", "ID &amp; passport photos, sized right", "Drag the frame onto your face, pick 3×4 or 3.5×4.5 cm and stay under the KB limit.", "Make an ID photo →"),
               ko=("새 기능", "증명사진, 규격도 용량도 한 번에", "틀을 얼굴에 맞추고 3×4·3.5×4.5cm를 고르면 원서 용량 제한까지 맞춰요.", "증명사진 만들기 →")),
    "sig": dict(href="/signature-image.html",
                imgs=[("/img/sig-demo-out.webp", 600, 182)],
                en=("New", "Your signature as a clean image", "Draw it, or photograph it on paper — get a JPG or transparent PNG at the size forms ask for.", "Make a signature image →"),
                ko=("새 기능", "서명을 깨끗한 이미지 파일로", "직접 그리거나 종이 서명을 찍어 올리면 원서 규격의 JPG·투명 PNG로 만들어요.", "서명 이미지 만들기 →")),
}

SIZE_PDF = ["compress-pdf-to-50kb.html", "compress-pdf-to-100kb.html", "compress-pdf-to-200kb.html", "compress-pdf-to-300kb.html",
            "compress-pdf-to-500kb.html", "compress-pdf-to-1mb.html", "compress-pdf-to-2mb.html", "compress-pdf-for-email.html"]
SIZE_IMG = ["compress-image.html", "compress-image-to-20kb.html", "compress-image-to-50kb.html",
            "compress-image-to-100kb.html", "compress-image-to-200kb.html"]

# page: (this tool, feature banner, next steps). The home page only gets next steps.
PAGES = {
    "index.html": ("compress", None, ["merge", "sign-pdf", "delete-pages"]),
    **{p: ("compress", "id", ["merge", "delete-pages", "sign-pdf"]) for p in SIZE_PDF},
    "merge.html": ("merge", "id", ["compress", "sign-pdf", "organize"]),
    "split.html": ("split", "id", ["compress", "merge", "delete-pages"]),
    "delete-pages.html": ("delete-pages", "id", ["compress", "merge", "organize"]),
    "rotate.html": ("rotate", "id", ["compress", "merge", "organize"]),
    "organize.html": ("organize", "id", ["compress", "sign-pdf", "add-page-numbers"]),
    "add-page-numbers.html": ("add-page-numbers", "id", ["compress", "watermark", "sign-pdf"]),
    "watermark.html": ("watermark", "id", ["compress", "sign-pdf", "add-page-numbers"]),
    "pdf-to-jpg.html": ("pdf-to-jpg", "id", ["compress-image", "jpg-to-pdf", "compress"]),
    "jpg-to-pdf.html": ("jpg-to-pdf", "id", ["compress", "merge", "sign-pdf"]),
    "sign-pdf.html": ("sign-pdf", "sig", ["compress", "merge", "signature-image"]),
    **{p: ("compress-image", "sig", ["compress-id-photo", "jpg-to-pdf", "signature-image"]) for p in SIZE_IMG},
    "compress-id-photo.html": ("compress-id-photo", "sig", ["signature-image", "compress-image", "jpg-to-pdf"]),
    "signature-image.html": ("signature-image", "id", ["sign-pdf", "compress-id-photo", "compress"]),
}

EN_TEXT = {"next": "Next, you might want to…", "more": "More free tools", "pdf": "PDF tools", "photo": "Photo &amp; signature tools"}
KO_TEXT = {"next": "이어서 이런 것도 해 보세요", "more": "다른 무료 도구", "pdf": "PDF 도구", "photo": "사진 · 서명 도구"}


def card(key):
    href, icon, (name, blurb), _ = TOOLS[key]
    return (f'<a class="tcard" href="{href}"><span class="ico">{icon}</span>'
            f'<span class="tx"><b>{name}</b><small>{blurb}</small></span></a>')


def cards(keys, cls="tcards"):
    return f'<div class="{cls}">\n' + "\n".join("          " + card(k) for k in keys) + "\n      </div>"


def feature(key):
    f = FEATURES[key]
    tag, title, text, cta = f["en"]
    imgs = "".join(f'<img src="{src}" width="{w}" height="{h}" loading="lazy" alt="" />' for src, w, h in f["imgs"])
    return (f'<a class="feature" href="{f["href"]}">\n'
            f'          <span class="feature-art">{imgs}</span>\n'
            f'          <span class="feature-body"><span class="tag">{tag}</span><b class="ft">{title}</b>'
            f'<span class="fx">{text}</span><span class="cta">{cta}</span></span>\n      </a>')


def next_block(keys):
    return ('<!-- next-steps:start -->\n<div class="next-steps" id="next" hidden>\n'
            f'      <b class="nh">{EN_TEXT["next"]}</b>\n      {cards(keys, "tcards three")}\n</div>\n<!-- next-steps:end -->\n')


def more_block(this, feat):
    pdf = [k for k in PDF_TOOLS if k != this]
    photo = [k for k in PHOTO_TOOLS if k != this]
    return ('<!-- more-tools:start -->\n<section class="more">\n'
            f'      {feature(feat)}\n'
            f'      <h2 class="more-h">{EN_TEXT["more"]}</h2>\n'
            f'      <p class="more-sub">{EN_TEXT["pdf"]}</p>\n      {cards(pdf)}\n'
            f'      <p class="more-sub">{EN_TEXT["photo"]}</p>\n      {cards(photo)}\n'
            '</section>\n<!-- more-tools:end -->\n')


def put(s, start, end, block, fallback, what):
    """Replace the marked block, or the old markup (first run)."""
    marked = re.compile(rf"<!-- {start} -->.*?<!-- {end} -->\n", re.S)
    if marked.search(s):
        return marked.sub(lambda m: block, s, count=1)
    out, n = re.subn(fallback[0], lambda m: fallback[1](m, block), s, count=1, flags=re.S)
    if n != 1:
        sys.exit(f"[{what}] no place for {start}")
    return out


def build(page):
    path = os.path.join(ROOT, page)
    s = open(path).read()
    this, feat, nxt = PAGES[page]
    # next steps go right under the tool card, before the ad slot
    s = put(s, "next-steps:start", "next-steps:end", next_block(nxt),
            (r'(\n\s*)(<div class="ad" id="ad">)', lambda m, b: "\n" + b + m.group(1).lstrip("\n") + m.group(2)), page)
    if feat:
        s = put(s, "more-tools:start", "more-tools:end", more_block(this, feat),
                (r'<div class="related">\s*<h3>Related tools</h3>.*?</div>\s*</div>\n', lambda m, b: b), page)
    open(path, "w").write(s)


def ko_pairs():
    """(English, Korean) replacements for gen_ko.py."""
    pairs = []
    for key, (_, _, (n, b), (kn, kb)) in TOOLS.items():
        pairs.append((f"<b>{n}</b><small>{b}</small>", f"<b>{kn}</b><small>{kb}</small>"))
    wraps = ['<span class="tag">{}</span>', '<b class="ft">{}</b>', '<span class="fx">{}</span>', '<span class="cta">{}</span>']
    for f in FEATURES.values():
        for wrap, en, ko in zip(wraps, f["en"], f["ko"]):
            pairs.append((wrap.format(en), wrap.format(ko)))
    for k in EN_TEXT:
        tag = {"next": '<b class="nh">{}</b>', "more": '<h2 class="more-h">{}</h2>'}.get(k, '<p class="more-sub">{}</p>')
        pairs.append((tag.format(EN_TEXT[k]), tag.format(KO_TEXT[k])))
    return list(dict.fromkeys(pairs))


def run():
    for page in PAGES:
        build(page)


if __name__ == "__main__":
    run()
    print(f"related blocks: {len(PAGES)} pages")
