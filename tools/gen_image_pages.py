#!/usr/bin/env python3
"""Build target-size image pages (compress-image-to-100kb.html, ...) from compress-image.html.

The tool markup and script come from compress-image.html; this swaps in the page's
own title, meta, structured data, hero, body copy and FAQ, and preselects the
target size. It also keeps the "other sizes" link row on every image page.

    python3 tools/gen_image_pages.py && python3 tools/gen_ko.py && python3 tools/bump_versions.py
"""
import html, json, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public")
SITE = "https://pdfslimio.com"
BASE = "compress-image.html"

PAGES = [
{
 "slug": "compress-image-to-100kb", "target": "100KB",
 "title": "Compress Image to 100KB — Reduce Photo Size Online Free | SlimIO",
 "short": "Compress Image to 100KB | SlimIO",
 "desc": "Reduce a photo or image to under 100KB for job, exam and government upload forms. Keeps the best quality that fits. Free, no signup, runs in your browser.",
 "keywords": "compress image to 100kb, reduce photo size to 100kb, image under 100kb, photo 100kb, compress jpg to 100kb",
 "h1": "Compress images<br /><b>to 100KB.</b>",
 "lead": "Upload form says “photo under 100KB”? Drop your image in and get the sharpest version that fits.",
 "content": """
      <h2>How to compress an image to 100KB</h2>
      <ul>
          <li><b>1. Add your photo.</b> The target is already set to 100KB. You can add several photos at once.</li>
          <li><b>2. Click Compress images.</b> SlimIO lowers JPEG quality just enough to fit, and scales the photo down only if it still doesn't.</li>
          <li><b>3. Download</b> the photo, or all of them as a ZIP.</li>
      </ul>
      <h3>Where the 100KB limit shows up</h3>
      <p>Job application sites, exam registrations, school portals and government forms often cap photo uploads — especially ID photos — at 100KB. A phone photo is usually 2–5MB, so it needs to shrink by 95% or more.</p>
      <h3>ID photos: size and dimensions</h3>
      <p>Many forms ask for a specific pixel size as well, such as 3×4 cm. Pick the ID photo preset under Resize: the photo is cropped from the center to the right shape, scaled to 354×472px, and then kept under 100KB — at that size it usually stays very sharp.</p>
      <h3>Tips for a clearer result</h3>
      <ul>
          <li>Crop away background you don't need before compressing — fewer pixels means more quality per KB.</li>
          <li>Keep the format on JPG; almost every upload form accepts it.</li>
          <li>Location data (EXIF) is removed automatically, so the photo is safe to submit.</li>
      </ul>""",
 "faq": [
  ("How do I reduce a photo to 100KB for free?", "Drop the photo on this page — the target is already 100KB — and click Compress images. You get the best quality that fits, with no signup."),
  ("Will my photo look blurry at 100KB?", "For ID-sized photos, no. For a full phone photo, SlimIO first lowers JPEG quality and only then scales the image down, so it stays as sharp as 100KB allows."),
  ("Can I make an ID photo that is both 100KB and the right size?", "Yes. Choose the ID photo 3×4 cm preset under Resize. The photo is cropped and scaled to 354×472px, then compressed under 100KB."),
  ("Can I compress several photos to 100KB at once?", "Yes. Add as many as you like; each one is compressed to under 100KB and you can download them together as a ZIP."),
  ("Are my photos uploaded?", "No. Everything runs in your browser, so your photos never leave your device."),
 ],
},
{
 "slug": "compress-image-to-200kb", "target": "200KB",
 "title": "Compress Image to 200KB — Reduce Photo Size Online Free | SlimIO",
 "short": "Compress Image to 200KB | SlimIO",
 "desc": "Reduce a photo or image to under 200KB for applications, portals and email. Keeps the best quality that fits. Free, no signup, runs in your browser.",
 "keywords": "compress image to 200kb, reduce photo size to 200kb, image under 200kb, photo 200kb, compress jpg to 200kb",
 "h1": "Compress images<br /><b>to 200KB.</b>",
 "lead": "Need a photo under 200KB? SlimIO shrinks it to fit and keeps it as sharp as the limit allows.",
 "content": """
      <h2>How to compress an image to 200KB</h2>
      <ul>
          <li><b>1. Add your photos.</b> The target is already set to 200KB.</li>
          <li><b>2. Click Compress images.</b> Quality is lowered only as much as needed; the photo is scaled down only if that isn't enough.</li>
          <li><b>3. Download</b> each photo, or all of them as a ZIP.</li>
      </ul>
      <h3>Common places that ask for 200KB</h3>
      <p>University and scholarship applications, visa and membership forms, and online marketplaces often limit each photo to around 200KB. It's also a comfortable size for photos you attach to emails or documents.</p>
      <h3>What 200KB is enough for</h3>
      <p>At 200KB a photo can usually keep about 1600px on its longest side with good quality — plenty for viewing on screen or printing small. Product photos, portraits and scanned certificates all fit well.</p>
      <h3>Putting photos in a document?</h3>
      <p>Compress them here first, then combine them with <a href="/jpg-to-pdf.html">JPG to PDF</a>. The PDF comes out small from the start.</p>""",
 "faq": [
  ("How do I reduce a photo to 200KB?", "Drop it on this page and click Compress images — the target is already 200KB. SlimIO keeps the best quality that fits."),
  ("How big will the photo be in pixels?", "It depends on the photo, but most photos keep around 1600px on the longest side at 200KB."),
  ("Does compressing change the photo's colors?", "No. Colors stay the same; only fine detail is reduced slightly to save space."),
  ("Can I keep a transparent background?", "Choose WebP as the format. JPG has no transparency, so transparent areas turn white."),
  ("Are my photos uploaded?", "No. Everything runs in your browser, so your photos never leave your device."),
 ],
},
]

