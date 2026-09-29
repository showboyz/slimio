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
 "slug": "compress-id-photo", "target": "100KB", "resize": "id-3x4",
 "title": "Passport & ID Photo Resizer — Crop and Compress to KB Free | SlimIO",
 "short": "ID Photo Resizer | SlimIO",
 "desc": "Crop a photo to passport or ID size (3.5×4.5 cm, 3×4 cm) and compress it under 100KB, 50KB or 20KB for online applications. Free, runs in your browser.",
 "keywords": "passport size photo resize, id photo resizer, passport photo size in kb, resize photo for online application, 3.5x4.5 photo, compress id photo",
 "h1": "ID &amp; passport photos,<br /><b>the right size.</b>",
 "lead": "Crop to 3×4 cm or 3.5×4.5 cm and get under the KB limit in one step — ready for online application forms.",
 "content": """
      <h2>How to resize an ID or passport photo</h2>
      <ul>
          <li><b>1. Add your photo.</b> The ID photo 3×4 cm preset and a 100KB target are already selected.</li>
          <li><b>2. Match the form.</b> Switch Resize to Passport photo 3.5×4.5 cm if needed, and pick the KB limit the form states (for example 50KB or 20KB).</li>
          <li><b>3. Click Compress images and download.</b> The photo is cropped from the center, scaled and compressed in one go.</li>
      </ul>
      <h3>Photo sizes at a glance</h3>
      <ul>
          <li><b>3×4 cm</b> → 354×472px. Common on résumés, job and exam applications.</li>
          <li><b>3.5×4.5 cm</b> → 413×531px. The usual passport-size photo, also used for many ID cards and visa forms.</li>
      </ul>
      <p>Both are 300 dpi — sharp enough to print at the stated size. Always check the exact size and KB range in the form's instructions; they differ from site to site.</p>
      <h3>Getting a good crop</h3>
      <p>The presets crop from the center, so start with a photo where your face is roughly in the middle, taken straight on against a plain, light background. Leave some space above your head: most rules want the head to fill a bit over half of the photo's height.</p>
      <h3>Safe to submit</h3>
      <p>Everything happens in your browser — the photo is never uploaded. Location and camera data (EXIF) are removed when the photo is saved again.</p>""",
 "faq": [
  ("How do I resize a photo to passport size online?", "Drop your photo here, choose Passport photo 3.5×4.5 cm under Resize, pick the KB limit your form asks for and click Compress images. You get a 413×531px JPG under that limit."),
  ("What size in KB should a passport or ID photo be?", "It depends on the form — common limits are 20–50KB, 100KB or 200KB. Select the limit from the target list; SlimIO keeps the best quality that fits."),
  ("Why was my photo cropped wrong?", "The presets crop from the center. If your face isn't centered, crop the photo roughly around your head and shoulders first, then use the preset."),
  ("Can I change the background color?", "No. SlimIO resizes and compresses but doesn't edit the background, so take the photo against a plain light wall."),
  ("Are my photos uploaded?", "No. Everything runs in your browser, so your photos never leave your device."),
 ],
},
{
 "slug": "compress-image-to-50kb", "target": "50KB",
 "title": "Compress Image to 50KB — Reduce Photo Size Online Free | SlimIO",
 "short": "Compress Image to 50KB | SlimIO",
 "desc": "Reduce a photo to under 50KB for exam, job and government application forms. Crops ID photos to size and keeps the best quality that fits. Free, runs in your browser.",
 "keywords": "compress image to 50kb, reduce photo size to 50kb, photo under 50kb, image 50kb, compress jpg to 50kb, photo resize 50kb",
 "h1": "Compress images<br /><b>to 50KB.</b>",
 "lead": "Application form wants a photo under 50KB? Drop it in and get the sharpest version that fits.",
 "content": """
      <h2>How to compress an image to 50KB</h2>
      <ul>
          <li><b>1. Add your photo.</b> The target is already set to 50KB.</li>
          <li><b>2. Pick a size if the form asks for one.</b> Under Resize, the ID and passport presets crop the photo to the right shape.</li>
          <li><b>3. Click Compress images and download.</b> SlimIO finds the highest JPEG quality that still fits under 50KB.</li>
      </ul>
      <h3>Where the 50KB limit shows up</h3>
      <p>Online applications for exams, government jobs, scholarships and admissions often ask for a passport-style photo between 20KB and 50KB. A phone photo is usually 2–5MB, around 50–100 times too big, so it has to shrink a lot without turning blurry.</p>
      <h3>Why a cropped photo looks better at 50KB</h3>
      <p>The same 50KB spread over fewer pixels means more detail per pixel. An ID-size photo (354×472px) fits comfortably under 50KB with sharp facial detail, while a full-frame photo has to be scaled down much further. Crop to your face and shoulders — or use the ID photo preset — before compressing.</p>
      <h3>Checklist before you upload</h3>
      <ul>
          <li>Format: keep JPG. Most forms accept only JPG/JPEG.</li>
          <li>Dimensions: if the form gives pixels or cm, use the matching Resize preset.</li>
          <li>File size: the result card shows the final size, so you can check it against the limit.</li>
      </ul>""",
 "faq": [
  ("How do I reduce a photo to 50KB for an application form?", "Drop the photo on this page — the target is already 50KB — and click Compress images. If the form also asks for ID or passport dimensions, choose that preset under Resize first."),
  ("Will a 50KB photo be clear enough?", "Yes, at ID-photo dimensions. A 354×472px photo keeps sharp facial detail under 50KB. Larger photos are scaled down step by step until they fit, keeping the best quality possible."),
  ("The form says the photo must be between 20KB and 50KB. Will this work?", "Usually, yes. SlimIO picks the highest quality that fits under 50KB, so ID-size photos normally come out well above 20KB. Check the size shown on the result."),
  ("Can I compress my signature image to 50KB too?", "Yes. Crop the signature tightly, then compress it here. If the form asks for a smaller signature file, use the 20KB page."),
  ("Are my photos uploaded?", "No. Everything runs in your browser, so your photos never leave your device."),
 ],
},
{
 "slug": "compress-image-to-20kb", "target": "20KB",
 "title": "Compress Image to 20KB — Photo & Signature Size Reducer Free | SlimIO",
 "short": "Compress Image to 20KB | SlimIO",
 "desc": "Reduce a photo or signature image to under 20KB for online exam and job forms. Keeps the best quality that fits. Free, no signup, runs in your browser.",
 "keywords": "compress image to 20kb, reduce photo size to 20kb, signature 20kb, photo under 20kb, image 20kb, compress jpg to 20kb, signature resize",
 "h1": "Compress images<br /><b>to 20KB.</b>",
 "lead": "Photo or signature must be under 20KB? SlimIO squeezes it down and keeps it readable.",
 "content": """
      <h2>How to compress an image to 20KB</h2>
      <ul>
          <li><b>1. Add your photo or signature scan.</b> The target is already set to 20KB.</li>
          <li><b>2. Crop first if you can.</b> For a photo, the ID photo preset under Resize crops and scales it for you.</li>
          <li><b>3. Click Compress images and download.</b> Quality is lowered just enough to fit, then the image is scaled down only if needed.</li>
      </ul>
      <h3>Signatures under 20KB</h3>
      <p>Many online application forms ask for a scanned signature between 10KB and 20KB. Sign in black or dark blue ink on plain white paper, take the photo in good light, and crop tightly around the signature. A cropped signature fits under 20KB easily and stays crisp.</p>
      <h3>Photos under 20KB</h3>
      <p>20KB is very small for a photo, so dimensions matter most. Choose the ID photo 3×4 cm preset (354×472px) — the face stays recognizable at that size. A full phone photo would have to be scaled down to a few hundred pixels to fit.</p>
      <h3>If it still looks too soft</h3>
      <ul>
          <li>Crop away as much background as the form allows.</li>
          <li>Keep JPG as the format; PNG is lossless and rarely fits under 20KB.</li>
          <li>Check whether the form allows a bigger file, such as <a href="/compress-image-to-50kb.html">50KB</a>, for the photo.</li>
      </ul>""",
 "faq": [
  ("How do I compress a signature to 20KB?", "Crop the scanned signature tightly, drop it on this page — the target is already 20KB — and click Compress images. Signatures are simple images, so they stay sharp at this size."),
  ("Can a photo really fit under 20KB?", "Yes, at ID-photo size. Choose the ID photo 3×4 cm preset under Resize; the photo is scaled to 354×472px and then compressed under 20KB."),
  ("Why does my photo get smaller in pixels?", "If lowering the JPEG quality isn't enough to reach 20KB, SlimIO scales the image down 20% at a time until it fits. Cropping first keeps more detail."),
  ("Should I use JPG or PNG for 20KB?", "JPG. PNG keeps every pixel exactly and is usually much larger, so it rarely fits under 20KB."),
  ("Are my files uploaded?", "No. Everything runs in your browser, so your photos and signatures never leave your device."),
 ],
},
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
              ("/compress-image-to-20kb.html", "Compress image to 20KB"),
              ("/compress-image-to-50kb.html", "Compress image to 50KB"),
              ("/compress-image-to-100kb.html", "Compress image to 100KB"),
              ("/compress-image-to-200kb.html", "Compress image to 200KB"),
              ("/compress-id-photo.html", "ID / passport photo")]


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
    if p.get("resize"):
        s = sub1(r'<option value="1920" selected>', '<option value="1920">', s, "default resize")
        s = sub1(rf'<option value="{p["resize"]}">', f'<option value="{p["resize"]}" selected>', s, "resize option")
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
