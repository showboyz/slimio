import json, html, sys, os
# After generating, run tools/bump_versions.py to set the ?v= asset hashes.

OUT = sys.argv[1]

SIZES = ["50KB", "100KB", "150KB", "200KB", "300KB", "500KB", "1MB", "2MB", "5MB", "10MB", "20MB", "25MB"]
SIBLINGS = [
    ("/compress-pdf-to-50kb.html", "Compress to 50KB"),
    ("/compress-pdf-to-100kb.html", "Compress to 100KB"),
    ("/compress-pdf-to-200kb.html", "Compress to 200KB"),
    ("/compress-pdf-to-300kb.html", "Compress to 300KB"),
    ("/compress-pdf-to-500kb.html", "Compress to 500KB"),
    ("/compress-pdf-to-1mb.html", "Compress to 1MB"),
    ("/compress-pdf-to-2mb.html", "Compress to 2MB"),
    ("/compress-pdf-for-email.html", "Compress for email"),
]

PAGES = [
{
 "slug": "compress-pdf-to-50kb", "target": "50KB",
 "title": "Compress PDF to 50KB — Free Online, Keeps It Readable | SlimIO",
 "short": "Compress PDF to 50KB | SlimIO",
 "desc": "Compress a one-page PDF — certificate, ID proof or signed form — to under 50KB for online applications. Free, no signup, keeps the text as readable as the limit allows.",
 "keywords": "compress pdf to 50kb, pdf under 50kb, reduce pdf size to 50kb, pdf 50kb, compress pdf below 50kb, certificate pdf 50kb",
 "h1": "Compress PDF<br /><b>to 50KB.</b>",
 "lead": "50KB is tiny — about one scanned page. SlimIO finds the clearest version of your document that still fits.",
 "content": """
      <h2>How to compress a PDF to 50KB</h2>
      <ul>
          <li><b>1. Keep it to the page the form needs.</b> 50KB realistically holds one page. Use <a href="/delete-pages.html">Remove Pages</a> first if your file has more.</li>
          <li><b>2. Drop it in and click Compress.</b> The target is already 50KB. A text PDF usually fits as is; a scan is re-rendered at the highest resolution that fits.</li>
          <li><b>3. Check it before you upload.</b> Open the result and zoom in on the smallest text, like a certificate number.</li>
      </ul>
      <h3>What fits in 50KB</h3>
      <p>A one-page PDF made from Word or a web form is often only 20–40KB already. A scanned page is different: a phone scan in color can be 1–3MB, so it has to shrink 20–60 times. At 50KB a grayscale scan of an A4 page stays readable at around 100 dpi; a color photo of a document gets noticeably soft.</p>
      <h3>Scan it so it compresses well</h3>
      <ul>
          <li>Scan in <b>grayscale</b> (or black &amp; white), not color — it's the biggest saving.</li>
          <li>Put the page on a dark, plain surface and fill the frame, so there is no desk or shadow around it.</li>
          <li>150 dpi is plenty; 300 dpi only makes the file bigger before we shrink it back.</li>
      </ul>
      <h3>Does the form accept JPG too?</h3>
      <p>If the form accepts an image instead of a PDF, a JPG of the same page is often clearer at 50KB. Use <a href="/compress-image-to-50kb.html">Compress image to 50KB</a> for that.</p>""",
 "faq": [
  ("How do I compress a PDF to 50KB?", "Drop your PDF on this page and click Compress — the target is already 50KB. SlimIO tries to keep the text first and only turns the page into an image if that's the only way to fit."),
  ("Can a 3-page PDF fit in 50KB?", "Only if the pages are mostly text created digitally. Three scanned pages at 50KB come out blurry. Remove pages the form doesn't need, or upload them separately if it allows."),
  ("Why does my scanned certificate look soft after compressing?", "To reach 50KB a color scan has to lose a lot of detail. Rescan it in grayscale at 150 dpi and compress again — the result is usually much sharper."),
  ("The form needs between 20KB and 50KB. Will this work?", "SlimIO aims for the best quality under 50KB, so the result is usually well above 20KB unless the original was already small. Check the size shown on the result."),
  ("Is my document uploaded?", "The image step runs entirely in your browser. The text-preserving step sends the file to our server over HTTPS and deletes it as soon as it is compressed; nothing is kept."),
 ],
},
{
 "slug": "compress-pdf-to-300kb", "target": "300KB",
 "title": "Compress PDF to 300KB — Free for Certificates & Mark Sheets | SlimIO",
 "short": "Compress PDF to 300KB | SlimIO",
 "desc": "Compress scanned certificates, mark sheets and multi-page documents to under 300KB for application portals. Free, no signup, keeps the best quality that fits.",
 "keywords": "compress pdf to 300kb, pdf under 300kb, reduce pdf size to 300kb, pdf 300kb, compress pdf below 300kb, mark sheet pdf 300kb",
 "h1": "Compress PDF<br /><b>to 300KB.</b>",
 "lead": "Portal asks for each document under 300KB? Shrink your scans to fit and keep every page readable.",
 "content": """
      <h2>How to compress a PDF to 300KB</h2>
      <ul>
          <li><b>1. Put the pages together.</b> If the portal wants one file per document, combine the scans with <a href="/merge.html">Merge PDF</a> or photos with <a href="/jpg-to-pdf.html">JPG to PDF</a>.</li>
          <li><b>2. Drop the PDF in and click Compress.</b> The target is already 300KB.</li>
          <li><b>3. Download and check.</b> The result shows the final size and whether the text is still selectable.</li>
      </ul>
      <h3>Where 300KB shows up</h3>
      <p>Admission, scholarship and recruitment portals often ask for each supporting document — mark sheets, degree certificates, experience letters, category or income certificates — as a PDF under 300KB. That's roughly two to five scanned pages.</p>
      <h3>Why phone scans come out so big</h3>
      <p>Scanning apps save every page as a high-resolution color photo, so a three-page scan is easily 5–10MB. SlimIO first tries a compression that keeps the text; if the file is still over 300KB, it re-renders the pages at the highest resolution that fits.</p>
      <h3>Several documents to upload?</h3>
      <ul>
          <li>Compress each document separately so each gets the full 300KB.</li>
          <li>Leave out blank backs of pages with <a href="/delete-pages.html">Remove Pages</a> — they cost as much space as a full page.</li>
          <li>Rotate sideways scans with <a href="/rotate.html">Rotate PDF</a> before compressing so they read the right way up.</li>
      </ul>""",
 "faq": [
  ("How do I reduce a PDF to 300KB?", "Drop it on this page and click Compress. The target is preset to 300KB, and SlimIO keeps the sharpest version that fits. No signup."),
  ("How many pages fit in 300KB?", "Digitally created PDFs can have dozens of pages. For scans, about two to five pages stay clearly readable."),
  ("Can I combine several certificates into one PDF under 300KB?", "Yes. Merge them first with Merge PDF (or JPG to PDF for photos), then compress the merged file here."),
  ("Will colored stamps and seals still show?", "Yes. Colors are kept; only fine detail is reduced to reach the target."),
  ("Is there a limit on how often I can use it?", "The free tier includes a daily number of operations. No signup is needed."),
 ],
},
{
 "slug": "compress-pdf-to-2mb", "target": "2MB",
 "title": "Compress PDF to 2MB — Free, Keeps Text Sharp | SlimIO",
 "short": "Compress PDF to 2MB | SlimIO",
 "desc": "Compress a PDF to under 2MB for university, bank, insurance and government upload portals. At 2MB most documents keep sharp, selectable text. Free, no signup.",
 "keywords": "compress pdf to 2mb, pdf under 2mb, reduce pdf size to 2mb, pdf 2mb, compress pdf less than 2mb, scanned pdf 2mb",
 "h1": "Compress PDF<br /><b>to 2MB.</b>",
 "lead": "Upload limit of 2MB? Most PDFs fit with text that stays crisp, selectable and searchable.",
 "content": """
      <h2>How to compress a PDF to 2MB</h2>
      <ul>
          <li><b>1. Add your PDF.</b> The target is already 2MB.</li>
          <li><b>2. Click Compress.</b> At this size SlimIO uses a gentler setting that keeps text as real text and only resamples large images.</li>
          <li><b>3. Download.</b> The result tells you whether the text is still selectable.</li>
      </ul>
      <h3>Where 2MB limits are common</h3>
      <p>University application systems, bank and insurance document uploads, visa and tender portals, and many HR systems cap each file at 2MB. Typical files that go over: scanning-app PDFs, reports with photos, slides saved as PDF, and theses with figures.</p>
      <h3>Why a scanning app's PDF is 15MB</h3>
      <p>Apps like phone scanners store each page as a full-resolution photo — often 2–4MB per page. Those photos are what SlimIO shrinks; the page itself keeps its layout. A 10-page scan usually fits under 2MB with readable text.</p>
      <h3>Keep it searchable</h3>
      <p>Reviewers often search inside PDFs. At 2MB, digitally created documents almost always keep their text layer, so names and numbers stay searchable and copyable. If a file can only fit by turning pages into images, SlimIO tells you on the result.</p>""",
 "faq": [
  ("How do I make a PDF smaller than 2MB?", "Drop it on this page and click Compress. The target is already 2MB; SlimIO keeps text sharp and reduces only the images as much as needed."),
  ("Will my PDF stay searchable at 2MB?", "Almost always for documents created on a computer. Scanned pages were images to begin with, so they stay images — just smaller."),
  ("My phone scan is 15MB. Can it get under 2MB?", "Usually, yes. Most of that size is high-resolution photos of each page, which compress very well."),
  ("Can I compress several PDFs to 2MB each?", "Yes. Compress them one after another; each file gets its own 2MB target."),
  ("Is my file uploaded?", "Files up to 50MB are compressed on our server over HTTPS with a text-preserving method and deleted right after. The image step runs only in your browser."),
 ],
},
{
 "slug": "compress-pdf-to-100kb", "target": "100KB",
 "title": "Compress PDF to 100KB — Free Online, No Signup | SlimIO",
 "short": "Compress PDF to 100KB | SlimIO",
 "desc": "Compress a PDF to under 100KB for job, exam and government upload forms. Free, no signup, runs in your browser — your file never leaves your device.",
 "keywords": "compress pdf to 100kb, pdf under 100kb, reduce pdf size to 100kb, pdf size reducer 100kb, compress pdf below 100kb",
 "h1": "Compress PDF<br /><b>to 100KB.</b>",
 "lead": "Upload forms that say “max 100KB”? Drop your PDF in and get a file that fits — with the best quality that still squeezes under the limit.",
 "content": """
      <h2>How to compress a PDF to 100KB</h2>
      <ul>
          <li><b>1. Add your PDF.</b> Drop it in or click to browse. The target is already set to 100KB.</li>
          <li><b>2. Click Compress.</b> SlimIO first tries a text-preserving compression. If the file is still too big, it lowers image resolution step by step until it fits.</li>
          <li><b>3. Download.</b> You get the sharpest version that is under 100KB.</li>
      </ul>
      <h3>Where the 100KB limit shows up</h3>
      <p>Online job applications, exam registrations and government service portals often cap each upload at 100KB — usually for scanned certificates, ID proofs, mark sheets or signed forms.</p>
      <h3>What realistically fits in 100KB</h3>
      <p>One or two scanned pages compress well to 100KB and stay readable. A text-only PDF made from Word is often already under the limit. A long scan of 10+ pages will fit only at low resolution, and small print may blur.</p>
      <h3>Tips for a clearer result</h3>
      <ul>
          <li>Upload only the pages the form asks for — use <a href="/delete-pages.html">Remove Pages</a> or <a href="/split.html">Split PDF</a> first.</li>
          <li>If you are scanning, choose grayscale at 150–200 dpi. Color scans take far more space.</li>
          <li>Crop away empty margins before scanning where you can.</li>
      </ul>""",
 "faq": [
  ("How do I compress a PDF to 100KB for free?", "Open this page, drop in your PDF and click Compress. The target is preset to 100KB. SlimIO keeps the best quality that fits and the file downloads right away — no signup or install."),
  ("Why is my PDF still over 100KB?", "Very long or very detailed scans can't always get under 100KB and stay legible. SlimIO then gives you the smallest version it could make. Remove pages you don't need, or split the file and upload the parts separately."),
  ("Will the text still be readable at 100KB?", "For one or two pages, yes. SlimIO lowers resolution only as much as needed to reach the target, so short documents stay clear."),
  ("Can I still select or copy text after compressing?", "If the text-preserving step reaches 100KB, yes. If pages have to be turned into images to hit the target, the text is no longer selectable — the result tells you which one happened."),
  ("Is it safe to compress my documents here?", "The image step runs entirely in your browser. The text-preserving step sends the file to our server over HTTPS and deletes it as soon as it is compressed; nothing is kept."),
 ],
},
{
 "slug": "compress-pdf-to-200kb", "target": "200KB",
 "title": "Compress PDF to 200KB — Free Online, No Signup | SlimIO",
 "short": "Compress PDF to 200KB | SlimIO",
 "desc": "Compress a PDF to under 200KB for visa, admission and scholarship applications. Free, no signup, keeps the best quality that fits.",
 "keywords": "compress pdf to 200kb, pdf under 200kb, reduce pdf size to 200kb, pdf compressor 200kb, compress pdf less than 200kb",
 "h1": "Compress PDF<br /><b>to 200KB.</b>",
 "lead": "Need a PDF under 200KB for an application form? SlimIO shrinks it to fit and keeps it as sharp as the limit allows.",
 "content": """
      <h2>How to compress a PDF to 200KB</h2>
      <ul>
          <li><b>1. Add your PDF.</b> The target is preset to 200KB — change it if your form asks for something else.</li>
          <li><b>2. Click Compress.</b> SlimIO tries text-preserving compression first, then steps image resolution down only if it has to.</li>
          <li><b>3. Download</b> the version that fits.</li>
      </ul>
      <h3>Common places that ask for 200KB</h3>
      <p>Visa and passport portals, university admission systems and scholarship applications often limit supporting documents — transcripts, bank statements, recommendation letters — to around 200KB per file.</p>
      <h3>How many pages fit in 200KB?</h3>
      <p>Roughly two to four scanned pages stay comfortably readable at 200KB. Digitally created PDFs (exported from Word or Google Docs) with a few images usually fit with text still sharp and selectable.</p>
      <h3>Get a sharper file</h3>
      <ul>
          <li>Merge only the pages you need with <a href="/merge.html">Merge PDF</a> or trim extras with <a href="/delete-pages.html">Remove Pages</a>.</li>
          <li>Pages scanned sideways? Fix them with <a href="/rotate.html">Rotate PDF</a> before uploading.</li>
          <li>Prefer grayscale scans for text documents — they compress much smaller than color.</li>
      </ul>""",
 "faq": [
  ("How do I reduce a PDF to 200KB?", "Drop your PDF on this page and click Compress — the target is already 200KB. SlimIO finds the best quality that fits and downloads it. Free, no signup."),
  ("My transcript is 5 pages. Will it fit in 200KB?", "Usually yes, if it was exported digitally. A 5-page scan may need lower resolution; SlimIO picks the highest resolution that still fits under 200KB."),
  ("Does compressing change my document's content?", "No. Pages, order and paper size stay the same. Only image detail is reduced."),
  ("Can I choose a different size?", "Yes. Use the target menu to pick anything from 50KB to 25MB."),
  ("Why does the result say text is not selectable?", "To reach small sizes, SlimIO sometimes has to turn pages into images. That keeps the look but drops selectable text. Forms that only need a readable copy accept this fine."),
 ],
},
{
 "slug": "compress-pdf-to-500kb", "target": "500KB",
 "title": "Compress PDF to 500KB — Free Online, No Signup | SlimIO",
 "short": "Compress PDF to 500KB | SlimIO",
 "desc": "Compress a PDF to under 500KB for resume uploads and online applications. Text stays sharp in most documents. Free, no signup.",
 "keywords": "compress pdf to 500kb, pdf under 500kb, reduce pdf size to 500kb, resume pdf 500kb, compress pdf less than 500kb",
 "h1": "Compress PDF<br /><b>to 500KB.</b>",
 "lead": "Resume portal says 500KB max? Shrink your PDF to fit — for most documents the text stays crisp and selectable.",
 "content": """
      <h2>How to compress a PDF to 500KB</h2>
      <ul>
          <li><b>1. Add your PDF.</b> The target is preset to 500KB.</li>
          <li><b>2. Click Compress.</b> SlimIO runs text-preserving compression first — at 500KB that is usually enough.</li>
          <li><b>3. Download</b> your file, ready to upload.</li>
      </ul>
      <h3>Resumes and cover letters</h3>
      <p>Applicant tracking systems and job boards often cap resume uploads at 500KB. Resumes with a photo, a designed template or embedded fonts can easily go over. At 500KB there is enough room to keep text sharp, so recruiters can still search and copy from your resume.</p>
      <h3>Other documents that fit well</h3>
      <p>Portfolios of a few pages, signed contracts, insurance claim documents and multi-page scans of up to about ten pages usually fit under 500KB with good readability.</p>
      <h3>Keep your resume searchable</h3>
      <ul>
          <li>Start from the original exported PDF, not a scan or photo of a printout.</li>
          <li>Large background images and full-page graphics take the most space — remove them if you can.</li>
          <li>Add <a href="/add-page-numbers.html">page numbers</a> to longer documents so reviewers can follow along.</li>
      </ul>""",
 "faq": [
  ("How do I compress my resume PDF to under 500KB?", "Drop the PDF on this page and click Compress. SlimIO keeps text selectable whenever it can and only reduces image detail. The file downloads right away."),
  ("Will recruiters still be able to search my resume?", "Yes, if the text-preserving step reaches 500KB — which it does for most resumes. The result tells you whether text stayed selectable."),
  ("Is 500KB enough for a 10-page document?", "For digitally created PDFs, usually yes. For scans, around ten pages fit with readable text."),
  ("Does SlimIO add a watermark?", "No. Your compressed PDF has no watermark and no branding."),
  ("Is there a limit on how often I can use it?", "The free tier includes a daily number of operations. No signup is needed."),
 ],
},
{
 "slug": "compress-pdf-to-1mb", "target": "1MB",
 "title": "Compress PDF to 1MB — Free Online, No Signup | SlimIO",
 "short": "Compress PDF to 1MB | SlimIO",
 "desc": "Compress a PDF to under 1MB for web forms, school portals and uploads. Keeps text sharp and selectable in most files. Free, no signup.",
 "keywords": "compress pdf to 1mb, pdf under 1mb, reduce pdf size to 1mb, compress pdf less than 1mb, pdf 1mb converter",
 "h1": "Compress PDF<br /><b>to 1MB.</b>",
 "lead": "Get any PDF under 1MB for forms, portals and uploads. At 1MB, most files keep sharp, selectable text.",
 "content": """
      <h2>How to compress a PDF to 1MB</h2>
      <ul>
          <li><b>1. Add your PDF.</b> The target is preset to 1MB.</li>
          <li><b>2. Click Compress.</b> Text-preserving compression runs first; image conversion is only used if the file is still too big.</li>
          <li><b>3. Download</b> the file under 1MB.</li>
      </ul>
      <h3>Where 1MB limits are common</h3>
      <p>School and university assignment portals, HR and onboarding systems, customer support forms and many website contact forms cap attachments at 1MB. Slide decks exported to PDF, reports with charts and photo-heavy documents are the files that usually go over.</p>
      <h3>What to expect</h3>
      <p>Most text-based documents and reports fit under 1MB with text kept sharp. Presentations with many full-slide photos may need image conversion; SlimIO still keeps the highest resolution that fits.</p>
      <h3>Still too big?</h3>
      <ul>
          <li>Split a long file into parts with <a href="/split.html">Split PDF</a> and upload each separately.</li>
          <li>Drop appendix or blank pages with <a href="/delete-pages.html">Remove Pages</a>.</li>
          <li>For full control over quality settings, use the main <a href="/">PDF compressor</a>.</li>
      </ul>""",
 "faq": [
  ("How can I make a PDF smaller than 1MB?", "Drop it on this page and click Compress. The target is already 1MB and SlimIO keeps the best quality that fits. Free, no signup."),
  ("Will my slides and charts stay sharp?", "Charts and text usually stay sharp at 1MB. Large photos are the part that gets compressed."),
  ("My PDF is 30MB. Can it get under 1MB?", "Often, yes, especially if most of the size comes from photos. Very long documents may lose some detail; split them if the result isn't clear enough."),
  ("What's the difference between this and the main compressor?", "The main compressor lets you set quality by hand. This page aims for a size — it finds the settings that land under 1MB for you."),
  ("Is my file uploaded?", "The text-preserving step is processed on our server over HTTPS and deleted immediately. The image step runs only in your browser."),
 ],
},
{
 "slug": "compress-pdf-for-email", "target": "10MB",
 "title": "Compress PDF for Email — Shrink PDF to Send | SlimIO",
 "short": "Compress PDF for Email | SlimIO",
 "desc": "PDF too large to email? Shrink it under Gmail, Outlook and company attachment limits. Free, no signup, keeps the best quality that fits.",
 "keywords": "compress pdf for email, pdf too large to email, reduce pdf size for email, shrink pdf to send, pdf attachment too big",
 "h1": "PDF too big<br /><b>to email?</b>",
 "lead": "Shrink your PDF under Gmail, Outlook or your company's attachment limit — keeping it as sharp as possible.",
 "content": """
      <h2>How to compress a PDF for email</h2>
      <ul>
          <li><b>1. Add your PDF.</b> The target is preset to 10MB, which gets through almost any mail server.</li>
          <li><b>2. Pick a limit</b> if you know it — see the table below — and click Compress.</li>
          <li><b>3. Download and attach.</b></li>
      </ul>
      <h3>Email attachment limits</h3>
      <ul>
          <li><b>Gmail:</b> 25MB total per message.</li>
          <li><b>Outlook.com:</b> 20MB per message for regular attachments.</li>
          <li><b>Yahoo Mail:</b> 25MB per message.</li>
          <li><b>Work email:</b> company mail servers are often set to 10MB, and the recipient's server limit applies too.</li>
      </ul>
      <h3>Why a 20MB file can bounce from a 25MB inbox</h3>
      <p>Attachments are encoded for sending, which makes them roughly a third larger in transit. A 20MB PDF can travel as about 27MB and be rejected. Aim for a file comfortably below the limit — 10MB is a safe choice when you don't know the recipient's setup.</p>
      <h3>Sending several documents?</h3>
      <p>Combine them with <a href="/merge.html">Merge PDF</a> first, then compress once. If one message still can't fit everything, use <a href="/split.html">Split PDF</a> and send the parts in separate emails.</p>""",
 "faq": [
  ("How do I make a PDF small enough to email?", "Drop it on this page and click Compress. The default 10MB target fits nearly every email service. The compressed PDF downloads right away."),
  ("What size should a PDF be for Gmail?", "Gmail allows 25MB per message, but encoding adds about a third in transit. Keep the PDF under about 18MB — or pick 10MB to be safe."),
  ("Why was my email rejected even though the file is under the limit?", "The recipient's mail server may have a smaller limit, and attachments grow when encoded for sending. Compress to 10MB or less."),
  ("Will the recipient see a lower-quality PDF?", "SlimIO keeps text sharp whenever it can and only reduces image detail as much as needed. For typical documents the difference is hard to notice."),
  ("Is there a size limit for the file I upload?", "Files up to 50MB get text-preserving compression on our server. Larger files are compressed entirely in your browser."),
 ],
},
]

