#!/usr/bin/env python3
"""Build the guides section (public/guides/, public/ko/guides/) from content/guides/.

Each article is an HTML fragment in content/guides/<lang>/<slug>.html whose first line is
an HTML comment holding JSON metadata:

    <!--
    {"title": "...", "seo_title": "...", "desc": "...", "published": "2026-10-09",
     "updated": "2026-10-09", "image": "/img/blog/x.jpg",
     "cta": ["/signature-image.html", "Make your signature image", "One line about the tool"],
     "faq": [["Question?", "Answer."], ...]}
    -->
    <p>Body…</p>

Articles exist in one language only (no hreflang pair); the two hub pages are paired.
This also adds a Guides link to every page footer. Run it before gen_ko.py, which
rebuilds the Korean tool pages from the English ones:

    python3 tools/gen_guides.py && python3 tools/gen_ko.py && python3 tools/gen_llms.py && python3 tools/bump_versions.py
"""
import glob, html, json, os, re, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "public")
SRC = os.path.join(HERE, "..", "content", "guides")
SITE = "https://pdfslimio.com"
ADSENSE = "ca-pub-5339352429300786"
UMAMI = "ab53f00a-b92a-4d4d-aaf0-6b5329869de7"

T = {
    "en": dict(guides="Guides", home="SlimIO", compress="Compress", all_tools="All tools", by="By SlimIO",
               updated="Updated", read="min read", faq="Questions", more="More guides", try_it="Try it free",
               hub_title="Guides — Photo, Signature and PDF Size Help | SlimIO",
               hub_h1="Guides", hub_lead="Practical, sourced answers for the size rules on application forms: photos, signatures and PDFs.",
               hub_desc="Guides to photo, signature and PDF size requirements for exam and job applications, with the official numbers and how to meet them.",
               other_lang="한국어 가이드", other_flag="/img/flag-kr.svg",
               foot=('<a href="/about.html">About</a> · <a href="/terms.html">Terms</a> · <a href="/privacy.html">Privacy Policy</a> · <a href="/contact.html">Contact</a>'),
               foot2="© 2026 SlimIO · Free PDF tools", foot3="Runs in your browser · No signup",
               months=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]),
    "ko": dict(guides="가이드", home="SlimIO", compress="PDF 압축", all_tools="전체 도구", by="SlimIO 작성",
               updated="업데이트", read="분 분량", faq="자주 묻는 질문", more="다른 가이드", try_it="무료로 해 보기",
               hub_title="가이드 — 사진·서명·PDF 용량 규격 정리 | SlimIO",
               hub_h1="가이드", hub_lead="원서·서류 제출에서 막히는 사진, 서명, PDF 규격을 공식 기준과 함께 정리했어요.",
               hub_desc="시험 원서 사진 규격, PDF 용량 줄이기 원리 등 서류 제출에 필요한 사진·서명·PDF 규격을 공식 기준과 함께 정리한 가이드.",
               other_lang="English guides", other_flag="/img/flag-us.svg",
               foot=('<a href="/ko/about.html">서비스 소개</a> · <a href="/ko/terms.html">이용약관</a> · <a href="/ko/privacy.html">개인정보처리방침</a> · <a href="/ko/contact.html">문의하기</a>'),
               foot2="© 2026 SlimIO · 무료 PDF 도구", foot3="브라우저에서 처리 · 회원가입 없음",
               months=None),
}


def hub_path(lang): return "/guides/" if lang == "en" else "/ko/guides/"
def art_path(lang, slug): return hub_path(lang) + slug + ".html"


def fmt_date(iso, lang):
    d = datetime.date.fromisoformat(iso)
    return f"{T['en']['months'][d.month - 1]} {d.day}, {d.year}" if lang == "en" else f"{d.year}년 {d.month}월 {d.day}일"