SIZE_LINKS = [("/compress-image.html", "Compress image (any size)"),
              ("/compress-image-to-100kb.html", "Compress image to 100KB"),
              ("/compress-image-to-200kb.html", "Compress image to 200KB")]


def sub1(pattern, repl, s, what):
    out, n = re.subn(pattern, repl, s, count=1, flags=re.S)
    if n != 1:
        sys.exit(f"[{what}] pattern not found: {pattern[:70]}")
    return out


def size_row(slug):
    links = "\n".join(f'          <a class="mini" href="{h}">{t}</a>' for h, t in SIZE_LINKS if h != f"/{slug}.html")
    return f'<div class="related sizes">\n      <h3>Compress to another size</h3>\n      <div class="tools-row">\n{links}\n      </div>\n</div>\n\n'


def with_size_row(s, slug):
    s = re.sub(r'<div class="related sizes">.*?</div>\n</div>\n\n', "", s, flags=re.S)   # idempotent
    return sub1(r'(<div class="related">\s*<h3>Related tools</h3>)', lambda m: size_row(slug) + m.group(1), s, slug)


def build(p, base):
    s, url = base, f"{SITE}/{p['slug']}.html"
    s = sub1(r"<title>.*?</title>", f"<title>{html.escape(p['title'])}</title>", s, "title")
    for attr, key, val in [("name", "description", p["desc"]), ("name", "keywords", p["keywords"]),
                           ("property", "og:title", p["title"]), ("property", "og:description", p["desc"]),
                           ("property", "og:url", url), ("name", "twitter:title", p["short"]),
                           ("name", "twitter:description", p["desc"])]:
        s = sub1(rf'(<meta {attr}="{re.escape(key)}" content=")[^"]*(")', lambda m: m.group(1) + html.escape(val, quote=True) + m.group(2), s, key)
    s = sub1(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), s, "canonical")

    def ld(m):
        obj = json.loads(m.group(1))
        if obj.get("@type") == "WebApplication":
            obj.update(name="SlimIO " + p["short"].split(" |")[0], url=url, description=p["desc"])
        elif obj.get("@type") == "FAQPage":
            obj["mainEntity"] = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]
        return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=6) + "\n</script>"
    s = re.sub(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', ld, s, flags=re.S)

    s = sub1(r'(<div class="hero">\s*<h1>).*?(</h1>\s*<p>).*?(</p>)', lambda m: m.group(1) + p["h1"] + m.group(2) + p["lead"] + m.group(3), s, "hero")
    s = s.replace('<option value="" selected>', '<option value="">')
    s = sub1(rf'<option value="{p["target"]}">', f'<option value="{p["target"]}" selected>', s, "target option")
    faq = "\n".join(f"      <details{' open' if i == 0 else ''}>\n          <summary>{html.escape(q)}</summary>\n          <p>{html.escape(a)}</p>\n      </details>"
                    for i, (q, a) in enumerate(p["faq"]))
    title = p["short"].split(" |")[0]
    s = sub1(r'<div class="content">.*?</div>\s*<section class="faq">.*?</section>',
             lambda m: f'<div class="content">{p["content"]}\n</div>\n\n<section class="faq">\n      <h2>{html.escape(title)} — FAQ</h2>\n{faq}\n</section>', s, "content")
    return with_size_row(s, p["slug"])


if __name__ == "__main__":
    base_path = os.path.join(ROOT, BASE)
    base = open(base_path).read()
    base = with_size_row(base, "compress-image")
    open(base_path, "w").write(base)
    for p in PAGES:
        open(os.path.join(ROOT, p["slug"] + ".html"), "w").write(build(p, base))
        print("wrote", p["slug"])
