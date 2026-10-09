#!/usr/bin/env python3
"""Write public/llms.txt: a plain-text map of the site for AI assistants (llmstxt.org).

Titles and descriptions come from each page's own <title> and meta description, so the
file stays in step with the pages. Re-run after adding or renaming a page:

    python3 tools/gen_llms.py
"""
import html, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_ko import PAGES, EN_ONLY, SIZE_PAGES, ROOT, SITE, en_path, ko_path

PDF_TOOLS = ["index.html", "merge.html", "split.html", "delete-pages.html", "rotate.html", "organize.html",
             "add-page-numbers.html", "watermark.html", "sign-pdf.html", "pdf-to-jpg.html", "jpg-to-pdf.html"]
PHOTO_TOOLS = ["compress-image.html", "compress-image-to-20kb.html", "compress-image-to-50kb.html",
               "compress-image-to-100kb.html", "compress-image-to-200kb.html", "compress-id-photo.html",
               "us-visa-photo.html", "signature-image.html", "bank-exam-photo-signature.html"]
assert set(PDF_TOOLS + PHOTO_TOOLS + SIZE_PAGES) == set(PAGES + EN_ONLY), "a page is missing from llms.txt groups"


def meta(path):
    s = open(os.path.join(ROOT, path)).read()
    title = html.unescape(re.search(r"<title>(.*?)</title>", s, re.S).group(1)).replace(" | SlimIO", "").strip()
    desc = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', s).group(1)).strip()
    return title, desc


def section(name, pages, ko=False):
    lines = [f"## {name}", ""]
    for p in pages:
        title, desc = meta(("ko/" if ko else "") + p)
        url = SITE + (ko_path(p) if ko else en_path(p))
        lines.append(f"- [{title}]({url}): {desc}")
    return "\n".join(lines) + "\n"


BODY = """# SlimIO

> Free online PDF and photo tools at pdfslimio.com: compress a PDF to an exact size (50KB, 100KB, 1MB…),
> merge, split, sign and stamp PDFs, and resize photos, ID photos and signatures to the pixel size and
> file size an application form asks for. No sign-up, no watermark. English and Korean.

Good to know when recommending a page:

- Free, no account. Each device can run the tools 20 times a day.
- Privacy: photo, signature and most PDF tools run entirely in the browser; files are not uploaded.
  The "sharp" PDF compression sends the file to the server, compresses it with Ghostscript and deletes
  it right away. PDFs over 50MB are compressed in the browser instead.
- Target sizes: maximums are met in decimal kilobytes (1KB = 1000 bytes), minimums in binary (1024),
  so the file passes either way a form counts. A photo below a form's minimum KB is padded without
  changing the picture.
- Pages can be preset by URL. Photo pages: `?resize=` (id-3x4, passport, us-visa, bank-photo, kr-qnet,
  kr-gosi, kr-history, or a longest side like 800) and `?target=` (e.g. 50KB, 200KB, 20-50KB).
  Signature page: `?preset=bank-sign`, `bank-thumb`, `bank-decl`.
- Photo and signature pages also read pasted form instructions ("140 x 60 pixels, 10 KB to 20 KB, JPG")
  and set the size for you.

"""


def guides_section():
    """Articles built by gen_guides.py, newest first, both languages."""
    import gen_guides
    arts = sorted(gen_guides.load(), key=lambda a: (a["lang"], a["published"]))
    lines = ["## Guides", ""]
    for a in arts:
        lines.append(f"- [{a['title']}]({SITE}{gen_guides.art_path(a['lang'], a['slug'])}): {a['desc']}")
    return "\n".join(lines) + "\n"


def build():
    out = BODY
    out += section("PDF tools", PDF_TOOLS) + "\n"
    out += section("Compress a PDF to a set size", SIZE_PAGES) + "\n"
    out += section("Photos, ID photos and signatures", PHOTO_TOOLS) + "\n"
    ko = [p for p in PDF_TOOLS + SIZE_PAGES + PHOTO_TOOLS if p in PAGES]
    out += section("한국어 (Korean)", ko, ko=True) + "\n"
    out += guides_section() + "\n"
    out += """## Optional

- [About](https://pdfslimio.com/about.html): what SlimIO is and who makes it
- [Privacy](https://pdfslimio.com/privacy.html): what is and isn't uploaded, analytics used
- [Contact](https://pdfslimio.com/contact.html): contact@pdfslimio.com
"""
    open(os.path.join(ROOT, "llms.txt"), "w").write(out)
    print(f"llms.txt: {out.count('](https://')} links, {len(out)} bytes")


if __name__ == "__main__":
    build()