def load():
    arts = []
    for lang in ("en", "ko"):
        for f in sorted(glob.glob(os.path.join(SRC, lang, "*.html"))):
            s = open(f).read()
            m = re.match(r"\s*<!--(.*?)-->\s*", s, re.S)
            meta = json.loads(m.group(1))
            body = s[m.end():].strip()
            words = len(re.sub(r"<[^>]+>", " ", body).split())
            chars = len(re.sub(r"\s", "", re.sub(r"<[^>]+>", "", body)))
            minutes = max(2, round(words / 220)) if lang == "en" else max(2, round(chars / 500))
            arts.append(dict(meta, lang=lang, slug=os.path.basename(f)[:-5], body=body, minutes=minutes, words=words))
    return arts


def head(lang, title, desc, path, og_type="article", image=None, alternates=None, ld=()):
    t = T[lang]
    alt = ""
    if alternates:
        alt = "".join(f'<link rel="alternate" hreflang="{hl}" href="{SITE}{p}" />\n' for hl, p in alternates)
    img = f'<meta property="og:image" content="{SITE}{image}" />\n' if image else ""
    lds = "".join(f'<script type="application/ld+json">\n{json.dumps(x, ensure_ascii=False, indent=2)}\n</script>\n' for x in ld)
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}" />
<meta name="robots" content="index, follow" />
<meta name="theme-color" content="#0b0d12" />
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
<link rel="canonical" href="{SITE}{path}" />
{alt}<meta property="og:type" content="{og_type}" />
<meta property="og:title" content="{html.escape(title)}" />
<meta property="og:description" content="{html.escape(desc)}" />
<meta property="og:url" content="{SITE}{path}" />
{img}<link rel="stylesheet" href="/style.css?v=0" />
<script defer src="https://cloud.umami.is/script.js" data-website-id="{UMAMI}" data-domains="pdfslimio.com"></script>
<meta name="google-adsense-account" content="{ADSENSE}" />
{lds}</head>
<body>
<div class="wrap">
      <nav>
           <a class="brand" href="{'/' if lang == 'en' else '/ko/'}"><span class="logo">📄</span> SlimIO</a>
           <div class="nav-links">
               <a href="{'/' if lang == 'en' else '/ko/'}">{t['compress']}</a>
               <a href="{'/#tools' if lang == 'en' else '/ko/#tools'}">{t['all_tools']}</a>
               <a href="{hub_path(lang)}">{t['guides']}</a>
               <a href="{hub_path('ko' if lang == 'en' else 'en')}" class="lang-switch"><img src="{t['other_flag']}" alt="" width="20" height="14" style="vertical-align:-2px;border-radius:2px;margin-right:6px" />{t['other_lang']}</a>
           </div>
      </nav>
</div>
"""


def foot(lang):
    t = T[lang]
    return f"""
<div class="wrap">
      <footer>
          <div class="foot">
              <div class="foot-links"><a href="{hub_path(lang)}">{t['guides']}</a> · {t['foot']}</div>
              <div>{t['foot2']}</div>
              <div>{t['foot3']}</div>
          </div>
      </footer>
</div>
</body>
</html>
"""


def article_page(a, siblings):
    lang, t = a["lang"], T[a["lang"]]
    path = art_path(lang, a["slug"])
    ld = [{
        "@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["desc"],
        "datePublished": a["published"], "dateModified": a["updated"], "inLanguage": lang,
        "author": {"@type": "Organization", "name": "SlimIO", "url": SITE + ("/about.html" if lang == "en" else "/ko/about.html")},
        "publisher": {"@type": "Organization", "name": "SlimIO", "url": SITE + "/"},
        "mainEntityOfPage": SITE + path, **({"image": SITE + a["image"]} if a.get("image") else {}),
    }, {
        "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "SlimIO", "item": SITE + ("/" if lang == "en" else "/ko/")},
            {"@type": "ListItem", "position": 2, "name": t["guides"], "item": SITE + hub_path(lang)},
            {"@type": "ListItem", "position": 3, "name": a["title"], "item": SITE + path}],
    }]
    if a.get("faq"):
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", ans)}} for q, ans in a["faq"]]})
    out = head(lang, a["seo_title"] + " | SlimIO", a["desc"], path, image=a.get("image"), ld=ld)
    out += f"""