HEAD_TPL = open(os.path.join(os.path.dirname(__file__), "size_template.html")).read()

for p in PAGES:
    url = f"https://pdfslimio.com/{p['slug']}.html"
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}
    app_ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "SlimIO " + p["short"].split(" |")[0],
              "url": url, "description": p["desc"], "applicationCategory": "UtilityApplication", "operatingSystem": "Any",
              "browserRequirements": "Requires a modern web browser", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}
    faq_html = "\n".join(
        f"      <details{' open' if i == 0 else ''}>\n          <summary>{html.escape(q)}</summary>\n          <p>{html.escape(a)}</p>\n      </details>"
        for i, (q, a) in enumerate(p["faq"]))
    opts = "\n".join(f'                       <option value="{s}"{" selected" if s == p["target"] else ""}>Under {s}</option>' for s in SIZES)
    sib = "\n".join(f'          <a class="mini" href="{h}">{t}</a>' for h, t in SIBLINGS if h != f"/{p['slug']}.html")
    out = HEAD_TPL
    for k, v in {
        "TITLE": html.escape(p["title"]), "SHORT": html.escape(p["short"]), "DESC": html.escape(p["desc"]),
        "KEYWORDS": p["keywords"], "URL": url, "APP_LD": json.dumps(app_ld, indent=6), "FAQ_LD": json.dumps(faq_ld, indent=6),
        "H1": p["h1"], "LEAD": p["lead"], "OPTIONS": opts, "CONTENT": p["content"], "FAQ": faq_html,
        "FAQ_TITLE": html.escape(p["short"].split(" |")[0]), "SIBLINGS": sib, "TARGET": p["target"],
    }.items():
        out = out.replace("{{" + k + "}}", v)
    assert "{{" not in out, p["slug"]
    open(os.path.join(OUT, p["slug"] + ".html"), "w").write(out)
    print("wrote", p["slug"])