<main class="content article">
      <p class="crumbs"><a href="{'/' if lang == 'en' else '/ko/'}">SlimIO</a> › <a href="{hub_path(lang)}">{t['guides']}</a></p>
      <h1>{a['title']}</h1>
      <p class="byline">{t['by']} · {t['updated']} <time datetime="{a['updated']}">{fmt_date(a['updated'], lang)}</time> · {a['minutes']} {t['read']}</p>
{a['body']}
"""
    if a.get("cta"):
        href, label, line = a["cta"]
        out += f"""      <div class="cta-box">
          <div><b>{t['try_it']}</b><p>{line}</p></div>
          <a class="cta-btn" href="{href}">{label} →</a>
      </div>
"""
    out += "</main>\n"
    if a.get("faq"):
        out += f'\n<section class="faq">\n      <h2>{t["faq"]}</h2>\n'
        out += "".join(f"      <details>\n          <summary>{q}</summary>\n          <p>{ans}</p>\n      </details>\n" for q, ans in a["faq"])
        out += "</section>\n"
    if siblings:
        out += f'\n<section class="content">\n      <h2>{t["more"]}</h2>\n      <div class="guide-list">\n'
        out += "".join(f'          <a class="guide-card" href="{art_path(s["lang"], s["slug"])}"><b>{s["title"]}</b><small>{s["desc"]}</small></a>\n' for s in siblings)
        out += "      </div>\n</section>\n"
    return out + foot(lang)


def hub_page(lang, arts):
    t = T[lang]
    alts = [("en", "/guides/"), ("ko", "/ko/guides/"), ("x-default", "/guides/")]
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": t["hub_h1"], "description": t["hub_desc"],
           "url": SITE + hub_path(lang), "inLanguage": lang,
           "hasPart": [{"@type": "Article", "headline": a["title"], "url": SITE + art_path(lang, a["slug"])} for a in arts]}]
    out = head(lang, t["hub_title"], t["hub_desc"], hub_path(lang), og_type="website", alternates=alts, ld=ld)
    out += f"""
<main class="content article">
      <h1>{t['hub_h1']}</h1>
      <p class="lead">{t['hub_lead']}</p>
      <div class="guide-list">
"""
    out += "".join(f'          <a class="guide-card" href="{art_path(lang, a["slug"])}"><b>{a["title"]}</b><small>{a["desc"]}</small>'
                   f'<span class="meta">{t["updated"]} {fmt_date(a["updated"], lang)} · {a["minutes"]} {t["read"]}</span></a>\n' for a in arts)
    out += "      </div>\n</main>\n"
    return out + foot(lang)


def footer_links():
    """Add the Guides link to every other page's footer (idempotent)."""
    n = 0
    for f in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
        if "/guides/" in f.replace(os.sep, "/"):
            continue
        s = open(f).read()
        ko = "/ko/" in f.replace(os.sep, "/")
        link = '<a href="/ko/guides/">가이드</a> · ' if ko else '<a href="/guides/">Guides</a> · '
        new = re.sub(r'(<div class="foot-links">)(?!<a href="/(?:ko/)?guides/">)', lambda m: m.group(1) + link, s)
        if new != s:
            open(f, "w").write(new)
            n += 1
    return n


def build():
    arts = load()
    for lang in ("en", "ko"):
        mine = sorted([a for a in arts if a["lang"] == lang], key=lambda a: a["published"], reverse=True)
        os.makedirs(os.path.join(ROOT, hub_path(lang).strip("/")), exist_ok=True)
        open(os.path.join(ROOT, hub_path(lang).strip("/"), "index.html"), "w").write(hub_page(lang, mine))
        for a in mine:
            open(os.path.join(ROOT, art_path(lang, a["slug"]).lstrip("/")), "w").write(article_page(a, [s for s in mine if s is not a][:4]))
            print(f"  {art_path(lang, a['slug'])}  {a['words']} words, {a['minutes']} min")
    print(f"guides: {len(arts)} articles · footer links added to {footer_links()} page(s)")


if __name__ == "__main__":
    build()
