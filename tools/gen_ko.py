#!/usr/bin/env python3
"""Build the Korean site (public/ko/) from the English pages, and link the two.

The English page is the source of truth for markup and behaviour (element ids,
scripts). This script swaps in Korean text: meta tags, structured data, hero,
tool labels, body copy and FAQ. It also adds hreflang links + a language switch
to both versions and rewrites sitemap.xml.

    python3 tools/gen_ko.py && python3 tools/bump_versions.py

Re-run it after changing an English page. If a UI string it expects is gone,
it stops and tells you which one, so the Korean page never silently drifts.
"""
import html, json, os, re, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_related   # cross-link blocks: written into the English pages first, translated with COMMON

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public")
SITE = "https://pdfslimio.com"
TODAY = datetime.date.today().isoformat()

SIZE_PAGES = ["compress-pdf-to-50kb.html", "compress-pdf-to-100kb.html", "compress-pdf-to-200kb.html",
              "compress-pdf-to-300kb.html", "compress-pdf-to-500kb.html", "compress-pdf-to-1mb.html",
              "compress-pdf-to-2mb.html", "compress-pdf-for-email.html"]
PAGES = ["index.html", "merge.html", "split.html", "delete-pages.html", "rotate.html", "organize.html",
         "add-page-numbers.html", "watermark.html", "pdf-to-jpg.html", "jpg-to-pdf.html",
         "sign-pdf.html", "compress-image.html", "compress-image-to-20kb.html", "compress-image-to-50kb.html",
         "compress-image-to-100kb.html", "compress-image-to-200kb.html", "compress-id-photo.html",
         "us-visa-photo.html", "signature-image.html"] + SIZE_PAGES


# English-only pages (no Korean version): listed in the sitemap, no hreflang.
EN_ONLY = ["bank-exam-photo-signature.html"]

# Hand-written in both languages (public/X.html and public/ko/X.html); gen_ko only links them.
INFO_PAGES = ["about.html", "terms.html", "privacy.html", "contact.html"]


def en_path(p): return "/" if p == "index.html" else "/" + p
def ko_path(p): return "/ko/" if p == "index.html" else "/ko/" + p


# --- text shared by many pages (applied wherever it appears) -----------------
COMMON = [
    (">Drop your PDF here<", ">PDF 파일을 여기에 끌어다 놓으세요<"),
    (">Drop PDF files here<", ">PDF 파일들을 여기에 끌어다 놓으세요<"),
    (">Drop image files here<", ">이미지 파일을 여기에 끌어다 놓으세요<"),
    (">or click to browse (select more than one)<", ">또는 클릭해서 여러 파일 선택<"),
    (">or click to browse (JPG, PNG, WebP…)<", ">또는 클릭해서 선택 (JPG, PNG, WebP 등)<"),
    (">or click to browse<", ">또는 클릭해서 파일 선택<"),
    ("<span>⚡ Instant</span>", "<span>⚡ 빠름</span>"),
    ("<span>🔒 Private</span>", "<span>🔒 안전</span>"),
    ("<span>🆓 Free</span>", "<span>🆓 무료</span>"),
    ("<span>📦 No install</span>", "<span>📦 설치 없음</span>"),
    ("<span>🎯 Hits your size</span>", "<span>🎯 원하는 용량</span>"),
    ('<a href="/">Compress</a>', '<a href="/">PDF 압축</a>'),
    ('<a href="/#tools">All tools</a>', '<a href="/#tools">전체 도구</a>'),
    ('<a href="/#how">How it works</a>', '<a href="/#how">사용 방법</a>'),
    ('<a href="/#pricing">Pricing</a>', '<a href="/#pricing">요금</a>'),
    ("SlimIO is free. A small <b>banner ad</b> may appear here to keep it free for everyone.",
     "SlimIO는 무료예요. 계속 무료로 운영할 수 있도록 이 자리에 작은 <b>배너 광고</b>가 표시될 수 있어요."),
    ("<div>© 2026 SlimIO · Free PDF tools</div>", "<div>© 2026 SlimIO · 무료 PDF 도구</div>"),
    ("<div>Runs in your browser · No signup</div>", "<div>브라우저에서 실행 · 회원가입 없음</div>"),
    ("<div>No signup · Files are never stored</div>", "<div>회원가입 없음 · 파일은 저장되지 않아요</div>"),
    ("<h3>Related tools</h3>", "<h3>다른 PDF 도구</h3>"),
    ("<h3>Compress to another size</h3>", "<h3>다른 용량으로 줄이기</h3>"),
    (">Compress PDF</a>", ">PDF 압축</a>"),
    (">Merge PDF</a>", ">PDF 합치기</a>"),
    (">Split PDF</a>", ">PDF 나누기</a>"),
    (">Remove Pages</a>", ">페이지 삭제</a>"),
    (">Rotate PDF</a>", ">PDF 회전</a>"),
    (">Organize PDF</a>", ">페이지 순서 변경</a>"),
    (">Page Numbers</a>", ">페이지 번호</a>"),
    (">Watermark PDF</a>", ">워터마크</a>"),
    (">PDF to JPG</a>", ">PDF → JPG</a>"),
    (">JPG to PDF</a>", ">JPG → PDF</a>"),
    (">Sign PDF</a>", ">PDF 서명</a>"),
    (">About</a>", ">서비스 소개</a>"),
    (">Terms</a>", ">이용약관</a>"),
    (">Privacy Policy</a>", ">개인정보처리방침</a>"),
    (">Contact</a>", ">문의하기</a>"),
    (">Compress Image</a>", ">사진 용량 줄이기</a>"),
    (">Compress image (any size)</a>", ">사진 용량 줄이기 (용량 자유)</a>"),
    (">Compress image to 20KB</a>", ">사진 20KB로 줄이기</a>"),
    (">Compress image to 50KB</a>", ">사진 50KB로 줄이기</a>"),
    (">Compress image to 100KB</a>", ">사진 100KB로 줄이기</a>"),
    (">Compress image to 200KB</a>", ">사진 200KB로 줄이기</a>"),
    (">ID / passport photo</a>", ">증명사진 용량 줄이기</a>"),
    (">US visa photo</a>", ">미국 비자 사진</a>"),
    (">Signature image</a>", ">서명 이미지 만들기</a>"),
    (">Signature Image</a>", ">서명 이미지</a>"),
    (">Compress to 100KB</a>", ">100KB로 줄이기</a>"),
    (">Compress to 200KB</a>", ">200KB로 줄이기</a>"),
    (">Compress to 500KB</a>", ">500KB로 줄이기</a>"),
    (">Compress to 1MB</a>", ">1MB로 줄이기</a>"),
    (">Compress to 50KB</a>", ">50KB로 줄이기</a>"),
    (">Compress to 300KB</a>", ">300KB로 줄이기</a>"),
    (">Compress to 2MB</a>", ">2MB로 줄이기</a>"),
    (">Compress for email</a>", ">메일 첨부용으로 줄이기</a>"),
    ("<span>Pages</span>", "<span>페이지</span>"),
    ("↓ Download PDF", "↓ PDF 다운로드"),
    ("↓ Download ZIP", "↓ ZIP 다운로드"),
    (">↓ Download<", ">↓ 다운로드<"),
    ('<label>Quality <span id="qval">', '<label>화질 <span id="qval">'),
    ('<label>Resolution <span id="sval">', '<label>해상도 <span id="sval">'),
]

SIZE_UI = [
    ("Nothing is kept — files are deleted right after compressing.", "파일은 저장되지 않아요. 압축 직후 삭제돼요."),
    ("<label>Target size</label>", "<label>목표 용량</label>"),
    ("SlimIO keeps the best quality that still fits under this size.", "이 용량 안에 들어가는 가장 좋은 화질로 만들어요."),
    (">Compress PDF</button>", ">PDF 압축하기</button>"),
    ("<span>Original</span>", "<span>원래 크기</span>"),
    ("<span>Compressed</span>", "<span>압축 후</span>"),
    ("<span>Target</span>", "<span>목표</span>"),
]

LOCAL_ONLY = "파일은 내 기기 밖으로 나가지 않아요. 브라우저 안에서 {}."

# --- per-page Korean text ------------------------------------------------------
KO = {}

KO["index.html"] = dict(
    title="PDF 용량 줄이기 - 무료 온라인 PDF 압축 | SlimIO",
    desc="PDF 용량을 무료로 줄이세요. 글자는 선명하게 유지하고, 회원가입·설치 없이 바로 압축해요. 100KB·1MB처럼 원하는 용량에 맞추는 것도 돼요.",
    keywords="PDF 용량 줄이기, PDF 압축, PDF 용량 축소, PDF 파일 크기 줄이기, PDF 압축 사이트, 무료 PDF 압축",
    short="PDF 용량 줄이기 | SlimIO",
    app_name="SlimIO PDF 압축",
    app_desc="회원가입 없이 쓰는 무료 온라인 PDF 압축 도구. 글자를 선명하게 유지하면서 PDF 용량을 줄여요.",
    features=["PDF 용량 줄이기", "Ghostscript 서버 압축 (글자 선명)", "브라우저 압축 (파일 업로드 없음)", "회원가입 없음"],
    h1="PDF 용량 줄이기,<br /><b>글자는 선명하게.</b>",
    lead="몇 초 만에 PDF 용량을 줄여요. 글자가 뭉개지지 않게, 무료로, 설치 없이.",
    ui=[
        ('<a href="#tools">Tools</a>', '<a href="#tools">도구</a>'),
        ('<a href="#how">How it works</a>', '<a href="#how">사용 방법</a>'),
        ('<a href="#pricing">Pricing</a>', '<a href="#pricing">요금</a>'),
        ('<a href="#security">Security</a>', '<a href="#security">보안</a>'),
        ('<a href="#tool">Try free</a>', '<a href="#tool">무료로 시작</a>'),
        (">Text stays sharp and selectable. Files are deleted right after compressing.<", ">글자가 선명하고 복사도 그대로 돼요. 파일은 압축 직후 삭제돼요.<"),
        ("<label>Compression</label>", "<label>압축 방식</label>"),
        (">Sharp (recommended) — text stays crisp and selectable<", ">선명하게 (추천) — 글자 선명, 복사 가능<"),
        (">Private — never leaves your device, shrinks the photos inside<", ">기기 안에서만 — 업로드 없음, PDF 속 사진만 줄여요<"),
        ("Best for most PDFs. Files up to 50MB; larger files are compressed in your browser.", "대부분의 PDF에 가장 좋아요. 50MB까지 가능하고, 더 큰 파일은 브라우저에서 압축해요."),
        ("<label>Level</label>", "<label>압축 정도</label>"),
        (">Smallest file — images at 72 dpi<", ">가장 작게 — 이미지 72dpi<"),
        (">Balanced (recommended) — images at 150 dpi<", ">균형 (추천) — 이미지 150dpi<"),
        (">High quality — images at 300 dpi<", ">고화질 — 이미지 300dpi<"),
        (">Smallest — images at 100 dpi<", ">가장 작게 — 이미지 100dpi<"),
        (">High quality — images at 200 dpi<", ">고화질 — 이미지 200dpi<"),
        (">Pages as images — smallest for text-heavy PDFs, text not selectable<", ">페이지를 이미지로 — 글자 많은 PDF를 가장 작게, 글자 선택 불가<"),
        ("Photos and scans inside the PDF are shrunk; text stays sharp and selectable.", "PDF 안의 사진·스캔만 줄여요. 글자는 선명하고 선택도 돼요."),
        (">Print shop — 300 dpi, keeps colour profiles<", ">인쇄소용 — 300dpi, 색 정보 유지<"),
        ("Only images are resampled; text and vector graphics stay sharp at every level.", "줄어드는 건 이미지뿐이에요. 글자와 도형은 어느 단계에서나 선명해요."),
        (">Compress PDF</button>", ">PDF 압축하기</button>"),
        ("<span>Original size</span>", "<span>원래 크기</span>"),
        ("<span>After compression</span>", "<span>압축 후</span>"),
        ("<span>Saved</span>", "<span>줄어든 비율</span>"),
        ("↓ Download compressed PDF", "↓ 압축된 PDF 다운로드"),
        ('<h2 class="sec">How it works</h2>', '<h2 class="sec">사용 방법</h2>'),
        ("Three steps. No account, no install.", "3단계면 끝나요. 가입도 설치도 필요 없어요."),
        (">STEP 1<", ">1단계<"), (">STEP 2<", ">2단계<"), (">STEP 3<", ">3단계<"),
        ("<h3>Drop your PDF</h3>", "<h3>PDF 올리기</h3>"),
        ("Drag a file in, or click to browse. You can pick how strong the compression should be.",
         "파일을 끌어다 놓거나 클릭해서 선택하세요. 압축 강도도 고를 수 있어요."),
        ("<h3>We shrink it</h3>", "<h3>용량 줄이기</h3>"),
        ("SlimIO re-encodes the document to remove dead weight — in your browser or on a fast server.",
         "필요 없는 무게를 덜어 내도록 문서를 다시 저장해요. 브라우저에서도, 빠른 서버에서도 할 수 있어요."),
        ("<h3>Download</h3>", "<h3>다운로드</h3>"),
        ("Get your smaller PDF instantly. See exactly how much you saved before you click.",
         "작아진 PDF를 바로 받으세요. 얼마나 줄었는지 먼저 확인할 수 있어요."),
        ('<h2 class="sec">Private by design</h2>', '<h2 class="sec">처음부터 안전하게</h2>'),
        ("Your files stay yours.", "파일은 온전히 내 것이에요."),
        ("<b>Browser mode</b>Files never leave your device", "<b>브라우저 모드</b>파일이 내 기기 밖으로 나가지 않아요"),
        ("<b>Auto-delete</b>Server files removed after each job", "<b>자동 삭제</b>서버 모드 파일은 처리 직후 삭제돼요"),
        ("<b>No signup</b>No account, ever", "<b>가입 없음</b>계정이 전혀 필요 없어요"),
        ('<h2 class="sec">All PDF tools</h2>', '<h2 class="sec">모든 PDF 도구</h2>'),
        ("Everything runs in your browser. Free, no signup.", "모두 브라우저에서 실행돼요. 무료, 가입 없음."),
        ("<h3>Merge PDF</h3><p>Combine multiple PDFs into one</p>", "<h3>PDF 합치기</h3><p>여러 PDF를 하나로</p>"),
        ("<h3>Split PDF</h3><p>Extract pages or split by range</p>", "<h3>PDF 나누기</h3><p>페이지별로 나누거나 범위 추출</p>"),
        ("<h3>PDF to JPG</h3><p>Convert pages to images</p>", "<h3>PDF → JPG</h3><p>페이지를 이미지로 변환</p>"),
        ("<h3>JPG to PDF</h3><p>Turn images into a PDF</p>", "<h3>JPG → PDF</h3><p>사진을 PDF로 묶기</p>"),
        ("<h3>Remove Pages</h3><p>Delete pages from a PDF</p>", "<h3>페이지 삭제</h3><p>필요 없는 페이지 빼기</p>"),
        ("<h3>Rotate PDF</h3><p>Turn pages 90/180/270°</p>", "<h3>PDF 회전</h3><p>90° · 180° · 270° 돌리기</p>"),
        ("<h3>Organize PDF</h3><p>Reorder, rotate or delete pages</p>", "<h3>페이지 순서 변경</h3><p>순서 바꾸기 · 회전 · 삭제</p>"),
        ("<h3>Page Numbers</h3><p>Number every page of a PDF</p>", "<h3>페이지 번호</h3><p>모든 페이지에 쪽번호</p>"),
        ("<h3>Watermark PDF</h3><p>Stamp text on every page</p>", "<h3>워터마크</h3><p>대외비 · 사본 문구 넣기</p>"),
        ("<h3>Sign PDF</h3><p>Draw, type or upload a signature</p>", "<h3>PDF 서명</h3><p>그리기 · 이름 · 도장으로 서명</p>"),
        ("<h3>Compress Image</h3><p>Shrink JPG and PNG photos to any size</p>", "<h3>사진 용량 줄이기</h3><p>JPG · PNG 사진을 원하는 KB로</p>"),
        ("<h3>ID Photo</h3><p>Crop to passport or ID size, under the KB limit</p>", "<h3>증명사진</h3><p>여권·반명함 규격으로 자르고 용량까지</p>"),
        ("<h3>US Visa Photo</h3><p>600×600 for the DS-160, under 240KB</p>", "<h3>미국 비자 사진</h3><p>DS-160용 600×600 · 240KB 이하</p>"),
        ("<h3>Signature Image</h3><p>Clean JPG or PNG signature, 10–20KB</p>", "<h3>서명 이미지</h3><p>깨끗한 서명 JPG · 투명 PNG, 10~20KB</p>"),
        ("Need an exact size?", "정해진 용량에 맞춰야 하나요?"),
        (">Compress PDF to 50KB</a>", ">PDF 50KB로 줄이기</a>"),
        (">for email</a>", ">메일 첨부용</a>"),
        ('<h2 class="sec">Simple, free pricing</h2>', '<h2 class="sec">간단한 요금제</h2>'),
        ("Start free. Upgrade only if you need more.", "무료로 시작하고, 더 필요할 때만 업그레이드하세요."),
        ('<span class="tag">Most popular</span>', '<span class="tag">가장 인기</span>'),
        ("<h3>Free</h3>", "<h3>무료</h3>"),
        ("<small> / forever</small>", "<small> / 평생</small>"),
        ("<li>20 compressions per day</li>", "<li>하루 20회 압축</li>"),
        ("<li>Both browser &amp; server mode</li>", "<li>브라우저 · 서버 모드 모두</li>"),
        ("<li>No account needed</li>", "<li>계정 필요 없음</li>"),
        (">Start free</button>", ">무료로 시작</button>"),
        ("<small> / month</small>", "<small> / 월</small>"),
        ("<li>Unlimited compressions</li>", "<li>무제한 압축</li>"),
        ("<li>Priority speed</li>", "<li>우선 처리</li>"),
        ("<li>No ads</li>", "<li>광고 없음</li>"),
        (">Coming soon</button>", ">준비 중</button>"),
        ("<div>© 2026 SlimIO · Shrink PDF fast</div>", "<div>© 2026 SlimIO · PDF 용량 줄이기</div>"),
        ("<div>Ghostscript-powered · Runs in your browser</div>", "<div>Ghostscript 기반 · 브라우저에서 실행</div>"),
    ],
    content="""
      <h2>PDF 용량 줄이는 방법</h2>
      <ul>
          <li><b>1. PDF 올리기.</b> 파일을 끌어다 놓거나 클릭해서 선택하세요.</li>
          <li><b>2. 압축 방식 고르기.</b> 파일을 밖으로 보내고 싶지 않다면 <b>브라우저 모드</b>, 글자를 최대한 선명하게 유지하고 싶다면 <b>서버 모드</b>를 고르세요.</li>
          <li><b>3. 다운로드.</b> 얼마나 줄었는지 확인하고 바로 받으세요.</li>
      </ul>
      <h3>PDF 용량이 큰 이유</h3>
      <p>PDF가 무거운 가장 큰 이유는 이미지예요. 스캔한 문서, 사진이 들어간 보고서, 고해상도 이미지가 그대로 들어간 발표 자료는 수십 MB가 되기 쉬워요. SlimIO는 글자와 도형은 그대로 두고, 이미지를 화면이나 인쇄에 충분한 해상도로 다시 저장해서 용량을 줄여요.</p>
      <h3>브라우저 모드와 서버 모드</h3>
      <p><b>브라우저 모드</b>는 파일이 내 기기 밖으로 나가지 않아요. 대신 페이지를 이미지로 다시 만들기 때문에 글자가 약간 부드러워질 수 있어요. <b>서버 모드</b>는 Ghostscript로 압축해서 글자가 선명하고 복사도 그대로 돼요. 서버로 보낸 파일은 결과를 돌려준 직후 삭제해요.</p>
      <h3>정해진 용량에 맞춰야 한다면</h3>
      <p>채용·공공기관 사이트처럼 “100KB 이하”, “1MB 이하” 제한이 있다면 <a href="/ko/compress-pdf-to-100kb.html">PDF 100KB로 줄이기</a>나 <a href="/ko/compress-pdf-to-1mb.html">1MB로 줄이기</a>를 쓰세요. 목표 용량 안에 들어가는 가장 좋은 화질을 자동으로 찾아 줘요. 메일로 보낼 PDF라면 <a href="/ko/compress-pdf-for-email.html">메일 첨부용으로 줄이기</a>가 편해요.</p>""",
    faq_title="PDF 용량 줄이기",
    faq=[
        ("PDF 용량 줄이기는 정말 무료인가요?", "네. 회원가입 없이 하루 20회까지 무료로 쓸 수 있어요. 결과 파일에 워터마크도 붙지 않아요."),
        ("파일이 서버에 남지 않나요?", "브라우저 모드는 파일이 아예 서버로 가지 않아요. 서버 모드는 압축을 위해 파일을 보내지만, 결과를 돌려준 직후 바로 삭제해요."),
        ("압축했는데 용량이 거의 안 줄었어요.", "글자 위주의 PDF는 이미 작아서 더 줄일 여지가 적어요. 스캔본이나 사진이 많은 PDF일수록 많이 줄어요. 서버 모드에서 ‘화면용’ 설정을 고르면 가장 작게 만들 수 있어요."),
        ("휴대폰에서도 되나요?", "네. 아이폰, 갤럭시 등 휴대폰 브라우저에서도 똑같이 쓸 수 있어요. 앱을 설치할 필요가 없어요."),
        ("압축하면 글자가 흐려지나요?", "서버 모드는 글자를 그대로 두기 때문에 선명하게 유지돼요. 브라우저 모드는 페이지를 이미지로 다시 만들어서 약간 부드러워질 수 있으니, 글자 선명도가 중요하면 서버 모드를 쓰세요."),
    ],
)

KO["merge.html"] = dict(
    title="PDF 합치기 - 여러 PDF 파일 하나로 무료 병합 | SlimIO",
    desc="여러 PDF 파일을 원하는 순서대로 하나로 합치세요. 회원가입 없이 무료이고, 파일은 브라우저 안에서만 처리돼 서버로 올라가지 않아요.",
    keywords="PDF 합치기, PDF 병합, PDF 파일 합치기, 여러 PDF 하나로, PDF 합치기 사이트, 무료 PDF 병합",
    short="PDF 합치기 | SlimIO",
    app_name="SlimIO PDF 합치기",
    app_desc="여러 PDF를 원하는 순서대로 하나로 합치는 무료 도구. 브라우저에서 처리돼 파일이 업로드되지 않아요.",
    features=["PDF 합치기", "합치는 순서 변경", "브라우저에서 처리 (업로드 없음)", "회원가입 없음"],
    h1="여러 PDF를<br /><b>하나로 합치기.</b>",
    lead="파일을 올리고 순서를 정한 뒤 합치기만 누르세요. 무료로, 설치 없이 브라우저에서 바로.",
    ui=[
        ('<a href="/merge.html">Merge</a>', '<a href="/merge.html">PDF 합치기</a>'),
        ("Files never leave your device — merging happens locally in your browser.", LOCAL_ONLY.format("합쳐요")),
        (">Merge PDFs</button>", ">PDF 합치기</button>"),
        ("<span>Files merged</span>", "<span>합친 파일</span>"),
        ("<span>Pages total</span>", "<span>전체 페이지</span>"),
        ("<span>Combined size</span>", "<span>합친 파일 크기</span>"),
        ("↓ Download merged PDF", "↓ 합친 PDF 다운로드"),
    ],
    content="""
      <h2>PDF 합치는 방법</h2>
      <ul>
          <li><b>1. PDF 올리기.</b> 합칠 파일을 한꺼번에 선택하거나 끌어다 놓으세요.</li>
          <li><b>2. 순서 정하기.</b> ▲ ▼ 버튼으로 순서를 바꾸고, ✕로 뺄 수 있어요.</li>
          <li><b>3. 합치기.</b> 하나로 합쳐진 PDF를 받으세요.</li>
      </ul>
      <h3>이럴 때 쓰세요</h3>
      <p>지원서와 증빙 서류를 한 파일로 제출해야 할 때, 여러 번 나눠 스캔한 문서를 하나로 묶을 때, 매달 받는 명세서나 영수증을 한 파일로 정리할 때 편해요.</p>
      <h3>합친 뒤 용량이 크다면</h3>
      <p>합친 파일이 업로드 제한보다 크다면 <a href="/ko/">PDF 용량 줄이기</a>로 줄이거나, <a href="/ko/compress-pdf-to-1mb.html">1MB로 줄이기</a>처럼 목표 용량에 맞춰 보세요. 페이지 단위로 순서를 바꾸려면 <a href="/ko/organize.html">페이지 순서 변경</a>을 쓰세요.</p>""",
    faq_title="PDF 합치기",
    faq=[
        ("PDF 합치기는 무료인가요?", "네, 회원가입 없이 무료예요. 하루 20회까지 쓸 수 있고, 결과 파일에 워터마크도 붙지 않아요."),
        ("몇 개까지 합칠 수 있나요?", "개수 제한은 없어요. 다만 브라우저에서 처리하기 때문에 아주 큰 파일을 많이 합치면 기기 사양에 따라 느려질 수 있어요."),
        ("파일이 서버로 올라가나요?", "아니요. 합치기는 브라우저 안에서만 처리돼서 파일이 서버로 가지 않아요."),
        ("합치는 순서를 바꿀 수 있나요?", "네. 목록의 ▲ ▼ 버튼으로 순서를 바꾼 뒤 합치면 돼요."),
        ("암호가 걸린 PDF도 합칠 수 있나요?", "열람 암호가 걸린 PDF는 열 수 없어서 합칠 수 없어요. 암호를 해제한 파일로 다시 시도해 주세요."),
    ],
)

KO["split.html"] = dict(
    title="PDF 나누기 - PDF 분할·페이지 추출 무료 | SlimIO",
    desc="PDF를 한 페이지씩 나누거나 원하는 페이지만 뽑아 새 PDF로 저장하세요. 회원가입 없이 무료이고, 파일은 브라우저 안에서만 처리돼요.",
    keywords="PDF 나누기, PDF 분할, PDF 페이지 추출, PDF 자르기, PDF 페이지 분리, PDF 쪼개기",
    short="PDF 나누기 | SlimIO",
    app_name="SlimIO PDF 나누기",
    app_desc="PDF를 페이지별로 나누거나 원하는 범위만 추출하는 무료 도구. 브라우저에서 처리돼 파일이 업로드되지 않아요.",
    features=["PDF 페이지별 분할", "페이지 범위 추출", "브라우저에서 처리 (업로드 없음)", "회원가입 없음"],
    h1="PDF 나누기,<br /><b>필요한 페이지만.</b>",
    lead="한 페이지씩 나누거나, 원하는 페이지만 골라 새 PDF로. 무료로, 설치 없이 브라우저에서 바로.",
    ui=[
        ('<a href="/split.html">Split</a>', '<a href="/split.html">PDF 나누기</a>'),
        ("File never leaves your device — splitting happens locally in your browser.", LOCAL_ONLY.format("나눠요")),
        ("<label>Split mode</label>", "<label>나누는 방식</label>"),
        (">Each page as its own PDF (ZIP)<", ">한 페이지씩 각각 PDF로 (ZIP)<"),
        (">Extract a page range (single PDF)<", ">원하는 페이지만 뽑아 PDF 하나로<"),
        ('<label>Pages <span class="hint" style="display:inline;">e.g. 1-3, 5, 8-10</span></label>',
         '<label>페이지 <span class="hint" style="display:inline;">예: 1-3, 5, 8-10</span></label>'),
        ("Comma-separated. Ranges use a dash (e.g. <code>1-3</code>).", "쉼표로 구분하고, 범위는 하이픈(-)으로 적어요. (예: <code>1-3</code>)"),
        ("<label>Total pages</label>", "<label>전체 페이지</label>"),
        (">Split PDF</button>", ">PDF 나누기</button>"),
    ],
    content="""
      <h2>PDF 나누는 방법</h2>
      <ul>
          <li><b>1. PDF 올리기.</b> 나눌 파일을 끌어다 놓거나 클릭해서 선택하세요.</li>
          <li><b>2. 방식 고르기.</b> 모든 페이지를 한 장씩 나누려면 “한 페이지씩”, 일부만 필요하면 “원하는 페이지만”을 고르고 <code>1-3, 5</code>처럼 적으세요.</li>
          <li><b>3. 다운로드.</b> 한 페이지씩 나눈 파일은 ZIP으로, 뽑은 페이지는 PDF 하나로 받아요.</li>
      </ul>
      <h3>이럴 때 쓰세요</h3>
      <p>두꺼운 서류에서 제출할 페이지만 떼어 낼 때, 여러 사람의 서류가 한 번에 스캔된 파일을 사람별로 나눌 때, 너무 커서 한 번에 올라가지 않는 PDF를 나눠 올릴 때 편해요.</p>
      <h3>페이지를 빼고 싶다면</h3>
      <p>필요한 페이지를 고르는 대신 필요 없는 페이지를 지우고 싶다면 <a href="/ko/delete-pages.html">페이지 삭제</a>를, 순서까지 바꾸려면 <a href="/ko/organize.html">페이지 순서 변경</a>을 쓰세요.</p>""",
    faq_title="PDF 나누기",
    faq=[
        ("PDF 나누기는 무료인가요?", "네, 회원가입 없이 무료예요. 하루 20회까지 쓸 수 있어요."),
        ("특정 페이지만 뽑을 수 있나요?", "네. “원하는 페이지만 뽑아 PDF 하나로”를 고르고 1-3, 5, 8-10처럼 적으면 그 페이지만 새 PDF로 저장돼요."),
        ("한 페이지씩 나누면 어떻게 받나요?", "페이지마다 PDF 파일이 하나씩 만들어지고, 모두 ZIP 파일 하나로 묶여서 받아요."),
        ("파일이 서버로 올라가나요?", "아니요. 나누기는 브라우저 안에서만 처리돼서 파일이 서버로 가지 않아요."),
        ("나눈 파일의 화질이 떨어지나요?", "아니요. 페이지를 그대로 옮기기만 해서 화질과 글자는 원본과 똑같아요."),
    ],
)

KO["delete-pages.html"] = dict(
    title="PDF 페이지 삭제 - 필요 없는 페이지 빼기 무료 | SlimIO",
    desc="PDF에서 필요 없는 페이지를 번호로 골라 삭제하세요. 회원가입 없이 무료이고, 파일은 브라우저 안에서만 처리돼 서버로 올라가지 않아요.",
    keywords="PDF 페이지 삭제, PDF 페이지 빼기, PDF 페이지 제거, PDF 특정 페이지 삭제, PDF 빈 페이지 삭제",
    short="PDF 페이지 삭제 | SlimIO",
    app_name="SlimIO PDF 페이지 삭제",
    app_desc="PDF에서 원하는 페이지를 번호로 골라 삭제하는 무료 도구. 브라우저에서 처리돼 파일이 업로드되지 않아요.",
    features=["PDF 페이지 삭제", "범위로 한 번에 삭제", "브라우저에서 처리 (업로드 없음)", "회원가입 없음"],
    h1="PDF 페이지 삭제,<br /><b>필요한 것만 남기기.</b>",
    lead="지울 페이지 번호만 적으면 끝. 무료로, 설치 없이 브라우저에서 바로.",
    ui=[
        ('<a href="/delete-pages.html">Remove Pages</a>', '<a href="/delete-pages.html">페이지 삭제</a>'),
        ("File never leaves your device — editing happens locally in your browser.", LOCAL_ONLY.format("편집해요")),
        ('<label>Pages to remove <span class="hint" style="display:inline;">e.g. 1, 3, 5-7</span></label>',
         '<label>삭제할 페이지 <span class="hint" style="display:inline;">예: 1, 3, 5-7</span></label>'),
        ("Comma-separated. Ranges use a dash (e.g. <code>5-7</code>).", "쉼표로 구분하고, 범위는 하이픈(-)으로 적어요. (예: <code>5-7</code>)"),
        (">Remove pages</button>", ">페이지 삭제하기</button>"),
        ("<span>Pages removed</span>", "<span>삭제한 페이지</span>"),
        ("<span>Pages left</span>", "<span>남은 페이지</span>"),
        ("<span>New size</span>", "<span>새 파일 크기</span>"),
    ],
    content="""
      <h2>PDF 페이지 삭제하는 방법</h2>
      <ul>
          <li><b>1. PDF 올리기.</b> 편집할 파일을 끌어다 놓거나 클릭해서 선택하세요.</li>
          <li><b>2. 페이지 번호 적기.</b> <code>1, 3, 5-7</code>처럼 쉼표와 하이픈으로 지울 페이지를 적으세요.</li>
          <li><b>3. 다운로드.</b> 선택한 페이지가 빠진 PDF를 받으세요.</li>
      </ul>
      <h3>이럴 때 쓰세요</h3>
      <p>스캔할 때 같이 들어간 빈 페이지를 뺄 때, 제출하면 안 되는 개인정보 페이지를 지울 때, 긴 보고서에서 부록만 덜어 낼 때 편해요. 페이지가 줄면 파일 용량도 함께 줄어요.</p>
      <h3>어떤 페이지인지 보면서 지우고 싶다면</h3>
      <p>페이지 번호가 헷갈린다면 미리보기를 보며 지울 수 있는 <a href="/ko/organize.html">페이지 순서 변경</a>을 쓰세요. 반대로 필요한 페이지만 뽑으려면 <a href="/ko/split.html">PDF 나누기</a>가 편해요.</p>""",
    faq_title="PDF 페이지 삭제",
    faq=[
        ("PDF 페이지 삭제는 무료인가요?", "네, 회원가입 없이 무료예요. 하루 20회까지 쓸 수 있어요."),
        ("여러 페이지를 한 번에 지울 수 있나요?", "네. 1, 3, 5-7처럼 쉼표로 구분하고 범위는 하이픈으로 적으면 한 번에 지워져요."),
        ("모든 페이지를 지울 수 있나요?", "아니요. 빈 파일이 되기 때문에 최소 한 페이지는 남아야 해요."),
        ("파일이 서버로 올라가나요?", "아니요. 브라우저 안에서만 처리돼서 파일이 서버로 가지 않아요."),
        ("남은 페이지의 화질이 떨어지나요?", "아니요. 남은 페이지는 원본 그대로예요. 지운 페이지만 빠져요."),
    ],
)

KO["rotate.html"] = dict(
    title="PDF 회전 - PDF 페이지 방향 돌리기 무료 | SlimIO",
    desc="옆으로 누운 PDF를 90°, 180°, 270° 돌려서 바로잡으세요. 회원가입 없이 무료이고, 파일은 브라우저 안에서만 처리돼 서버로 올라가지 않아요.",
    keywords="PDF 회전, PDF 돌리기, PDF 방향 바꾸기, PDF 페이지 회전, PDF 가로 세로 변경",
    short="PDF 회전 | SlimIO",
    app_name="SlimIO PDF 회전",
    app_desc="PDF의 모든 페이지를 90°, 180°, 270° 회전하는 무료 도구. 브라우저에서 처리돼 파일이 업로드되지 않아요.",
    features=["PDF 회전", "90° · 180° · 270°", "브라우저에서 처리 (업로드 없음)", "회원가입 없음"],
    h1="PDF 회전,<br /><b>바른 방향으로.</b>",
    lead="옆으로 누운 PDF를 한 번에 돌려요. 무료로, 설치 없이 브라우저에서 바로.",
    ui=[
        ('<a href="/rotate.html">Rotate</a>', '<a href="/rotate.html">PDF 회전</a>'),
        ("File never leaves your device — rotation happens locally in your browser.", LOCAL_ONLY.format("회전해요")),
        ("<label>Rotation</label>", "<label>회전 각도</label>"),
        (">No rotate<", ">회전 안 함<"),
        (">90° clockwise<", ">시계 방향 90°<"),
        (">270° (90° counter-clockwise)<", ">270° (반시계 방향 90°)<"),
        ("Every page is rotated by the same amount.", "모든 페이지가 같은 각도로 회전해요."),
        ("<label>Pages in this PDF</label>", "<label>이 PDF의 페이지 수</label>"),
        (">Rotate PDF</button>", ">PDF 회전하기</button>"),
        ("<span>Rotated</span>", "<span>회전</span>"),
    ],
    content="""
      <h2>PDF 회전하는 방법</h2>
      <ul>
          <li><b>1. PDF 올리기.</b> 돌릴 파일을 끌어다 놓거나 클릭해서 선택하세요.</li>
          <li><b>2. 각도 고르기.</b> 시계 방향 90°, 180°, 270° 중에서 고르세요. 모든 페이지가 같은 각도로 돌아가요.</li>
          <li><b>3. 다운로드.</b> 바로잡힌 PDF를 받으세요.</li>
      </ul>
      <h3>스캔한 PDF가 옆으로 누워 있다면</h3>
      <p>스캐너나 휴대폰 스캔 앱은 가로로 놓인 문서를 옆으로 누운 채 저장하는 경우가 많아요. 90°나 270°로 돌리면 대부분 바로잡혀요. 거꾸로 뒤집혀 있다면 180°를 고르세요.</p>
      <h3>한 페이지만 돌리고 싶다면</h3>
      <p>이 도구는 모든 페이지를 같이 돌려요. 특정 페이지만 돌리려면 미리보기에서 페이지별로 회전할 수 있는 <a href="/ko/organize.html">페이지 순서 변경</a>을 쓰세요. 돌린 뒤 용량을 줄이려면 <a href="/ko/">PDF 압축</a>을 쓰면 돼요.</p>""",
    faq_title="PDF 회전",
    faq=[
        ("PDF 회전은 무료인가요?", "네, 회원가입 없이 무료예요. 하루 20회까지 쓸 수 있어요."),
        ("한 페이지만 돌릴 수 있나요?", "이 도구는 모든 페이지를 같이 돌려요. 한 페이지만 돌리려면 페이지 순서 변경 도구에서 페이지마다 ↻ 버튼을 누르세요."),
        ("회전하면 화질이 떨어지나요?", "아니요. 페이지의 방향 정보만 바꾸기 때문에 화질과 글자는 원본과 똑같아요."),
        ("파일이 서버로 올라가나요?", "아니요. 브라우저 안에서만 처리돼서 파일이 서버로 가지 않아요."),
        ("PDF가 왜 옆으로 누워서 저장되나요?", "스캐너나 스캔 앱이 가로 방향 문서를 그대로 저장하면 옆으로 누워 보여요. 90°나 270°로 돌리면 대부분 해결돼요."),
    ],
)

KO["organize.html"] = dict(
    title="PDF 페이지 순서 바꾸기 - 정렬·회전·삭제 무료 | SlimIO",
    desc="PDF 페이지를 미리보기로 보면서 끌어다 순서를 바꾸고, 한 페이지씩 회전하거나 삭제하세요. 회원가입 없이 무료, 브라우저에서 처리돼요.",
    keywords="PDF 페이지 순서 바꾸기, PDF 순서 변경, PDF 페이지 이동, PDF 페이지 정렬, PDF 한 페이지만 회전",
    short="PDF 페이지 순서 바꾸기 | SlimIO",
    app_name="SlimIO PDF 페이지 순서 변경",
    app_desc="미리보기를 보며 PDF 페이지 순서를 바꾸고, 페이지별로 회전·삭제하는 무료 도구. 브라우저에서 처리돼 파일이 업로드되지 않아요.",
    features=["페이지 순서 변경", "페이지별 회전", "페이지 삭제", "미리보기", "브라우저에서 처리 (업로드 없음)"],
    h1="PDF 페이지 순서,<br /><b>보면서 바꾸기.</b>",
    lead="모든 페이지를 미리보기로 보면서 순서를 바꾸고, 한 장씩 회전하거나 지워요. 무료로, 설치 없이.",
    ui=[
        ('<a href="/organize.html">Organize</a>', '<a href="/organize.html">페이지 순서 변경</a>'),
        ("File never leaves your device — pages are rearranged locally in your browser.", LOCAL_ONLY.format("순서를 바꿔요")),
        ('<label>Pages <span id="pagecount"></span></label>', '<label>페이지 <span id="pagecount"></span></label>'),
        ("Drag to reorder, or use ← → · ↻ rotates one page · ✕ removes it.", "끌어다 놓거나 ← → 로 순서를 바꿔요 · ↻ 한 페이지만 회전 · ✕ 삭제"),
        (">Save PDF</button>", ">PDF 저장하기</button>"),
        ("<span>Size</span>", "<span>크기</span>"),
    ],
    content="""
      <h2>PDF 페이지 순서 바꾸는 방법</h2>
      <ul>
          <li><b>1. PDF 올리기.</b> 파일을 올리면 모든 페이지가 미리보기로 나와요.</li>
          <li><b>2. 정리하기.</b> 페이지를 끌어다 옮기거나 ← → 버튼을 누르세요. ↻로 그 페이지만 돌리고, ✕로 지울 수 있어요.</li>
          <li><b>3. 저장하기.</b> PDF 저장하기를 눌러 정리된 파일을 받으세요.</li>
      </ul>
      <h3>순서가 뒤섞인 스캔본 정리</h3>
      <p>양면 스캔이나 여러 번 나눠 스캔한 문서는 페이지 순서가 뒤섞이거나 일부만 거꾸로 저장되기 쉬워요. 미리보기로 확인하면서 바로잡을 수 있어요.</p>
      <h3>정리한 다음에는</h3>
      <p>정리가 끝났다면 <a href="/ko/add-page-numbers.html">페이지 번호</a>를 넣거나 <a href="/ko/">PDF 용량 줄이기</a>로 용량을 줄여 보세요. 여러 파일을 먼저 합쳐야 한다면 <a href="/ko/merge.html">PDF 합치기</a>를 쓰세요.</p>""",
    faq_title="PDF 페이지 순서 바꾸기",
    faq=[
        ("PDF 페이지 순서는 어떻게 바꾸나요?", "파일을 올리면 페이지가 미리보기로 나와요. 페이지를 끌어다 원하는 자리에 놓거나 ← → 버튼으로 옮긴 뒤 PDF 저장하기를 누르세요."),
        ("한 페이지만 회전할 수 있나요?", "네. 페이지 아래의 ↻ 버튼을 누르면 그 페이지만 시계 방향으로 90° 돌아가요."),
        ("페이지를 지울 수도 있나요?", "네. ✕ 버튼을 누르면 저장할 때 그 페이지가 빠져요."),
        ("휴대폰에서도 되나요?", "네. 휴대폰에서는 끌어다 놓기 대신 ← → 버튼으로 순서를 바꾸면 돼요."),
        ("파일이 서버로 올라가나요?", "아니요. 브라우저 안에서만 처리돼서 파일이 서버로 가지 않아요."),
    ],
)

KO["add-page-numbers.html"] = dict(
    title="PDF 페이지 번호 넣기 - 쪽번호 무료 추가 | SlimIO",
    desc="PDF에 페이지 번호를 넣으세요. 위치·형식·시작 번호를 고르고 표지는 건너뛸 수 있어요. 회원가입 없이 무료, 브라우저 안에서 처리돼요.",
    keywords="PDF 페이지 번호 넣기, PDF 쪽번호 넣기, PDF 페이지 번호 추가, PDF 번호 매기기, PDF 쪽번호",
    short="PDF 페이지 번호 넣기 | SlimIO",
    app_name="SlimIO PDF 페이지 번호",
    app_desc="PDF에 페이지 번호를 넣는 무료 도구. 위치·형식·시작 번호를 고르고 표지를 건너뛸 수 있어요. 브라우저에서 처리돼요.",
    features=["PDF 페이지 번호 넣기", "위치 · 형식 선택", "표지 건너뛰기", "브라우저에서 처리 (업로드 없음)"],
    h1="PDF 페이지 번호,<br /><b>한 번에 넣기.</b>",
    lead="위치와 형식만 고르면 모든 페이지에 번호가 들어가요. 무료로, 설치 없이 브라우저에서 바로.",
    ui=[
        ('<a href="/add-page-numbers.html">Page Numbers</a>', '<a href="/add-page-numbers.html">페이지 번호</a>'),
        ("File never leaves your device — numbering happens locally in your browser.", LOCAL_ONLY.format("번호를 넣어요")),
        ("<label>Position</label>", "<label>위치</label>"),
        (">Bottom center<", ">아래 가운데<"), (">Bottom right<", ">아래 오른쪽<"), (">Bottom left<", ">아래 왼쪽<"),
        (">Top center<", ">위 가운데<"), (">Top right<", ">위 오른쪽<"), (">Top left<", ">위 왼쪽<"),
        ("<label>Format</label>", "<label>형식</label>"),
        ("<label>Font size</label>", "<label>글자 크기</label>"),
        (">Small (9pt)<", ">작게 (9pt)<"), (">Medium (11pt)<", ">보통 (11pt)<"), (">Large (14pt)<", ">크게 (14pt)<"),
        ("<label>Skip first pages</label>", "<label>앞 페이지 건너뛰기</label>"),
        (">None — number every page<", ">건너뛰지 않음 — 모든 페이지에 번호<"),
        (">Skip 1 (cover page)<", ">1페이지 건너뛰기 (표지)<"),
        (">Skip 2<", ">2페이지 건너뛰기<"), (">Skip 3<", ">3페이지 건너뛰기<"),
        ("Skipped pages stay unnumbered.", "건너뛴 페이지에는 번호가 들어가지 않아요."),
        ("<label>Start at</label>", "<label>시작 번호</label>"),
        ("The number shown on the first numbered page.", "번호가 들어가는 첫 페이지에 표시될 숫자예요."),
        (">Add page numbers</button>", ">페이지 번호 넣기</button>"),
        ("<span>Numbered</span>", "<span>번호를 넣은 페이지</span>"),
    ],
    content="""
      <h2>PDF에 페이지 번호 넣는 방법</h2>
      <ul>
          <li><b>1. PDF 올리기.</b> 번호를 넣을 파일을 끌어다 놓거나 클릭해서 선택하세요.</li>
          <li><b>2. 모양 고르기.</b> 위치(위·아래, 왼쪽·가운데·오른쪽), 형식, 글자 크기를 고르세요.</li>
          <li><b>3. 다운로드.</b> 페이지 번호 넣기를 누르고 번호가 들어간 PDF를 받으세요.</li>
      </ul>
      <h3>표지는 번호 없이</h3>
      <p>보고서나 논문은 보통 표지에 번호를 넣지 않아요. <b>앞 페이지 건너뛰기</b>를 “1페이지”로 두면 둘째 페이지부터 번호가 들어가요. 시작 번호도 바꿀 수 있어요.</p>
      <h3>함께 쓰면 좋은 도구</h3>
      <p>번호를 넣기 전에 순서부터 정리하려면 <a href="/ko/organize.html">페이지 순서 변경</a>을, 여러 파일을 먼저 하나로 묶으려면 <a href="/ko/merge.html">PDF 합치기</a>를 쓰세요. 검토용 사본이라면 <a href="/ko/watermark.html">워터마크</a>도 함께 넣을 수 있어요.</p>""",
    faq_title="PDF 페이지 번호 넣기",
    faq=[
        ("PDF에 페이지 번호를 무료로 넣을 수 있나요?", "네. 회원가입 없이 하루 20회까지 무료로 쓸 수 있고, 결과 파일에 워터마크도 붙지 않아요."),
        ("표지에는 번호를 안 넣을 수 있나요?", "네. ‘앞 페이지 건너뛰기’에서 1페이지를 고르면 표지는 비우고 둘째 페이지부터 번호가 들어가요."),
        ("번호 형식은 어떤 게 있나요?", "1, Page 1, 1 / 10, Page 1 of 10 네 가지 중에서 고를 수 있어요."),
        ("가로 페이지나 회전된 페이지에도 제대로 들어가나요?", "네. 화면에 보이는 방향을 기준으로 위치를 잡기 때문에 가로 페이지에도 바른 방향으로 들어가요."),
        ("파일이 서버로 올라가나요?", "아니요. 브라우저 안에서만 처리돼서 파일이 서버로 가지 않아요."),
    ],
)

KO["watermark.html"] = dict(
    title="PDF 워터마크 넣기 - 대외비·사본 문구 무료 | SlimIO",
    desc="PDF 모든 페이지에 ‘대외비’, ‘사본’ 같은 워터마크를 넣으세요. 한글도 돼요. 회원가입 없이 무료이고, 파일은 브라우저 안에서만 처리돼요.",
    keywords="PDF 워터마크 넣기, PDF 워터마크, PDF 대외비 표시, PDF 사본 표시, PDF 문구 넣기, PDF 한글 워터마크",
    short="PDF 워터마크 넣기 | SlimIO",
    app_name="SlimIO PDF 워터마크",
    app_desc="PDF 모든 페이지에 문구 워터마크를 넣는 무료 도구. 한글 문구도 되고, 브라우저에서 처리돼 파일이 업로드되지 않아요.",
    features=["PDF 워터마크 넣기", "한글 문구 지원", "대각선 · 가운데 · 반복 배치", "브라우저에서 처리 (업로드 없음)"],
    h1="PDF 워터마크,<br /><b>한 번에 넣기.</b>",
    lead="‘대외비’, ‘사본’, 회사 이름까지. 모든 페이지에 한 번에 넣어요. 무료로, 설치 없이 브라우저에서 바로.",
    ui=[
        ('<a href="/watermark.html">Watermark</a>', '<a href="/watermark.html">워터마크</a>'),
        ("File never leaves your device — the watermark is added locally in your browser.", LOCAL_ONLY.format("워터마크를 넣어요")),
        ("<label>Watermark text</label>", "<label>워터마크 문구</label>"),
        ('value="CONFIDENTIAL"', 'value="대외비"'),
        ("Any language works — English, Korean, Japanese and more.", "한글, 영문, 일본어 등 어떤 언어든 돼요."),
        ("<label>Style</label>", "<label>배치</label>"),
        (">Diagonal, centered<", ">대각선 · 가운데<"), (">Horizontal, centered<", ">가로 · 가운데<"),
        (">Tiled across the page<", ">페이지 전체에 반복<"),
        ("<label>Color</label>", "<label>색상</label>"),
        (">Gray<", ">회색<"), (">Red<", ">빨간색<"), (">Blue<", ">파란색<"),
        ('<label>Opacity <span id="opv">', '<label>진하기 <span id="opv">'),
        (">Add watermark</button>", ">워터마크 넣기</button>"),
        ("<span>Watermark</span>", "<span>워터마크</span>"),
    ],
    content="""
      <h2>PDF에 워터마크 넣는 방법</h2>
      <ul>
          <li><b>1. PDF 올리기.</b> 워터마크를 넣을 파일을 끌어다 놓거나 클릭해서 선택하세요.</li>
          <li><b>2. 문구와 모양 정하기.</b> 문구를 적고 배치(대각선·가운데·반복), 색상, 진하기를 고르세요.</li>
          <li><b>3. 다운로드.</b> 모든 페이지에 워터마크가 들어간 PDF를 받으세요.</li>
      </ul>
      <h3>대외비 · 사본 · 초안 표시</h3>
      <p>외부로 나가면 안 되는 문서, 검토용 초안, 제출용 사본에 워터마크를 넣으면 용도를 분명히 보여 줄 수 있어요. 신분증이나 통장 사본에 “OO 제출용”처럼 적어 두면 다른 곳에 도용되는 걸 막는 데도 도움이 돼요.</p>
      <h3>한글 워터마크도 돼요</h3>
      <p>영문은 선명한 글자로, 한글이나 일본어처럼 다른 문자는 고해상도 이미지로 찍혀요. 기기에서 표시할 수 있는 글자라면 모두 쓸 수 있어요. 검토용 사본에는 <a href="/ko/add-page-numbers.html">페이지 번호</a>도 함께 넣어 보세요.</p>""",
    faq_title="PDF 워터마크 넣기",
    faq=[
        ("PDF 워터마크는 무료로 넣을 수 있나요?", "네. 회원가입 없이 하루 20회까지 무료로 쓸 수 있어요."),
        ("한글 워터마크도 되나요?", "네. ‘대외비’, ‘사본’처럼 한글 문구도 그대로 넣을 수 있어요. 영문은 선명한 글자로, 한글은 고해상도 이미지로 찍혀요."),
        ("워터마크가 내용을 가리지 않나요?", "반투명하게 들어가서 내용은 그대로 읽혀요. 더 옅게 하려면 진하기를 낮추세요."),
        ("신분증 사본에 ‘제출용’ 문구를 넣어도 되나요?", "네. ‘OO 제출용’처럼 적어 두면 다른 곳에 도용되는 걸 막는 데 도움이 돼요. 파일은 브라우저 안에서만 처리돼서 서버로 가지 않아요."),
        ("넣은 워터마크를 나중에 지울 수 있나요?", "워터마크는 페이지에 합쳐져서 저장되기 때문에 이 도구로 지울 수는 없어요. 원본 파일은 따로 보관해 두세요."),
    ],
)

KO["pdf-to-jpg.html"] = dict(
    title="PDF JPG 변환 - PDF를 이미지로 무료 변환 | SlimIO",
    desc="PDF 페이지를 JPG나 PNG 이미지로 바꾸세요. 화질과 해상도를 고르고 ZIP으로 한 번에 받아요. 회원가입 없이 무료, 브라우저 안에서 처리돼요.",
    keywords="PDF JPG 변환, PDF 이미지 변환, PDF를 JPG로, PDF PNG 변환, PDF 사진으로 저장",
    short="PDF JPG 변환 | SlimIO",
    app_name="SlimIO PDF JPG 변환",
    app_desc="PDF 페이지를 JPG나 PNG 이미지로 바꾸는 무료 도구. 브라우저에서 처리돼 파일이 업로드되지 않아요.",
    features=["PDF를 JPG로 변환", "PNG 무손실 저장", "화질 · 해상도 선택", "브라우저에서 처리 (업로드 없음)"],
    h1="PDF를 JPG로,<br /><b>선명하게.</b>",
    lead="모든 페이지를 이미지로 바꿔 ZIP으로 한 번에 받아요. 무료로, 설치 없이 브라우저에서 바로.",
    ui=[
        ('<a href="/merge.html">Merge</a>', '<a href="/merge.html">PDF 합치기</a>'),
        ('<a href="/pdf-to-jpg.html">PDF to JPG</a>', '<a href="/pdf-to-jpg.html">PDF → JPG</a>'),
        ("File never leaves your device — conversion happens locally in your browser.", LOCAL_ONLY.format("변환해요")),
        ("Higher = sharper images but larger files.", "높을수록 선명하지만 파일이 커져요."),
        ("<label>Output</label>", "<label>저장 형식</label>"),
        (">JPG (smaller)<", ">JPG (용량 작음)<"), (">PNG (lossless)<", ">PNG (무손실)<"),
        (">Convert to JPG</button>", ">JPG로 변환하기</button>"),
        ("<span>Output</span>", "<span>저장 형식</span>"),
    ],
    content="""
      <h2>PDF를 JPG로 바꾸는 방법</h2>
      <ul>
          <li><b>1. PDF 올리기.</b> 변환할 파일을 끌어다 놓거나 클릭해서 선택하세요.</li>
          <li><b>2. 화질 고르기.</b> 화질과 해상도, 저장 형식(JPG 또는 PNG)을 고르세요.</li>
          <li><b>3. 다운로드.</b> 페이지마다 이미지 한 장씩, ZIP 파일 하나로 받아요.</li>
      </ul>
      <h3>이럴 때 쓰세요</h3>
      <p>PDF를 올릴 수 없고 이미지만 받는 곳에 제출할 때, 블로그나 SNS에 문서 일부를 올릴 때, 발표 자료에 PDF 페이지를 그림으로 넣을 때 편해요.</p>
      <h3>JPG와 PNG 중 무엇을 고를까요?</h3>
      <p>사진이 많은 문서라면 용량이 작은 <b>JPG</b>, 글자나 도표가 많아 또렷해야 한다면 <b>PNG</b>가 좋아요. 반대로 이미지를 PDF로 묶으려면 <a href="/ko/jpg-to-pdf.html">JPG → PDF</a>를 쓰세요.</p>""",
    faq_title="PDF JPG 변환",
    faq=[
        ("PDF를 JPG로 무료 변환할 수 있나요?", "네. 회원가입 없이 하루 20회까지 무료로 쓸 수 있어요."),
        ("여러 페이지는 어떻게 받나요?", "페이지마다 이미지가 한 장씩 만들어지고, 모두 ZIP 파일 하나로 묶여서 받아요."),
        ("이미지 화질을 높일 수 있나요?", "네. 해상도를 높이면 더 선명해져요. 대신 파일이 커져요."),
        ("PNG로도 저장할 수 있나요?", "네. 저장 형식에서 PNG를 고르면 화질 손실 없이 저장돼요."),
        ("파일이 서버로 올라가나요?", "아니요. 브라우저 안에서만 처리돼서 파일이 서버로 가지 않아요."),
    ],
)

KO["jpg-to-pdf.html"] = dict(
    title="JPG PDF 변환 - 사진·이미지를 PDF로 무료 변환 | SlimIO",
    desc="JPG, PNG 사진 여러 장을 PDF 하나로 묶으세요. 순서도 바꿀 수 있어요. 회원가입 없이 무료이고, 파일은 브라우저 안에서만 처리돼요.",
    keywords="JPG PDF 변환, 이미지 PDF 변환, 사진 PDF 만들기, PNG PDF 변환, 사진 여러장 PDF로",
    short="JPG PDF 변환 | SlimIO",
    app_name="SlimIO JPG PDF 변환",
    app_desc="JPG, PNG 이미지를 PDF 하나로 묶는 무료 도구. 브라우저에서 처리돼 파일이 업로드되지 않아요.",
    features=["JPG를 PDF로 변환", "여러 장을 한 파일로", "순서 변경", "브라우저에서 처리 (업로드 없음)"],
    h1="사진을 PDF로,<br /><b>한 파일에 깔끔하게.</b>",
    lead="JPG, PNG 여러 장을 순서대로 PDF 하나로 묶어요. 무료로, 설치 없이 브라우저에서 바로.",
    ui=[
        ('<a href="/jpg-to-pdf.html">JPG to PDF</a>', '<a href="/jpg-to-pdf.html">JPG → PDF</a>'),
        ("Files never leave your device — conversion happens locally in your browser.", LOCAL_ONLY.format("변환해요")),
        (">Convert to PDF</button>", ">PDF로 변환하기</button>"),
        ("<span>Images</span>", "<span>이미지</span>"),
        ("<span>PDF size</span>", "<span>PDF 크기</span>"),
    ],
    content="""
      <h2>사진을 PDF로 바꾸는 방법</h2>
      <ul>
          <li><b>1. 이미지 올리기.</b> JPG, PNG 파일을 한꺼번에 선택하거나 끌어다 놓으세요.</li>
          <li><b>2. 순서 정하기.</b> ▲ ▼ 버튼으로 순서를 바꾸고, ✕로 뺄 수 있어요.</li>
          <li><b>3. 다운로드.</b> 한 장이 한 페이지인 PDF를 받으세요.</li>
      </ul>
      <h3>이럴 때 쓰세요</h3>
      <p>휴대폰으로 찍은 서류 사진을 PDF 하나로 제출할 때, 영수증이나 증빙 사진을 한 파일로 정리할 때, 여러 장의 스캔 이미지를 문서로 묶을 때 편해요.</p>
      <h3>만든 PDF가 너무 크다면</h3>
      <p>휴대폰 사진은 한 장에 수 MB라서 여러 장을 묶으면 금방 커져요. 업로드 제한이 있다면 <a href="/ko/">PDF 용량 줄이기</a>나 <a href="/ko/compress-pdf-to-1mb.html">1MB로 줄이기</a>로 줄여 보세요.</p>""",
    faq_title="JPG PDF 변환",
    faq=[
        ("사진을 PDF로 무료 변환할 수 있나요?", "네. 회원가입 없이 하루 20회까지 무료로 쓸 수 있어요."),
        ("여러 장을 PDF 하나로 만들 수 있나요?", "네. 여러 장을 한꺼번에 올리면 올린 순서대로 한 장이 한 페이지가 돼요. ▲ ▼ 버튼으로 순서를 바꿀 수 있어요."),
        ("어떤 이미지 형식을 지원하나요?", "JPG, PNG, WebP 등 브라우저에서 열리는 이미지는 대부분 돼요."),
        ("휴대폰 사진도 되나요?", "네. 아이폰, 갤럭시 브라우저에서 사진을 바로 골라 PDF로 만들 수 있어요."),
        ("파일이 서버로 올라가나요?", "아니요. 브라우저 안에서만 처리돼서 사진이 서버로 가지 않아요."),
    ],
)

KO["compress-image.html"] = dict(
    title="사진 용량 줄이기 - 이미지 용량·크기 줄이기 무료 | SlimIO",
    desc="사진·이미지 용량을 100KB, 200KB처럼 원하는 크기로 줄이세요. 증명사진 규격 맞추기와 위치정보 삭제까지. 회원가입 없이 무료, 브라우저에서 처리돼요.",
    keywords="사진 용량 줄이기, 이미지 용량 줄이기, 사진 크기 줄이기, 증명사진 용량 줄이기, 사진 100KB 줄이기, JPG 용량 줄이기, 이미지 압축",
    short="사진 용량 줄이기 | SlimIO",
    app_name="SlimIO 사진 용량 줄이기",
    app_desc="사진과 이미지 용량을 원하는 KB로 줄이는 무료 도구. 증명사진 규격 맞추기와 위치정보 삭제도 돼요. 브라우저에서 처리돼 사진이 업로드되지 않아요.",
    features=["사진 용량 줄이기 (JPG · PNG · WebP)", "원하는 KB로 맞추기", "증명사진 · 여권사진 규격", "위치정보(EXIF) 삭제", "브라우저에서 처리 (업로드 없음)"],
    h1="사진 용량 줄이기,<br /><b>화질은 그대로.</b>",
    lead="JPG·PNG 사진을 100KB, 200KB처럼 원하는 용량으로. 여러 장도 한 번에, 무료로, 설치 없이.",
    ui=[
        (">Drop images here<", ">사진을 여기에 끌어다 놓으세요<"),
        ("Images never leave your device. Location data (EXIF) is removed.", "사진은 내 기기 밖으로 나가지 않아요. 위치정보(EXIF)도 지워져요."),
        ("<label>Target size</label>", "<label>목표 용량</label>"),
        (">No limit — just optimize<", ">제한 없음 — 알맞게 최적화<"),
        ("Each image gets the best quality that still fits.", "사진마다 그 용량 안에서 가장 좋은 화질로 맞춰요."),
        ("<label>Resize</label>", "<label>크기 조절</label>"),
        (">Keep original dimensions<", ">원래 크기 유지<"),
        (">Longest side 1920px<", ">긴 변 1920px<"), (">Longest side 1280px<", ">긴 변 1280px<"), (">Longest side 800px<", ">긴 변 800px<"),
        (">ID photo 3×4 cm (354×472px)<", ">증명사진 3×4cm (354×472px)<"),
        (">Passport photo 3.5×4.5 cm (413×531px)<", ">여권사진 3.5×4.5cm (413×531px)<"),
        (">US visa 600×600 px (square)<", ">미국 비자 600×600px (정사각형)<"),
        (">Bank exam photo 200×230 px (IBPS / SBI)<", ">인도 은행 시험 사진 200×230px (IBPS / SBI)<"),
        (">Korea Q-Net exam photo 300×400 px<", ">큐넷 자격시험 300×400px<"),
        (">Korea civil service exam 137×177 px<", ">공무원 시험 원서 137×177px<"),
        (">Korean History Exam 120×160 px<", ">한국사능력검정 120×160px<"),
        ("📋 Paste your form's photo requirements <small>(optional)</small>", "📋 원서의 사진 규격 붙여넣기 <small>(선택)</small>"),
        ('placeholder="e.g. Photo 200 x 230 pixels, file size 20 KB to 50 KB, JPG"', 'placeholder="예: 사진 3x4cm, 200 x 230 픽셀, 20KB~50KB, JPG"'),
        ('<option value="custom">Custom range…</option>', '<option value="custom">직접 입력…</option>'),
        ('<label for="kmin">From</label>', '<label for="kmin">최소</label>'), ('<label for="kmax">to</label>', '<label for="kmax">최대</label>'),
        ('<option value="20-50KB">20–50KB</option>', '<option value="20-50KB">20~50KB</option>'),
        (">Custom size in pixels…<", ">픽셀 직접 입력…<"),
        ('<label for="cw">Width</label>', '<label for="cw">가로</label>'), ('<label for="ch">Height</label>', '<label for="ch">세로</label>'),
        ("ID, passport and custom sizes are cropped to the right shape — you can move the frame.", "증명·여권사진과 직접 입력한 크기는 비율에 맞게 잘라요. 자르는 위치는 옮길 수 있어요."),
        ('aria-label="Crop preview"', 'aria-label="자르기 미리보기"'),
        ('<label for="zoom">Zoom</label>', '<label for="zoom">확대</label>'),
        ('id="cropreset">Reset</button>', 'id="cropreset">처음으로</button>'),
        ("Drag the frame so your face sits inside the guide.</div>", "틀을 끌어서 얼굴이 점선 안에 들어오게 하세요.</div>"),
        ("<label>Format</label>", "<label>저장 형식</label>"),
        (">JPG — works everywhere<", ">JPG — 어디서나 호환<"),
        (">WebP — smaller, keeps transparency<", ">WebP — 더 작고 투명 배경 유지<"),
        (">PNG — lossless, larger<", ">PNG — 무손실, 용량 큼<"),
        (">Compress images</button>", ">사진 용량 줄이기</button>"),
        ("↓ Download all (ZIP)", "↓ 전체 다운로드 (ZIP)"),
    ],
    content="""
      <h2>사진 용량 줄이는 방법</h2>
      <ul>
          <li><b>1. 사진 올리기.</b> JPG, PNG, WebP 사진을 한 장이든 여러 장이든 끌어다 놓으세요.</li>
          <li><b>2. 용량 고르기.</b> “200KB 이하”처럼 목표 용량을 고르고, 필요하면 크기도 조절하세요. “제한 없음”으로 두면 알맞게 최적화만 해요.</li>
          <li><b>3. 다운로드.</b> 한 장씩 받거나, 전체를 ZIP 하나로 받으세요.</li>
      </ul>
      <h3>업로드 용량 제한에 걸렸다면</h3>
      <p>채용 사이트, 학교 시스템, 관공서 민원 신청에서는 사진을 100KB나 200KB 이하로 제한하는 경우가 많아요. 그 용량을 고르면 먼저 화질을 조절하고, 그래도 크면 크기를 조금씩 줄여서 제한 안에서 가장 선명한 사진을 만들어요.</p>
      <h3>증명사진 · 여권사진 규격</h3>
      <p>“증명사진 3×4cm”, “여권사진 3.5×4.5cm”를 고르면 규격 비율에 맞게 자르고, 온라인 접수에서 흔히 요구하는 픽셀 크기로 맞춰요. 사진 위에 나오는 틀을 얼굴로 옮기고 확대하면 원하는 부분만 남길 수 있어요. 자세한 방법은 <a href="/ko/compress-id-photo.html">증명사진 용량 줄이기</a>에서 볼 수 있어요.</p>
      <h3>위치정보도 함께 지워요</h3>
      <p>모든 처리는 브라우저 안에서 이루어져서 사진이 서버로 올라가지 않아요. 다시 저장하는 과정에서 사진에 숨어 있는 촬영 위치(GPS), 기종, 촬영 날짜 같은 정보(EXIF)도 지워져요. 사진을 문서로 묶어야 한다면 <a href="/ko/jpg-to-pdf.html">JPG → PDF</a>로 만든 뒤 <a href="/ko/">PDF 용량 줄이기</a>를 쓰세요.</p>""",
    faq_title="사진 용량 줄이기",
    faq=[
        ("사진 용량을 무료로 줄이려면 어떻게 하나요?", "이 페이지에 사진을 올리고 “200KB 이하”처럼 목표 용량을 고른 뒤 사진 용량 줄이기를 누르세요. 사진마다 그 용량 안에서 가장 좋은 화질로 만들어 주고, 한 장씩 또는 ZIP으로 받을 수 있어요."),
        ("사진이 서버로 올라가나요?", "아니요. 모든 처리가 브라우저 안에서 이루어져서 사진이 내 기기 밖으로 나가지 않아요."),
        ("사진의 위치정보도 지워지나요?", "네. 사진을 다시 저장하면서 촬영 위치(GPS), 기종, 촬영 날짜 같은 EXIF 정보가 지워져요."),
        ("증명사진 규격에 맞출 수 있나요?", "네. 증명사진 3×4cm나 여권사진 3.5×4.5cm를 고르면 비율에 맞게 자르고(틀을 끌어서 위치 조정 가능), 접수 사이트에서 흔히 요구하는 픽셀 크기로 맞춰요."),
        ("아이폰 사진이 안 열려요.", "아이폰 사진은 HEIC 형식인 경우가 많은데, 이 형식은 브라우저에 따라 열리지 않아요. 사진을 JPG로 공유하거나, 아이폰 설정 → 카메라 → 포맷에서 ‘높은 호환성’으로 바꾼 뒤 다시 시도해 주세요."),
    ],
)

KO["us-visa-photo.html"] = dict(
    title="미국 비자 사진 만들기 - DS-160 600×600·240KB 규격 무료 | SlimIO",
    desc="DS-160에 올릴 미국 비자 사진을 600×600 정사각형, 240KB 이하 JPG로 만드세요. 머리 크기·눈 높이 가이드까지. 무료, 브라우저에서 처리돼요.",
    keywords="미국 비자 사진, DS-160 사진, 미국 비자 사진 규격, 600x600 사진, 비자 사진 240KB, DS160 사진 업로드 오류, 미국 비자 사진 크기",
    short="미국 비자 사진 만들기 | SlimIO",
    app_name="SlimIO 미국 비자 사진",
    app_desc="DS-160용 미국 비자 사진을 600×600 정사각형, 240KB 이하 JPG로 만드는 무료 도구. 머리 크기와 눈 높이 가이드를 보여 줘요.",
    features=["600×600 정사각형 자르기", "240KB 이하 JPG", "머리 크기 · 눈 높이 가이드", "브라우저에서 처리 (업로드 없음)"],
    h1="미국 비자 사진,<br /><b>600×600 · 240KB 이하.</b>",
    lead="DS-160 규격대로 정사각형으로 자르고, 가이드에 머리를 맞추면 용량 검사를 통과하는 JPG가 나와요.",
    ui=None,
    content="""
      <h2>DS-160용 미국 비자 사진 만드는 방법</h2>
      <ul>
          <li><b>1. 사진 올리기.</b> 미국 비자 600×600과 240KB 제한이 이미 골라져 있어요.</li>
          <li><b>2. 위치 맞추기.</b> 초록색 틀을 끌어 머리가 점선 타원을 채우고, 눈이 두 점선 사이에 오게 하세요.</li>
          <li><b>3. 사진 용량 줄이기 → 다운로드.</b> 600×600px, 240KB 이하의 정사각형 JPG가 나와요. 바로 올릴 수 있어요.</li>
      </ul>
      <figure class="demo">
          <div class="demo-row">
              <div class="demo-src"><img src="/img/id-sample.webp" width="900" height="600" loading="lazy" alt="흰 벽 앞에서 찍은 평범한 휴대폰 사진" /><span>휴대폰 사진 · 1.8MB</span></div>
              <div class="demo-arrow" aria-hidden="true">→</div>
              <div class="demo-out"><div><img src="/img/us-visa-sample.webp" width="600" height="600" loading="lazy" alt="600×600 정사각형 비자 사진" /><span>600×600px · JPG</span></div></div>
          </div>
          <figcaption>가상 인물 예시 사진으로 이 페이지에서 만든 결과예요.</figcaption>
      </figure>
      <h3>공식 디지털 사진 규격</h3>
      <ul>
          <li><b>모양·크기:</b> 정사각형, 최소 600×600 ~ 최대 1200×1200 픽셀</li>
          <li><b>파일:</b> JPEG, 240KB 이하</li>
          <li><b>머리 크기:</b> 머리카락 끝부터 턱까지가 사진 높이의 50~69%</li>
          <li><b>배경:</b> 흰색 또는 미색의 단색</li>
          <li><b>최근·무보정:</b> 6개월 이내 촬영, 안경 불가, 얼굴을 바꾸는 디지털 보정 불가</li>
      </ul>
      <p>출처: 미국 국무부 <a href="https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/photos.html" rel="noopener">사진 규정(영문)</a>. 기준은 바뀔 수 있으니 신청 전에 공식 페이지를 확인하세요.</p>
      <h3>SlimIO가 하는 일과 하지 않는 일</h3>
      <p>자르기, 크기 맞추기, 용량 줄이기만 해요. 얼굴 보정이나 배경 바꾸기는 하지 않아요. 규정상 어차피 허용되지 않아요. 흰 벽 앞에서 정면을 보고, 그림자 없이 고르게 밝은 곳에서 찍으세요.</p>
      <h3>2×2인치로 인쇄해야 한다면</h3>
      <p>600×600 픽셀을 300dpi로 인쇄하면 정확히 2×2인치(51×51mm)예요. 미국 비자·여권 인화 사진 크기와 같아요.</p>""",
    faq_title="미국 비자 사진 만들기",
    faq=[
        ("DS-160에 올릴 사진 크기는 어떻게 맞추나요?", "이 페이지에 사진을 올리세요. 미국 비자 600×600과 240KB가 이미 골라져 있어요. 틀을 얼굴에 맞추고 사진 용량 줄이기를 누르면 240KB 이하의 정사각형 JPG가 나와요."),
        ("DS-160에서 사진이 통과되지 않아요.", "흔한 이유는 240KB 초과, 정사각형이 아니거나 600×600보다 작은 크기, 너무 작거나 큰 머리예요. 앞의 세 가지는 이 페이지가 맞춰 주고, 머리 크기는 가이드를 보고 맞추세요."),
        ("미국 비자 사진에 안경을 써도 되나요?", "안 돼요. 의사 소견서가 있는 드문 의료 사유를 빼고는 안경을 쓸 수 없어요."),
        ("배경을 흰색으로 바꿔 주나요?", "아니요. 배경이나 얼굴은 바꾸지 않아요. 디지털로 고친 사진은 받아 주지 않아요. 흰색이나 미색 벽 앞에서 찍어 주세요."),
        ("사진이 서버로 올라가나요?", "아니요. 모든 처리가 브라우저 안에서 이루어져서 사진이 내 기기 밖으로 나가지 않아요."),
    ],
)

KO["compress-id-photo.html"] = dict(
    title="증명사진 용량 줄이기 - 큐넷·공무원·한능검 원서 사진 규격 무료 | SlimIO",
    desc="증명사진을 3×4cm, 3.5×4.5cm나 큐넷(300×400px)·공무원(137×177px)·한국사능력검정(120×160px) 원서 규격으로 자르고 100KB, 200KB처럼 원하는 용량으로 한 번에 줄이세요. 무료, 브라우저에서 처리돼요.",
    keywords="증명사진 용량 줄이기, 증명사진 크기 줄이기, 원서 사진 규격, 큐넷 사진 규격, 공무원 원서 사진 규격, 한국사능력검정시험 사진 규격, 반명함 사진 크기, 이력서 사진 용량, 증명사진 100KB",
    short="증명사진 용량 줄이기 | SlimIO",
    app_name="SlimIO 증명사진 용량 줄이기",
    app_desc="증명사진과 여권사진을 규격에 맞게 자르고 원하는 KB 이하로 줄이는 무료 도구. 브라우저에서 처리돼 사진이 업로드되지 않아요.",
    features=["증명사진 3×4cm · 여권사진 3.5×4.5cm 규격", "원하는 KB 이하로 압축", "가운데 기준 자동 자르기", "위치정보(EXIF) 삭제", "브라우저에서 처리 (업로드 없음)"],
    h1="증명사진,<br /><b>규격도 용량도 한 번에.</b>",
    ui_extra=[
        ('aria-label="Photo size"', 'aria-label="사진 규격"'),
        ("<b>3×4 cm</b><span>ID photo</span>", "<b>3×4cm</b><span>반명함 · 이력서</span>"),
        ("<b>3.5×4.5 cm</b><span>Passport</span>", "<b>3.5×4.5cm</b><span>여권 · 신분증</span>"),
        ("<b>Custom</b><span>Any pixels</span></button>\n               </div>",
         "<b>직접 입력</b><span>원하는 픽셀</span></button>\n               </div>\n"
         '           <div class="exams" role="group" aria-label="시험 원서 사진 규격"><span>시험 원서</span>'
         '<button type="button" class="preset" data-resize="kr-qnet"><b>큐넷</b>300×400</button>'
         '<button type="button" class="preset" data-resize="kr-gosi"><b>공무원</b>137×177</button>'
         '<button type="button" class="preset" data-resize="kr-history"><b>한능검</b>120×160</button></div>'),
    ],
    lead="3×4cm·3.5×4.5cm, 큐넷·공무원·한능검 원서 규격으로 자르고 용량 제한까지 맞춰요. 설치 없이, 무료로.",
    ui=None,
    content="""
      <h2>증명사진 용량 줄이는 방법</h2>
      <ul>
          <li><b>1. 사진 올리기.</b> 증명사진 3×4cm 규격과 100KB가 이미 골라져 있어요.</li>
          <li><b>2. 접수 조건에 맞추기.</b> 여권·신분증용이면 크기 조절을 여권사진 3.5×4.5cm로, 용량은 공고문에 적힌 제한(예: 50KB, 200KB)으로 바꾸세요.</li>
          <li><b>3. 자르기 틀 맞추기.</b> 초록색 틀을 얼굴로 끌어 오고, 확대해서 머리가 점선 안에 들어오게 하세요.</li>
          <li><b>4. 사진 용량 줄이기 → 다운로드.</b> 자르기, 크기 맞추기, 용량 줄이기를 한 번에 해요.</li>
      </ul>
      <figure class="demo">
          <div class="demo-row">
              <div class="demo-src"><img src="/img/id-sample.webp" width="900" height="600" loading="lazy" alt="인물이 한쪽에 치우친 평범한 휴대폰 사진" /><span>휴대폰 사진 · 1.8MB</span></div>
              <div class="demo-arrow" aria-hidden="true">→</div>
              <div class="demo-out">
                  <div><img src="/img/id-sample-3x4.webp" width="354" height="472" loading="lazy" alt="3×4cm · 30KB" /><span>3×4cm · 30KB</span></div>
                  <div><img src="/img/id-sample-passport.webp" width="413" height="531" loading="lazy" alt="3.5×4.5cm · 38KB" /><span>3.5×4.5cm · 38KB</span></div>
              </div>
          </div>
          <figcaption>이 페이지로 만든 결과예요. 틀을 얼굴로 옮기고 살짝 확대한 뒤 100KB 이하로 저장했어요. (가상 인물 예시 사진)</figcaption>
      </figure>
      <h3>증명사진 규격 한눈에 보기</h3>
      <ul>
          <li><b>3×4cm (반명함)</b> → 354×472px. 이력서, 입사지원서, 자격시험 접수에 많이 써요.</li>
          <li><b>3.5×4.5cm (여권용)</b> → 413×531px. 여권, 주민등록증, 운전면허증에 쓰는 크기예요.</li>
      </ul>
      <p>두 규격 모두 300dpi라서 그 크기로 인쇄해도 선명해요. 접수 사이트마다 요구하는 크기와 용량이 다를 수 있으니 공고문의 안내를 꼭 확인하세요.</p>
      <h3>시험 원서별 사진 규격</h3>
      <p>위의 <b>시험 원서</b> 버튼을 누르면 픽셀 크기와 용량이 한 번에 맞춰져요. 링크로 바로 열 수도 있어요.</p>
      <ul>
          <li><b>큐넷 (국가기술자격·전문자격)</b> → 300×400px 이상, JPG, 200KB 이하. <a href="/ko/compress-id-photo.html?resize=kr-qnet">큐넷 규격으로 열기</a></li>
          <li><b>국가직 공무원 원서</b> → 3.5×4.5cm(137×177px), JPG. 용량은 공고마다 달라요(100KB 미만 등). <a href="/ko/compress-id-photo.html?resize=kr-gosi">공무원 규격으로 열기</a></li>
          <li><b>한국사능력검정시험</b> → 약 3×4cm(120×160px), JPG. <a href="/ko/compress-id-photo.html?resize=kr-history">한능검 규격으로 열기</a></li>
          <li><b>토익</b> → 픽셀 제한 없이 JPG 6MB 이하. 반명함 3×4cm로 저장하면 돼요.</li>
      </ul>
      <p>2026년 10월 각 접수 사이트 안내 기준이에요. 지방직·기업 채용처럼 규격이 다른 곳은 공고문의 문장을 위 <b>원서의 사진 규격 붙여넣기</b> 칸에 그대로 붙여 넣으면 숫자를 읽어서 맞춰 줘요.</p>
      <h3>“150×200 픽셀”처럼 픽셀로 정해져 있다면</h3>
      <p>cm 대신 픽셀로 규격을 적어 둔 접수 사이트도 많아요. 크기 조절에서 <b>픽셀 직접 입력</b>을 고르고 가로·세로를 입력하세요. 틀을 얼굴에 맞춰 옮기면 그 비율로 잘라서 정확히 그 픽셀 크기로, 용량 제한 안에 맞춰 저장해요.</p>
      <h3>잘 잘리게 찍는 팁</h3>
      <p>밝고 단색인 벽 앞에서 정면으로 찍으세요. 자르는 위치는 직접 정할 수 있으니 얼굴이 사진 한쪽에 있어도 괜찮아요. 머리(정수리~턱)가 사진 높이의 70% 정도를 차지하고 위에 약간 여백이 있으면 좋아요. 점선 타원이 대략 그 크기예요. 여권 사진은 흰색 배경이어야 하니 흰 벽 앞에서 찍는 게 안전해요.</p>
      <h3>안심하고 제출하세요</h3>
      <p>모든 처리는 브라우저 안에서 이루어져서 사진이 서버로 올라가지 않아요. 다시 저장하면서 촬영 위치(GPS)나 기종 같은 정보(EXIF)도 지워져요.</p>""",
    faq_title="증명사진 용량 줄이기",
    faq=[
        ("증명사진 용량을 줄이려면 어떻게 하나요?", "이 페이지에 사진을 올리고 사진 용량 줄이기를 누르세요. 증명사진 3×4cm 규격과 100KB가 기본으로 골라져 있고, 접수 사이트에 맞게 규격과 용량을 바꿀 수 있어요."),
        ("증명사진은 몇 KB로 줄여야 하나요?", "사이트마다 달라요. 50KB, 100KB, 200KB 이하가 흔하니 공고문을 확인하고 목표 용량에서 고르세요. 그 안에서 가장 좋은 화질로 맞춰 드려요."),
        ("반명함과 여권사진 크기는 어떻게 다른가요?", "반명함은 3×4cm(354×472px)이고, 여권·주민등록증·운전면허증용은 3.5×4.5cm(413×531px)예요."),
        ("사이트에서 150×200 픽셀로 올리라고 해요.", "크기 조절에서 픽셀 직접 입력을 고르고 가로 150, 세로 200을 입력한 뒤 목표 용량을 고르세요. 비율에 맞게 잘라서 정확히 150×200px로 저장해요."),
        ("큐넷 사진은 어떻게 맞추나요?", "시험 원서 줄의 큐넷 버튼을 누르세요. 300×400px, 200KB 이하로 맞춰져요. 틀을 얼굴에 맞추고 사진 용량 줄이기를 누르면 큐넷에 바로 올릴 수 있는 JPG가 나와요."),
        ("공무원 원서 사진 규격은요?", "국가직 원서는 3.5×4.5cm, 137×177px JPG예요. 공무원 버튼을 누르면 그 크기에 100KB 이하로 맞춰져요. 지방직 등 다른 시험은 공고문의 규격을 확인하세요."),
        ("얼굴이 사진 가운데에 있지 않아요.", "괜찮아요. 사진을 올린 뒤 초록색 틀을 얼굴로 끌어 오고, 확대로 머리가 점선 안에 들어오게 맞추세요. 다운로드하면 정확히 그 부분이 저장돼요."),
    ],
)

KO["signature-image.html"] = dict(
    title="서명 이미지 만들기 - 서명 용량 20KB 줄이기, 투명 PNG 무료 | SlimIO",
    desc="서명을 직접 그리거나 종이에 쓴 서명 사진을 올려서 배경을 지우고, 원서 규격(예: 10~20KB, 140×60px)에 맞는 JPG나 투명 PNG로 만드세요. 무료, 브라우저에서 처리돼요.",
    keywords="서명 이미지 만들기, 서명 용량 줄이기, 서명 20KB, 서명 투명 PNG, 서명 사진 배경 제거, 전자서명 이미지, 원서 서명 스캔",
    short="서명 이미지 만들기 | SlimIO",
    app_name="SlimIO 서명 이미지 만들기",
    app_desc="서명을 그리거나 사진으로 올려 배경을 지우고, 원하는 픽셀 크기와 용량(KB)의 JPG·투명 PNG로 만드는 무료 도구. 브라우저에서 처리돼요.",
    features=["직접 그려서 서명", "종이 서명 사진 배경 정리", "JPG · 투명 PNG", "정확한 픽셀 크기", "20KB 이하 · 10~20KB 맞추기", "브라우저에서 처리 (업로드 없음)"],
    h1="서명 이미지,<br /><b>규격에 딱 맞게.</b>",
    lead="직접 그리거나 종이에 쓴 서명을 찍어 올리세요. 원서가 요구하는 픽셀과 용량의 깨끗한 JPG·투명 PNG로 만들어요.",
    ui=[
        ('data-mode="draw">✍️ Draw<', 'data-mode="draw">✍️ 직접 그리기<'),
        ('data-mode="upload">📷 Paper signature photo<', 'data-mode="upload">📷 종이 서명 사진<'),
        ("Want to sign a PDF document instead? ", "PDF 문서에 바로 서명하려면 "),
        (">Sign PDF →</a>", ">PDF 서명 →</a>"),
        ("Upload forms usually accept only JPG. For putting on documents, a transparent PNG looks cleaner.", "원서 사이트는 대부분 JPG만 받아요. 문서에 넣을 서명은 투명한 PNG가 깔끔해요."),
        (">✍️ Use this signature to sign a PDF →<", ">✍️ 이 서명으로 PDF에 서명하기 →<"),
        ('aria-label="Signature pad"', 'aria-label="서명 입력판"'),
        ("📋 Paste your form's requirements <small>(optional)</small>", "📋 원서 안내문 붙여넣기 <small>(선택)</small>"),
        ('placeholder="e.g. Signature 140 x 60 pixels, file size between 10 KB and 20 KB, JPG format"', 'placeholder="예: 서명 140 x 60 픽셀, 파일 크기 10KB~20KB, JPG"'),
        (">Custom range…<", ">직접 입력…<"),
        ('<label for="kmin">From</label>', '<label for="kmin">최소</label>'), ('<label for="kmax">to</label>', '<label for="kmax">최대</label>'),
        ("✍️ Tap here to sign", "✍️ 여기를 눌러 서명하기"),
        ('title="Black ink"', 'title="검은색"'),
        ('title="Blue ink"', 'title="파란색"'),
        ('id="clear">Clear<', 'id="clear">지우기<'),
        ("Choose a photo or scan of your signature<small>Signed on plain white paper, in good light</small>", "서명 사진이나 스캔 고르기<small>흰 종이에 쓴 서명을 밝은 곳에서 찍어 주세요</small>"),
        ("Clean up background (paper becomes white)", "배경 정리 (종이를 흰색으로)"),
        ("<label>Size</label>", "<label>크기</label>"),
        (">Trim to the signature<", ">서명에 맞게 자르기<"),
        (">Exact size in pixels…<", ">픽셀 직접 입력…<"),
        ('<optgroup label="Bank exams (IBPS / SBI)">', '<optgroup label="인도 은행 시험 (IBPS / SBI)">'),
        (">Signature — 140×60 px, 10–20KB<", ">서명 — 140×60px, 10~20KB<"),
        (">Left thumb impression — 240×240 px, 20–50KB<", ">왼손 엄지 지문 — 240×240px, 20~50KB<"),
        (">Handwritten declaration — 800×400 px, 50–100KB<", ">손글씨 서약문 — 800×400px, 50~100KB<"),
        (">20–50KB<", ">20~50KB<"), (">50–100KB<", ">50~100KB<"),
        ('<label for="cw">Width</label>', '<label for="cw">가로</label>'), ('<label for="ch">Height</label>', '<label for="ch">세로</label>'),
        ("<label>File size</label>", "<label>파일 용량</label>"),
        ('<option value="">No limit</option>', '<option value="" selected>제한 없음</option>'),
        ('<option value="10-20" selected>10–20KB</option>', '<option value="10-20">10~20KB</option>'),
        (">Under 20KB<", ">20KB 이하<"), (">Under 50KB<", ">50KB 이하<"), (">Under 100KB<", ">100KB 이하<"),
        ("Check the form's instructions — many ask for a signature between 10KB and 20KB.", "원서 안내를 확인하세요. 서명은 10~20KB를 요구하는 경우가 많아요."),
        ("<label>Format</label>", "<label>저장 형식</label>"),
        ('<option value="jpeg" selected>JPG — white background</option>', '<option value="jpeg">JPG — 흰 배경</option>'),
        ('<option value="png">PNG — transparent background</option>', '<option value="png" selected>PNG — 투명 배경</option>'),
        (">Make signature image</button>", ">서명 이미지 만들기</button>"),
        ('alt="Your signature image"', 'alt="만든 서명 이미지"'),
        ("↓ Download signature", "↓ 서명 다운로드"),
    ],
    content="""
      <h2>서명 이미지 만드는 방법</h2>
      <ul>
          <li><b>1. 그리거나 올리기.</b> 손가락이나 마우스로 서명하거나, 흰 종이에 쓴 서명을 찍어 ‘종이 서명 사진’으로 올리세요.</li>
          <li><b>2. 크기 고르기.</b> 서명에 맞게 자르거나, 원서가 요구하는 픽셀(예: 140×60)을 직접 입력하세요.</li>
          <li><b>3. 용량과 형식 고르기.</b> 기본은 투명 PNG예요. 원서 사이트에 올릴 거라면 JPG와 요구 용량(예: 10~20KB)을 고르세요.</li>
          <li><b>4. 만들고 다운로드.</b> 미리보기 아래 나오는 크기와 용량을 확인한 뒤 제출하세요.</li>
      </ul>
      <div class="sig-demo">
          <div><img src="/img/sig-demo-photo.webp" width="600" height="400" loading="lazy" alt="종이에 쓴 서명을 찍은 사진" /><span>종이 서명을 폰으로 찍은 사진</span></div>
          <div class="arr" aria-hidden="true">→</div>
          <div><div class="out"><img src="/img/sig-demo-out.webp" width="600" height="182" loading="lazy" alt="배경을 지운 투명 서명 이미지" /></div><span>배경 정리 · 자르기 · 투명 PNG</span></div>
      </div>
      <h3>원서의 서명 규격</h3>
      <p>시험 접수, 채용, 관공서 온라인 신청에서는 서명을 JPG 10~20KB로, 때로는 “140×60 픽셀”이나 “3.5×1.5cm”처럼 크기까지 정해서 요구해요. 기준은 원서와 연도마다 바뀔 수 있으니 공고문의 숫자를 꼭 따르세요.</p>
      <h3>깨끗한 서명 사진 찍는 팁</h3>
      <ul>
          <li>줄이나 격자가 없는 흰 종이에 검은색이나 진한 파란색 펜으로 쓰세요.</li>
          <li>낮이나 밝은 조명 아래에서, 바로 위에서 폰 그림자가 지지 않게 찍으세요.</li>
          <li>서명이 사진의 대부분을 차지하게 찍으면 좋아요. 나머지는 자동으로 잘라요.</li>
      </ul>
      <h3>사진도 같이 내야 한다면</h3>
      <p>원서는 서명과 함께 증명사진도 요구하는 경우가 많아요. <a href="/ko/compress-id-photo.html">증명사진 용량 줄이기</a>로 3×4·3.5×4.5cm 규격과 용량을 맞추거나, <a href="/ko/sign-pdf.html">PDF 서명</a>으로 문서에 바로 서명을 넣을 수 있어요.</p>
      <h3>증명서·서류도 PDF로 올려야 한다면</h3>
      <p>원서 사이트는 졸업증명서, 자격증 사본 같은 서류에도 용량 제한을 두는 경우가 많아요. <a href="/ko/compress-pdf-to-100kb.html">PDF 100KB 이하로 줄이기</a>, <a href="/ko/compress-pdf-to-200kb.html">200KB</a>, <a href="/ko/compress-pdf-to-500kb.html">500KB</a>, <a href="/ko/compress-pdf-to-1mb.html">1MB</a>로 정확히 맞출 수 있고, 글자는 읽을 수 있게 유지돼요.</p>""",
    faq_title="서명 이미지 만들기",
    faq=[
        ("서명을 20KB 이하로 줄이려면 어떻게 하나요?", "서명을 그리거나 사진으로 올리고, 파일 용량에서 20KB 이하(또는 10~20KB)를 고른 뒤 서명 이미지 만들기를 누르세요. 빈 공간을 잘라 내고 그 용량 안에서 가장 선명하게 만들어요."),
        ("“10KB 이상 20KB 이하”처럼 최소 용량도 있어요.", "10~20KB를 고르세요. 20KB 안에서 가장 좋은 화질로 만들고, 그래도 10KB보다 작으면 파일에 무해한 여백 데이터를 더해서 최소 용량을 맞춰요. 이미지 자체는 바뀌지 않아요."),
        ("종이에 쓴 서명 사진을 깨끗하게 만들 수 있나요?", "네. 흰 종이에 진한 펜으로 서명하고 밝은 곳에서 찍어 올리세요. 배경 정리를 켜 두면 종이를 흰색(PNG는 투명)으로 바꾸고 서명 부분만 잘라 줘요."),
        ("투명 배경 서명을 만들 수 있나요?", "네. 저장 형식에서 PNG — 투명 배경을 고르세요. 문서에 얹기 좋아요. 다만 원서 사이트는 JPG만 받는 경우가 많고, JPG는 항상 흰 배경이에요."),
        ("서명이 서버로 올라가나요?", "아니요. 그리기, 배경 정리, 크기 조절이 모두 브라우저 안에서 이루어져서 서명이 내 기기 밖으로 나가지 않아요."),
    ],
)

KO["compress-image-to-50kb.html"] = dict(
    title="사진 50KB 줄이기 - 증명사진·이미지 용량 50KB 이하로 무료 | SlimIO",
    desc="증명사진·지원서 사진을 50KB 이하로 줄이세요. 시험 접수·채용·원서용으로 규격 맞추기까지. 회원가입 없이 무료, 브라우저에서 처리돼요.",
    keywords="사진 50KB 줄이기, 사진 용량 50KB, 증명사진 50KB, 이미지 50KB 이하, 사진 50KB 이하로, JPG 50KB 줄이기",
    short="사진 50KB 줄이기 | SlimIO",
    app_name="SlimIO 사진 50KB 줄이기",
    app_desc="사진과 이미지를 50KB 이하로 줄이는 무료 도구. 증명사진 규격에 맞추고 제한 안에서 가장 좋은 화질을 찾아요.",
    features=["사진 50KB 이하로 압축", "증명사진 · 여권사진 규격", "여러 장 한 번에", "위치정보(EXIF) 삭제", "브라우저에서 처리 (업로드 없음)"],
    h1="사진을<br /><b>50KB 이하로.</b>",
    lead="원서 사진이 “50KB 이하”여야 하나요? 사진을 넣으면 제한 안에서 가장 선명하게 맞춰 드려요.",
    ui=None,
    content="""
      <h2>사진을 50KB로 줄이는 방법</h2>
      <ul>
          <li><b>1. 사진 올리기.</b> 목표 용량은 이미 50KB로 맞춰져 있어요.</li>
          <li><b>2. 규격이 있다면 크기 고르기.</b> 크기 조절에서 증명사진·여권사진을 고르면 비율에 맞게 잘라 줘요.</li>
          <li><b>3. 사진 용량 줄이기 → 다운로드.</b> 50KB 안에서 가장 높은 화질을 찾아 저장해요.</li>
      </ul>
      <h3>50KB 제한은 어디서 만나나요?</h3>
      <p>시험 접수, 공공기관·기업 채용, 장학금·입학 원서처럼 온라인으로 제출하는 서류에서 증명사진을 20~50KB로 제한하는 경우가 있어요. 휴대폰 사진은 보통 2~5MB라서 50~100배 가까이 줄여야 해요.</p>
      <h3>잘라 낸 사진이 더 선명한 이유</h3>
      <p>같은 50KB라도 픽셀 수가 적으면 픽셀마다 더 많은 정보를 담을 수 있어요. 증명사진 크기(354×472px)는 50KB 안에 여유 있게 들어가 얼굴이 선명하게 남지만, 사진 전체를 그대로 넣으면 훨씬 작게 줄여야 해요. 얼굴과 어깨 위주로 자르거나 증명사진 규격을 먼저 고르세요.</p>
      <h3>제출 전에 확인하세요</h3>
      <ul>
          <li>형식: JPG로 두세요. 대부분의 접수 사이트가 JPG만 받아요.</li>
          <li>크기: 픽셀이나 cm 규격이 정해져 있다면 크기 조절에서 맞는 항목을 고르세요.</li>
          <li>용량: 결과 카드에 최종 용량이 나오니 제한과 비교해 보세요.</li>
      </ul>""",
    faq_title="사진 50KB 줄이기",
    faq=[
        ("원서 사진을 50KB로 줄이려면 어떻게 하나요?", "이 페이지에 사진을 올리고 사진 용량 줄이기를 누르세요. 목표는 이미 50KB예요. 증명사진·여권사진 규격도 요구한다면 크기 조절에서 먼저 골라 주세요."),
        ("50KB면 사진이 충분히 선명한가요?", "증명사진 크기라면 충분해요. 354×472px 사진은 50KB 안에서도 얼굴이 선명하게 남아요. 큰 사진은 들어갈 때까지 조금씩 줄이면서 가장 좋은 화질을 유지해요."),
        ("“20KB 이상 50KB 이하”처럼 최소 용량도 있어요.", "SlimIO는 50KB 안에서 가장 높은 화질을 찾기 때문에 대부분 20KB보다 넉넉히 커요. 결과 카드에 나온 용량을 확인해 주세요."),
        ("서명 이미지도 줄일 수 있나요?", "네. 서명 부분만 바짝 잘라서 올리면 돼요. 더 작은 용량을 요구한다면 20KB 페이지를 쓰세요."),
        ("사진이 서버로 올라가나요?", "아니요. 모든 처리가 브라우저 안에서 이루어져서 사진이 내 기기 밖으로 나가지 않아요."),
    ],
)

KO["compress-image-to-20kb.html"] = dict(
    title="사진 20KB 줄이기 - 서명·증명사진 용량 20KB 이하로 무료 | SlimIO",
    desc="서명 이미지와 사진을 20KB 이하로 줄이세요. 온라인 시험·채용 원서 제출용. 제한 안에서 가장 선명하게. 회원가입 없이 무료, 브라우저에서 처리돼요.",
    keywords="사진 20KB 줄이기, 서명 20KB, 사진 용량 20KB, 이미지 20KB 이하, 서명 이미지 용량 줄이기, JPG 20KB 줄이기",
    short="사진 20KB 줄이기 | SlimIO",
    app_name="SlimIO 사진 20KB 줄이기",
    app_desc="서명 이미지와 사진을 20KB 이하로 줄이는 무료 도구. 제한 안에서 가장 좋은 화질을 자동으로 찾아요.",
    features=["사진 · 서명 20KB 이하로 압축", "증명사진 규격 맞추기", "여러 장 한 번에", "위치정보(EXIF) 삭제", "브라우저에서 처리 (업로드 없음)"],
    h1="사진·서명을<br /><b>20KB 이하로.</b>",
    lead="사진이나 서명을 20KB 이하로 올려야 하나요? 알아볼 수 있게 선명함은 지키면서 줄여 드려요.",
    ui=None,
    content="""
      <h2>사진을 20KB로 줄이는 방법</h2>
      <ul>
          <li><b>1. 사진이나 서명 스캔 올리기.</b> 목표 용량은 이미 20KB로 맞춰져 있어요.</li>
          <li><b>2. 가능하면 먼저 자르기.</b> 사진이라면 크기 조절의 증명사진 규격이 알아서 잘라 줘요.</li>
          <li><b>3. 사진 용량 줄이기 → 다운로드.</b> 화질을 필요한 만큼만 낮추고, 그래도 크면 크기를 줄여요.</li>
      </ul>
      <h3>서명을 20KB 이하로</h3>
      <p>온라인 원서에서는 서명 스캔을 10~20KB로 요구하는 경우가 많아요. 흰 종이에 검정·진한 파랑 펜으로 서명하고, 밝은 곳에서 찍은 뒤 서명 주변만 바짝 잘라 주세요. 잘라 낸 서명은 20KB 안에 쉽게 들어가고 또렷하게 남아요.</p>
      <h3>사진을 20KB 이하로</h3>
      <p>20KB는 사진에게 아주 작은 용량이라 크기가 가장 중요해요. 증명사진 3×4cm(354×472px)를 고르면 얼굴을 충분히 알아볼 수 있어요. 휴대폰 사진 전체를 그대로 넣으면 몇백 픽셀까지 줄여야 해요.</p>
      <h3>그래도 흐릿하다면</h3>
      <ul>
          <li>제출 규정이 허용하는 만큼 배경을 더 잘라 내세요.</li>
          <li>저장 형식은 JPG로 두세요. PNG는 무손실이라 20KB 안에 잘 안 들어가요.</li>
          <li>사진은 <a href="/ko/compress-image-to-50kb.html">50KB</a>처럼 더 큰 용량이 허용되는지 확인해 보세요.</li>
      </ul>""",
    faq_title="사진 20KB 줄이기",
    faq=[
        ("서명 이미지를 20KB로 줄이려면요?", "서명 부분만 바짝 잘라서 이 페이지에 올리고 사진 용량 줄이기를 누르세요. 목표는 이미 20KB이고, 서명은 단순한 이미지라 이 용량에서도 또렷해요."),
        ("사진이 정말 20KB 안에 들어가나요?", "증명사진 크기라면 들어가요. 크기 조절에서 증명사진 3×4cm를 고르면 354×472px로 맞춘 뒤 20KB 이하로 저장해요."),
        ("왜 사진 크기(픽셀)가 작아지나요?", "화질을 낮추는 것만으로 20KB가 안 되면 들어갈 때까지 20%씩 줄여요. 먼저 잘라 두면 더 많은 디테일이 남아요."),
        ("JPG와 PNG 중 무엇이 좋나요?", "JPG를 고르세요. PNG는 모든 픽셀을 그대로 보존해서 용량이 훨씬 커서 20KB 안에 잘 안 들어가요."),
        ("파일이 서버로 올라가나요?", "아니요. 모든 처리가 브라우저 안에서 이루어져서 사진과 서명이 내 기기 밖으로 나가지 않아요."),
    ],
)

KO["compress-image-to-100kb.html"] = dict(
    title="사진 100KB 줄이기 - 이미지 용량 100KB 이하로 무료 | SlimIO",
    desc="증명사진·지원서 사진을 100KB 이하로 줄이세요. 제한 안에서 가장 선명하게 맞춰요. 증명사진 규격 맞추기까지. 회원가입 없이 무료, 브라우저에서 처리돼요.",
    keywords="사진 100KB 줄이기, 사진 용량 100KB, 증명사진 100KB, 이미지 100KB 이하, 사진 100KB 이하로, JPG 100KB 줄이기",
    short="사진 100KB 줄이기 | SlimIO",
    app_name="SlimIO 사진 100KB 줄이기",
    app_desc="사진과 이미지를 100KB 이하로 줄이는 무료 도구. 제한 안에서 가장 좋은 화질을 자동으로 찾아요.",
    features=["사진 100KB 이하로 압축", "증명사진 규격 맞추기", "여러 장 한 번에", "위치정보(EXIF) 삭제", "브라우저에서 처리 (업로드 없음)"],
    h1="사진을<br /><b>100KB 이하로.</b>",
    lead="“100KB 이하 사진만 첨부 가능”에 막혔나요? 사진을 넣으면 제한 안에서 가장 선명하게 맞춰 드려요.",
    ui=None,
    content="""
      <h2>사진을 100KB로 줄이는 방법</h2>
      <ul>
          <li><b>1. 사진 올리기.</b> 목표 용량은 이미 100KB로 맞춰져 있어요. 여러 장을 한 번에 올려도 돼요.</li>
          <li><b>2. 사진 용량 줄이기.</b> 먼저 화질을 필요한 만큼만 낮추고, 그래도 크면 크기를 조금씩 줄여서 100KB 안에 맞춰요.</li>
          <li><b>3. 다운로드.</b> 한 장씩 받거나, 전체를 ZIP으로 받으세요.</li>
      </ul>
      <h3>100KB 제한은 어디서 만나나요?</h3>
      <p>공공기관·기업 채용 사이트, 자격시험 접수, 학교 시스템, 각종 민원 신청에서 사진(특히 증명사진)을 100KB 이하로 제한하는 경우가 많아요. 휴대폰 사진은 보통 2~5MB라서 95% 이상 줄여야 해요.</p>
      <h3>증명사진은 용량과 규격을 함께</h3>
      <p>접수 사이트는 용량뿐 아니라 “3×4cm”처럼 크기도 요구하는 경우가 많아요. 크기 조절에서 <b>증명사진 3×4cm</b>를 고르고 틀을 얼굴에 맞추면 비율에 맞게 잘라 354×472px로 맞춘 뒤 100KB 안에 넣어요. 이 크기면 대부분 아주 선명하게 들어가요.</p>
      <h3>더 선명하게 만드는 팁</h3>
      <ul>
          <li>필요 없는 배경을 먼저 잘라 내면 같은 용량에서 더 선명해져요.</li>
          <li>저장 형식은 JPG로 두세요. 거의 모든 접수 사이트가 받아 줘요.</li>
          <li>위치정보(EXIF)는 자동으로 지워져서 그대로 제출해도 안전해요.</li>
      </ul>""",
    faq_title="사진 100KB 줄이기",
    faq=[
        ("사진을 100KB로 무료로 줄이려면요?", "이 페이지에 사진을 올리고 사진 용량 줄이기를 누르세요. 목표는 이미 100KB로 맞춰져 있고, 회원가입 없이 바로 받을 수 있어요."),
        ("100KB로 줄이면 사진이 흐려지나요?", "증명사진 크기라면 거의 티가 나지 않아요. 큰 휴대폰 사진은 화질부터 조절하고 필요할 때만 크기를 줄여서, 100KB 안에서 가장 선명하게 만들어요."),
        ("증명사진 규격과 100KB를 한 번에 맞출 수 있나요?", "네. 크기 조절에서 증명사진 3×4cm를 고르면 354×472px로 맞춘 뒤 100KB 이하로 저장해요."),
        ("여러 장을 한꺼번에 100KB로 줄일 수 있나요?", "네. 여러 장을 올리면 각각 100KB 이하로 줄이고, ZIP 하나로 받을 수 있어요."),
        ("사진이 서버로 올라가나요?", "아니요. 모든 처리가 브라우저 안에서 이루어져서 사진이 내 기기 밖으로 나가지 않아요."),
    ],
)

KO["compress-image-to-200kb.html"] = dict(
    title="사진 200KB 줄이기 - 이미지 용량 200KB 이하로 무료 | SlimIO",
    desc="사진·이미지를 200KB 이하로 줄이세요. 입학·장학금 서류, 온라인 신청, 메일 첨부용으로. 제한 안에서 가장 선명하게. 회원가입 없이 무료.",
    keywords="사진 200KB 줄이기, 사진 용량 200KB, 이미지 200KB 이하, 사진 200KB 이하로, JPG 200KB 줄이기",
    short="사진 200KB 줄이기 | SlimIO",
    app_name="SlimIO 사진 200KB 줄이기",
    app_desc="사진과 이미지를 200KB 이하로 줄이는 무료 도구. 제한 안에서 가장 좋은 화질을 자동으로 찾아요.",
    features=["사진 200KB 이하로 압축", "여러 장 한 번에", "위치정보(EXIF) 삭제", "브라우저에서 처리 (업로드 없음)"],
    h1="사진을<br /><b>200KB 이하로.</b>",
    lead="사진마다 “200KB 이하” 제한이 있나요? 제한 안에서 가장 선명하게 맞춰 드려요.",
    ui=None,
    content="""
      <h2>사진을 200KB로 줄이는 방법</h2>
      <ul>
          <li><b>1. 사진 올리기.</b> 목표 용량은 이미 200KB로 맞춰져 있어요.</li>
          <li><b>2. 사진 용량 줄이기.</b> 화질을 필요한 만큼만 낮추고, 그래도 크면 크기를 조금씩 줄여요.</li>
          <li><b>3. 다운로드.</b> 한 장씩 받거나, 전체를 ZIP으로 받으세요.</li>
      </ul>
      <h3>200KB 제한을 자주 만나는 곳</h3>
      <p>대학 입학·장학금 신청, 비자·회원 가입 서류, 중고거래·쇼핑몰 상품 사진은 한 장당 200KB 안팎으로 제한하는 경우가 많아요. 메일에 첨부하거나 문서에 넣기에도 알맞은 크기예요.</p>
      <h3>200KB면 어느 정도 화질일까요?</h3>
      <p>대부분의 사진은 긴 변 1600px 정도를 유지한 채 200KB 안에 들어가요. 화면으로 보거나 작게 인쇄하기에 충분하고, 상품 사진·인물 사진·스캔한 증명서 모두 잘 맞아요.</p>
      <h3>사진을 문서로 묶어야 한다면</h3>
      <p>여기서 먼저 줄인 다음 <a href="/ko/jpg-to-pdf.html">JPG → PDF</a>로 묶으면 처음부터 가벼운 PDF가 만들어져요.</p>""",
    faq_title="사진 200KB 줄이기",
    faq=[
        ("사진을 200KB로 줄이려면 어떻게 하나요?", "이 페이지에 사진을 올리고 사진 용량 줄이기를 누르세요. 목표는 이미 200KB이고, 그 안에서 가장 좋은 화질로 만들어 드려요."),
        ("줄인 사진은 몇 픽셀 정도가 되나요?", "사진마다 다르지만, 200KB면 대부분 긴 변 1600px 안팎을 유지해요."),
        ("색이 바뀌지는 않나요?", "아니요. 색은 그대로이고, 용량을 줄이려고 아주 세밀한 부분만 조금 줄어들어요."),
        ("투명 배경을 유지할 수 있나요?", "저장 형식에서 WebP를 고르세요. JPG는 투명 배경을 지원하지 않아서 흰색으로 바뀌어요."),
        ("사진이 서버로 올라가나요?", "아니요. 모든 처리가 브라우저 안에서 이루어져서 사진이 내 기기 밖으로 나가지 않아요."),
    ],
)

KO["sign-pdf.html"] = dict(
    title="PDF 도장 넣기·서명 넣기 - 직인·이름 도장 무료 | SlimIO",
    desc="PDF에 도장·직인이나 서명을 무료로 넣으세요. 이름으로 빨간 도장을 만들거나, 도장을 찍은 사진을 올리면 배경을 지우고 원하는 자리에 넣어요. 회원가입 없이 브라우저에서 처리돼요.",
    keywords="PDF 도장 넣기, PDF 직인 넣기, PDF 서명 넣기, 이름 도장 만들기, PDF 도장 무료, PDF 전자서명, PDF 사인, 전자 도장 만들기",
    short="PDF 도장·서명 넣기 | SlimIO",
    app_name="SlimIO PDF 서명",
    app_desc="PDF에 서명과 도장을 넣는 무료 도구. 직접 그리거나 이름으로 만들거나 이미지를 올려 원하는 위치에 넣어요. 브라우저에서 처리돼 파일이 업로드되지 않아요.",
    features=["직접 그려서 서명", "이름으로 손글씨 서명 · 도장 만들기", "서명 · 도장 이미지 올리기 (흰 배경 자동 제거)", "원하는 페이지 · 위치에 배치", "브라우저에서 처리 (업로드 없음)"],
    h1="PDF 서명,<br /><b>도장까지 한 번에.</b>",
    lead="서명을 그리거나, 이름으로 만들거나, 도장 이미지를 올려서 원하는 곳에. 무료로, 설치 없이 브라우저에서 바로.",
    ui=[
        ("File never leaves your device — signing happens locally in your browser.", LOCAL_ONLY.format("서명을 넣어요")),
        ("<label>1. Create your signature</label>", "<label>1. 서명 만들기</label>"),
        ('data-mode="draw">Draw<', 'data-mode="draw">직접 그리기<'),
        ('data-mode="type">Type<', 'data-mode="type">이름 입력<'),
        ('data-mode="upload">Upload<', 'data-mode="upload">이미지 올리기<'),
        ('title="Black ink"', 'title="검은색"'),
        ('title="Blue ink"', 'title="파란색"'),
        ('id="clear">Clear<', 'id="clear">지우기<'),
        ("✍️ Tap here to sign", "✍️ 여기를 눌러 서명하기"),
        ('placeholder="Type your name"', 'placeholder="이름을 입력하세요"'),
        ('id="pickimg">Choose a signature or stamp image<', 'id="pickimg">서명 · 도장 이미지 고르기<'),
        ("Remove white background", "흰 배경 자동 제거"),
        ('id="add">+ Add signature to this page<', 'id="add">+ 이 페이지에 서명 넣기<'),
        ("✓ Your signature is ready. Choose the PDF you want to sign.", "✓ 서명이 준비됐어요. 서명할 PDF를 골라 주세요."),
        ("<label>2. Place it <span", "<label>2. 위치 정하기 <span"),
        ("← Previous page", "← 이전 페이지"),
        ("Next page →", "다음 페이지 →"),
        ("Drag to move · drag the green corner to resize · ✕ removes it.", "끌어서 옮기기 · 초록색 모서리로 크기 조절 · ✕로 삭제"),
        (">Sign &amp; download</button>", ">서명하고 다운로드</button>"),
        ("<span>Signatures</span>", "<span>서명</span>"),
    ],
    content="""
      <h2>PDF에 서명 넣는 방법</h2>
      <ul>
          <li><b>1. PDF 올리기.</b> 파일을 끌어다 놓거나 클릭해서 선택하면 첫 페이지가 미리보기로 나와요.</li>
          <li><b>2. 서명 만들기.</b> 마우스나 손가락으로 직접 그리거나, 이름을 입력해 손글씨 서명·도장을 고르거나, 서명·도장 사진을 올리세요.</li>
          <li><b>3. 배치하고 다운로드.</b> 이 페이지에 서명 넣기를 누르고 원하는 자리로 끌어 옮긴 뒤, 모서리로 크기를 맞추고 서명하고 다운로드를 누르세요.</li>
      </ul>
      <h3>PDF에 도장 넣기 (이름 도장)</h3>
      <p>도장이 없어도 괜찮아요. 이름 입력 탭에서 이름을 적고 빨간 원형 스타일을 고르면 도장이 만들어져요. 두 글자는 세로로, 세 글자 이름은 세로 한 줄로, 네 글자는 오른쪽 위부터 읽는 방식으로 배치해요.</p>
      <h3>PDF에 직인·실제 도장 넣기</h3>
      <p>흰 종이에 도장이나 회사 직인을 찍은 뒤 사진을 찍어 이미지 올리기로 넣으세요. 흰 배경을 자동으로 지워서 빨간 인영만 PDF에 들어가요. 문서 글자 위에 겹쳐 찍어도 아래 글자가 비쳐 보여요. 직인 스캔 파일(PNG·JPG)이 있다면 그대로 올려도 돼요. 손으로 쓴 서명은 <a href="/ko/signature-image.html">서명 이미지 만들기</a>에서 먼저 깨끗하게 정리할 수 있어요.</p>
      <h3>여러 페이지에 서명하기</h3>
      <p>이전 · 다음 페이지로 넘기면서 필요한 곳마다 서명을 추가하세요. 모두 한 파일에 저장돼요. 사본 표시가 필요하면 <a href="/ko/watermark.html">워터마크</a>를, 메일로 보낼 파일이라면 <a href="/ko/compress-pdf-for-email.html">메일 첨부용으로 줄이기</a>를 함께 쓰세요.</p>""",
    faq_title="PDF 서명 넣기",
    faq=[
        ("PDF에 서명을 무료로 넣으려면요?", "이 페이지에 PDF를 올리고, 서명을 그리거나 이름으로 만들거나 이미지를 올린 뒤 이 페이지에 서명 넣기를 누르세요. 원하는 자리로 옮기고 서명하고 다운로드를 누르면 돼요."),
        ("PDF에 도장을 무료로 넣을 수 있나요?", "네. 이름 입력 탭에서 이름을 적고 빨간 원형 도장 스타일을 고르면 도장이 만들어져요. 이 페이지에 서명 넣기를 누르고 원하는 자리로 옮기면 돼요."),
        ("회사 직인을 PDF에 넣으려면요?", "흰 종이에 직인을 찍어 사진을 찍거나 직인 스캔 파일을 이미지 올리기로 넣으세요. 흰 배경을 지우고 인영만 PDF에 넣어요. 파일은 서버로 올라가지 않아요."),
        ("휴대폰에서도 되나요?", "네. 손가락으로 서명을 그리고, 미리보기에서 끌어서 위치를 정할 수 있어요."),
        ("PDF가 서버로 올라가나요?", "아니요. PDF와 서명 모두 브라우저 안에서만 처리돼서 서버로 가지 않아요."),
        ("이렇게 넣은 서명도 효력이 있나요?", "일상적인 신청서, 견적서, 개인 간 계약서 등에는 서명 이미지가 흔히 쓰여요. 다만 공동인증서(옛 공인인증서)를 이용한 전자서명과는 다르니, 특정 전자서명이 필요한 서류라면 받는 곳의 요구사항을 확인하세요."),
    ],
)

SIZE_FAQ_PRIVACY = ("파일이 서버에 남나요?", "글자를 유지하는 압축 단계에서 파일을 서버로 보내지만, 압축이 끝나면 바로 삭제해요. 이미지로 바꾸는 단계는 브라우저 안에서만 처리돼요.")

KO["compress-pdf-to-50kb.html"] = dict(
    title="PDF 50KB 이하로 줄이기 - 증명서 한 장도 선명하게 무료 | SlimIO",
    desc="증명서·신분증 사본·서명한 서류 한 장을 PDF 50KB 이하로 줄이세요. 이 용량 안에서 가장 읽기 좋게 맞춰요. 회원가입 없이 무료.",
    keywords="PDF 50KB 줄이기, PDF 50KB 이하, PDF 용량 50KB, 증명서 PDF 50KB, PDF 50KB 압축",
    short="PDF 50KB 이하로 줄이기 | SlimIO",
    app_name="SlimIO PDF 50KB 압축",
    app_desc="한 장짜리 PDF를 50KB 이하로 줄이는 무료 도구. 이 용량 안에서 가장 읽기 좋은 상태로 맞춰요.",
    features=["PDF 50KB 이하로 압축", "목표 용량 자동 맞춤", "회원가입 없음"],
    h1="PDF를<br /><b>50KB 이하로.</b>",
    lead="50KB는 스캔 한 장 정도의 아주 작은 용량이에요. 그 안에서 가장 선명한 버전을 찾아 드려요.",
    content="""
      <h2>PDF를 50KB로 줄이는 방법</h2>
      <ul>
          <li><b>1. 필요한 페이지만 남기기.</b> 50KB에는 현실적으로 한 장이 들어가요. 여러 장이라면 먼저 <a href="/ko/delete-pages.html">페이지 삭제</a>로 빼 주세요.</li>
          <li><b>2. 올리고 압축하기.</b> 목표는 이미 50KB예요. 한글·워드로 만든 PDF는 그대로 들어가는 경우가 많고, 스캔은 들어가는 가장 높은 해상도로 다시 만들어요.</li>
          <li><b>3. 올리기 전에 확인.</b> 결과를 열어 증명서 번호처럼 가장 작은 글자를 확대해 보세요.</li>
      </ul>
      <h3>50KB에는 얼마나 들어가나요?</h3>
      <p>한글·워드나 웹에서 만든 한 장짜리 PDF는 원래 20~40KB인 경우가 많아요. 스캔은 달라요. 폰으로 컬러 스캔한 한 장은 1~3MB라서 20~60배 줄여야 해요. 흑백 스캔은 50KB에서도 읽을 만하지만, 컬러로 찍은 서류 사진은 눈에 띄게 흐려져요.</p>
      <h3>잘 줄어들게 스캔하는 법</h3>
      <ul>
          <li>컬러 대신 <b>흑백(회색조)</b>으로 스캔하세요. 가장 크게 줄어요.</li>
          <li>어둡고 단색인 바닥에 종이를 놓고 화면을 꽉 채워 찍으세요. 책상이나 그림자가 없게요.</li>
          <li>해상도는 150dpi면 충분해요. 300dpi는 파일만 커져요.</li>
      </ul>
      <h3>JPG로 내도 된다면</h3>
      <p>원서가 PDF 대신 이미지도 받는다면, 같은 페이지를 JPG로 내는 편이 50KB에서 더 선명한 경우가 많아요. <a href="/ko/compress-image-to-50kb.html">사진 50KB로 줄이기</a>를 쓰세요.</p>""",
    faq_title="PDF 50KB 이하로 줄이기",
    faq=[
        ("PDF를 50KB로 줄이려면 어떻게 하나요?", "이 페이지에 PDF를 넣고 압축하기를 누르세요. 목표는 이미 50KB예요. 글자를 유지하는 압축을 먼저 해 보고, 그래야만 들어갈 때만 페이지를 이미지로 바꿔요."),
        ("세 장짜리 PDF도 50KB에 들어가나요?", "컴퓨터로 만든 글자 위주 문서라면 가능해요. 스캔 세 장을 50KB에 넣으면 흐려져요. 필요 없는 페이지를 빼거나, 가능하면 따로 올리세요."),
        ("스캔한 증명서가 흐릿해졌어요.", "컬러 스캔을 50KB로 맞추려면 세밀함이 많이 줄어요. 흑백 150dpi로 다시 스캔해서 압축하면 대개 훨씬 선명해요."),
        ("“20KB 이상 50KB 이하”처럼 최소 용량도 있어요.", "50KB 안에서 가장 좋은 화질로 만들기 때문에, 원본이 아주 작지 않다면 대개 20KB보다 넉넉히 커요. 결과에 나온 용량을 확인해 주세요."),
        SIZE_FAQ_PRIVACY,
    ],
)

KO["compress-pdf-to-300kb.html"] = dict(
    title="PDF 300KB 이하로 줄이기 - 증명서·성적표 스캔 무료 압축 | SlimIO",
    desc="성적증명서·졸업증명서·경력증명서처럼 여러 장 스캔한 PDF를 300KB 이하로 줄이세요. 회원가입 없이 무료, 들어가는 가장 좋은 화질로.",
    keywords="PDF 300KB 줄이기, PDF 300KB 이하, PDF 용량 300KB, 증명서 PDF 300KB, 스캔 PDF 300KB",
    short="PDF 300KB 이하로 줄이기 | SlimIO",
    app_name="SlimIO PDF 300KB 압축",
    app_desc="여러 장 스캔한 PDF를 300KB 이하로 줄이는 무료 도구. 들어가는 가장 좋은 화질을 찾아요.",
    features=["PDF 300KB 이하로 압축", "목표 용량 자동 맞춤", "회원가입 없음"],
    h1="PDF를<br /><b>300KB 이하로.</b>",
    lead="서류마다 “300KB 이하”인가요? 스캔한 증명서를 모든 페이지가 읽히게 맞춰 드려요.",
    content="""
      <h2>PDF를 300KB로 줄이는 방법</h2>
      <ul>
          <li><b>1. 페이지 모으기.</b> 서류 하나를 파일 하나로 내야 한다면, 스캔 PDF는 <a href="/ko/merge.html">PDF 합치기</a>로, 사진은 <a href="/ko/jpg-to-pdf.html">JPG → PDF</a>로 먼저 묶으세요.</li>
          <li><b>2. 올리고 압축하기.</b> 목표는 이미 300KB예요.</li>
          <li><b>3. 다운로드하고 확인.</b> 결과에 최종 용량과 글자 선택이 가능한지가 나와요.</li>
      </ul>
      <h3>300KB 제한을 자주 만나는 곳</h3>
      <p>입학·장학금·채용 시스템은 성적증명서, 졸업증명서, 경력증명서, 자격증 사본 같은 첨부 서류를 한 파일에 300KB 이하로 제한하는 경우가 많아요. 스캔으로 치면 대략 두세 장에서 다섯 장 정도예요.</p>
      <h3>폰으로 스캔하면 왜 이렇게 클까요?</h3>
      <p>스캔 앱은 페이지마다 고해상도 컬러 사진으로 저장해서, 세 장만 스캔해도 5~10MB가 되기 쉬워요. SlimIO는 먼저 글자를 유지하는 압축을 해 보고, 그래도 300KB를 넘으면 들어가는 가장 높은 해상도로 페이지를 다시 만들어요.</p>
      <h3>서류가 여러 개라면</h3>
      <ul>
          <li>서류마다 따로 압축하세요. 그래야 각 파일이 300KB를 온전히 쓸 수 있어요.</li>
          <li>빈 뒷면은 <a href="/ko/delete-pages.html">페이지 삭제</a>로 빼세요. 빈 페이지도 한 장만큼 용량을 차지해요.</li>
          <li>옆으로 누운 스캔은 <a href="/ko/rotate.html">PDF 회전</a>으로 바로 세운 뒤 압축하세요.</li>
      </ul>""",
    faq_title="PDF 300KB 이하로 줄이기",
    faq=[
        ("PDF를 300KB로 줄이려면요?", "이 페이지에 PDF를 넣고 압축하기를 누르세요. 목표는 이미 300KB이고, 그 안에서 가장 선명하게 만들어 드려요. 회원가입은 필요 없어요."),
        ("300KB에 몇 장까지 들어가나요?", "컴퓨터로 만든 PDF는 수십 장도 들어가요. 스캔은 두 장에서 다섯 장 정도까지 또렷하게 읽혀요."),
        ("증명서 여러 개를 PDF 하나로 묶어서 300KB로 만들 수 있나요?", "네. 먼저 PDF 합치기(사진은 JPG → PDF)로 묶은 뒤 여기서 압축하세요."),
        ("빨간 직인이나 도장도 남나요?", "네. 색은 그대로 남고, 용량을 맞추려고 세밀한 부분만 조금 줄어요."),
        SIZE_FAQ_PRIVACY,
    ],
)

KO["compress-pdf-to-2mb.html"] = dict(
    title="PDF 2MB 이하로 줄이기 - 글자 선명하게 무료 압축 | SlimIO",
    desc="학교·공공기관·은행·보험 제출 시스템의 2MB 제한에 맞춰 PDF를 줄이세요. 2MB면 대부분 글자가 선명하고 검색도 돼요. 회원가입 없이 무료.",
    keywords="PDF 2MB 줄이기, PDF 2MB 이하, PDF 용량 2MB, PDF 2MB 압축, 스캔 PDF 2MB",
    short="PDF 2MB 이하로 줄이기 | SlimIO",
    app_name="SlimIO PDF 2MB 압축",
    app_desc="PDF를 2MB 이하로 줄이는 무료 도구. 대부분 글자를 선명하고 검색 가능한 상태로 유지해요.",
    features=["PDF 2MB 이하로 압축", "글자 선명하게 유지", "회원가입 없음"],
    h1="PDF를<br /><b>2MB 이하로.</b>",
    lead="업로드 제한이 2MB인가요? 대부분의 PDF는 글자가 선명하고 검색되는 그대로 들어가요.",
    content="""
      <h2>PDF를 2MB로 줄이는 방법</h2>
      <ul>
          <li><b>1. PDF 올리기.</b> 목표 용량은 2MB로 맞춰져 있어요.</li>
          <li><b>2. 압축하기.</b> 이 용량에서는 글자를 그대로 두고 큰 이미지만 줄이는 부드러운 설정을 써요.</li>
          <li><b>3. 다운로드.</b> 결과에 글자 선택이 가능한지 함께 나와요.</li>
      </ul>
      <h3>2MB 제한을 자주 만나는 곳</h3>
      <p>대학 입학·대학원 원서 시스템, 공공기관 민원·입찰 첨부, 은행·보험 서류 제출, 회사 인사 시스템은 파일당 2MB로 제한하는 경우가 많아요. 스캔 앱으로 만든 PDF, 사진이 많은 보고서, PDF로 저장한 발표 자료, 그림이 많은 논문이 주로 넘어가요.</p>
      <h3>스캔 앱 PDF는 왜 15MB나 될까요?</h3>
      <p>폰 스캔 앱은 페이지마다 원본 해상도 사진으로 저장해서 한 장에 2~4MB가 되기도 해요. SlimIO가 줄이는 건 이 사진들이고, 페이지 배치는 그대로예요. 10장짜리 스캔도 대개 글자가 읽히는 상태로 2MB 안에 들어가요.</p>
      <h3>검색되는 PDF로 남기기</h3>
      <p>심사하는 쪽은 PDF 안에서 이름이나 번호를 검색하곤 해요. 컴퓨터로 만든 문서는 2MB에서 거의 항상 글자 정보가 그대로 남아서 검색과 복사가 돼요. 페이지를 이미지로 바꿔야만 들어가는 경우에는 결과에 알려 드려요.</p>""",
    faq_title="PDF 2MB 이하로 줄이기",
    faq=[
        ("PDF를 2MB보다 작게 만들려면요?", "이 페이지에 PDF를 넣고 압축하기를 누르세요. 목표는 이미 2MB이고, 글자는 선명하게 두고 이미지만 필요한 만큼 줄여요."),
        ("2MB로 줄여도 PDF 안에서 검색이 되나요?", "컴퓨터로 만든 문서라면 거의 항상 돼요. 스캔한 페이지는 원래 이미지라서 이미지인 채로 크기만 작아져요."),
        ("폰으로 스캔한 15MB PDF도 2MB로 줄어드나요?", "대개 줄어요. 용량 대부분이 페이지마다 저장된 고해상도 사진이라 잘 줄어들어요."),
        ("PDF 여러 개를 각각 2MB로 줄일 수 있나요?", "네. 하나씩 차례로 압축하면 파일마다 2MB 목표로 맞춰요."),
        SIZE_FAQ_PRIVACY,
    ],
)

KO["compress-pdf-to-100kb.html"] = dict(
    title="PDF 100KB 이하로 줄이기 - 무료 용량 맞춤 압축 | SlimIO",
    desc="채용·공공기관 사이트 업로드용으로 PDF를 100KB 이하로 줄이세요. 제한 안에서 가장 좋은 화질을 자동으로 찾아요. 회원가입 없이 무료.",
    keywords="PDF 100KB 줄이기, PDF 100KB 이하, PDF 용량 100KB, PDF 100KB 압축, PDF 용량 줄이기 100KB",
    short="PDF 100KB 이하로 줄이기 | SlimIO",
    app_name="SlimIO PDF 100KB 압축",
    app_desc="PDF를 100KB 이하로 줄이는 무료 도구. 제한 안에서 가장 좋은 화질을 자동으로 찾아요.",
    features=["PDF 100KB 이하로 압축", "목표 용량 자동 맞춤", "회원가입 없음"],
    h1="PDF를<br /><b>100KB 이하로.</b>",
    lead="“100KB 이하만 첨부 가능”에 막혔나요? PDF를 넣으면 제한 안에서 가장 선명한 파일로 만들어 드려요.",
    content="""
      <h2>PDF를 100KB로 줄이는 방법</h2>
      <ul>
          <li><b>1. PDF 올리기.</b> 목표 용량은 이미 100KB로 맞춰져 있어요.</li>
          <li><b>2. 압축하기.</b> 먼저 글자를 유지하는 압축을 해 보고, 그래도 크면 이미지 해상도를 조금씩 낮춰 100KB 안에 맞춰요.</li>
          <li><b>3. 다운로드.</b> 100KB 안에서 가장 선명한 파일을 받으세요.</li>
      </ul>
      <h3>100KB 제한은 어디서 만나나요?</h3>
      <p>공공기관·기업 채용 사이트, 자격시험 접수, 각종 지원사업 신청 시스템에서 증명서, 신분증 사본, 자격증 스캔본을 올릴 때 파일당 100KB 제한이 자주 있어요.</p>
      <h3>100KB에 얼마나 들어갈까요?</h3>
      <p>스캔한 1~2페이지는 충분히 읽을 수 있게 들어가요. 워드나 한글에서 PDF로 저장한 문서는 원래 100KB보다 작은 경우가 많아요. 10페이지가 넘는 스캔본은 해상도를 많이 낮춰야 해서 작은 글씨가 흐려질 수 있어요.</p>
      <h3>더 선명하게 만드는 팁</h3>
      <ul>
          <li>제출할 페이지만 남기세요. <a href="/ko/delete-pages.html">페이지 삭제</a>나 <a href="/ko/split.html">PDF 나누기</a>로 먼저 줄이면 훨씬 선명해져요.</li>
          <li>스캔할 때는 컬러 대신 흑백, 150~200dpi로 하세요. 컬러 스캔은 용량을 훨씬 많이 차지해요.</li>
          <li>여백이 넓다면 스캔할 때 잘라 내세요.</li>
      </ul>""",
    faq_title="PDF 100KB 이하로 줄이기",
    faq=[
        ("PDF를 100KB로 무료로 줄일 수 있나요?", "네. 이 페이지에 PDF를 넣고 압축하기를 누르면 돼요. 목표는 이미 100KB로 맞춰져 있고, 회원가입 없이 바로 받을 수 있어요."),
        ("압축했는데도 100KB가 넘어요.", "페이지가 아주 많거나 세밀한 스캔본은 읽을 수 있는 화질로 100KB 안에 넣기 어려워요. 그럴 땐 가장 작게 만든 파일을 드려요. 필요 없는 페이지를 빼거나 파일을 나눠 올려 보세요."),
        ("100KB로 줄이면 글자가 읽히나요?", "1~2페이지라면 충분히 읽혀요. 목표 용량에 맞출 만큼만 해상도를 낮추기 때문에 짧은 문서는 선명하게 유지돼요."),
        ("압축한 뒤에도 글자를 복사할 수 있나요?", "글자를 유지하는 압축만으로 100KB가 되면 복사할 수 있어요. 이미지로 바꿔야 했다면 복사는 안 돼요. 결과 화면에서 어느 쪽인지 알려 드려요."),
        SIZE_FAQ_PRIVACY,
    ],
)

KO["compress-pdf-to-200kb.html"] = dict(
    title="PDF 200KB 이하로 줄이기 - 무료 용량 맞춤 압축 | SlimIO",
    desc="입학·장학금·지원사업 서류용으로 PDF를 200KB 이하로 줄이세요. 제한 안에서 가장 좋은 화질을 자동으로 찾아요. 회원가입 없이 무료.",
    keywords="PDF 200KB 줄이기, PDF 200KB 이하, PDF 용량 200KB, PDF 200KB 압축, PDF 용량 줄이기 200KB",
    short="PDF 200KB 이하로 줄이기 | SlimIO",
    app_name="SlimIO PDF 200KB 압축",
    app_desc="PDF를 200KB 이하로 줄이는 무료 도구. 제한 안에서 가장 좋은 화질을 자동으로 찾아요.",
    features=["PDF 200KB 이하로 압축", "목표 용량 자동 맞춤", "회원가입 없음"],
    h1="PDF를<br /><b>200KB 이하로.</b>",
    lead="서류마다 “200KB 이하” 제한이 있나요? 제한 안에서 가장 선명하게 맞춰 드려요.",
    content="""
      <h2>PDF를 200KB로 줄이는 방법</h2>
      <ul>
          <li><b>1. PDF 올리기.</b> 목표 용량은 200KB로 맞춰져 있어요. 다른 용량이 필요하면 바꿀 수 있어요.</li>
          <li><b>2. 압축하기.</b> 글자를 유지하는 압축을 먼저 하고, 필요할 때만 이미지 해상도를 낮춰요.</li>
          <li><b>3. 다운로드.</b> 200KB 안에 맞춘 파일을 받으세요.</li>
      </ul>
      <h3>200KB 제한을 자주 만나는 곳</h3>
      <p>대학·대학원 입학 원서 접수, 장학금 신청, 정부 지원사업 신청 시스템에서 졸업증명서, 성적증명서, 추천서 같은 증빙 서류를 파일당 200KB 안팎으로 제한하는 경우가 많아요.</p>
      <h3>200KB에 몇 페이지까지 들어갈까요?</h3>
      <p>스캔한 문서 2~4페이지는 편하게 읽을 수 있는 화질로 들어가요. 워드나 한글에서 PDF로 저장한 문서라면 사진이 조금 있어도 글자가 선명한 채로 들어가는 경우가 많아요.</p>
      <h3>더 선명하게 만드는 팁</h3>
      <ul>
          <li>필요한 페이지만 <a href="/ko/merge.html">합치거나</a> 필요 없는 페이지는 <a href="/ko/delete-pages.html">삭제</a>하세요.</li>
          <li>옆으로 누운 스캔본은 <a href="/ko/rotate.html">PDF 회전</a>으로 먼저 바로잡으세요.</li>
          <li>글자 위주의 서류는 흑백으로 스캔하면 훨씬 작아져요.</li>
      </ul>""",
    faq_title="PDF 200KB 이하로 줄이기",
    faq=[
        ("PDF를 200KB로 줄이려면 어떻게 하나요?", "이 페이지에 PDF를 넣고 압축하기를 누르세요. 목표는 이미 200KB이고, 그 안에 들어가는 가장 좋은 화질로 만들어 드려요."),
        ("성적증명서가 5페이지인데 200KB에 들어갈까요?", "PDF로 발급받은 파일이라면 대부분 들어가요. 5페이지 스캔본이라면 해상도를 조금 낮춰야 할 수 있지만, 200KB 안에서 가장 높은 해상도를 골라 드려요."),
        ("압축하면 내용이 바뀌나요?", "아니요. 페이지 수, 순서, 종이 크기는 그대로예요. 이미지의 세밀함만 줄어들어요."),
        ("다른 용량으로도 맞출 수 있나요?", "네. 목표 용량에서 50KB부터 25MB까지 고를 수 있어요."),
        SIZE_FAQ_PRIVACY,
    ],
)

KO["compress-pdf-to-500kb.html"] = dict(
    title="PDF 500KB 이하로 줄이기 - 이력서·지원서용 무료 압축 | SlimIO",
    desc="이력서·포트폴리오를 500KB 이하로 줄이세요. 대부분의 문서는 글자가 선명하고 검색도 그대로 돼요. 회원가입 없이 무료.",
    keywords="PDF 500KB 줄이기, PDF 500KB 이하, 이력서 PDF 용량 줄이기, PDF 용량 500KB, PDF 500KB 압축",
    short="PDF 500KB 이하로 줄이기 | SlimIO",
    app_name="SlimIO PDF 500KB 압축",
    app_desc="PDF를 500KB 이하로 줄이는 무료 도구. 대부분의 문서는 글자를 선명하게 유지해요.",
    features=["PDF 500KB 이하로 압축", "목표 용량 자동 맞춤", "회원가입 없음"],
    h1="PDF를<br /><b>500KB 이하로.</b>",
    lead="이력서 첨부가 “500KB 이하”인가요? 대부분의 문서는 글자를 선명하게 유지한 채 맞춰 드려요.",
    content="""
      <h2>PDF를 500KB로 줄이는 방법</h2>
      <ul>
          <li><b>1. PDF 올리기.</b> 목표 용량은 500KB로 맞춰져 있어요.</li>
          <li><b>2. 압축하기.</b> 글자를 유지하는 압축을 먼저 해요. 500KB라면 대부분 이 단계에서 끝나요.</li>
          <li><b>3. 다운로드.</b> 바로 올릴 수 있는 파일을 받으세요.</li>
      </ul>
      <h3>이력서와 자기소개서</h3>
      <p>채용 사이트나 회사 지원 시스템은 이력서 첨부를 500KB 안팎으로 제한하는 경우가 많아요. 사진이 들어간 이력서, 디자인 템플릿, 글꼴이 포함된 파일은 쉽게 넘어가요. 500KB면 글자를 선명하게 유지할 여유가 있어서, 채용 담당자가 내용을 검색하고 복사할 수 있어요.</p>
      <h3>잘 들어가는 문서</h3>
      <p>몇 페이지짜리 포트폴리오, 서명한 계약서, 보험금 청구 서류, 10페이지 정도의 스캔본까지는 500KB 안에 읽기 좋게 들어가요.</p>
      <h3>이력서를 검색 가능하게 유지하려면</h3>
      <ul>
          <li>스캔본이나 사진 대신, 워드·한글에서 바로 PDF로 저장한 원본으로 압축하세요.</li>
          <li>큰 배경 이미지나 페이지 전체를 채운 그림이 용량을 가장 많이 차지해요. 빼도 된다면 빼 주세요.</li>
          <li>여러 장이라면 <a href="/ko/add-page-numbers.html">페이지 번호</a>를 넣어 두면 읽는 사람이 편해요.</li>
      </ul>""",
    faq_title="PDF 500KB 이하로 줄이기",
    faq=[
        ("이력서 PDF를 500KB 이하로 줄이려면요?", "이 페이지에 PDF를 넣고 압축하기를 누르세요. 가능하면 글자를 선택할 수 있게 유지하고, 이미지만 줄여요."),
        ("압축해도 채용 담당자가 내용을 검색할 수 있나요?", "글자를 유지하는 압축으로 500KB가 되면 그대로 검색·복사돼요. 대부분의 이력서가 여기에 해당하고, 결과 화면에서 알려 드려요."),
        ("10페이지 문서도 500KB에 들어가나요?", "워드나 한글에서 만든 PDF라면 대부분 들어가요. 스캔본은 10페이지 정도까지 읽기 좋게 들어가요."),
        ("압축한 파일에 워터마크가 붙나요?", "아니요. 워터마크나 광고 문구는 전혀 붙지 않아요."),
        SIZE_FAQ_PRIVACY,
    ],
)

KO["compress-pdf-to-1mb.html"] = dict(
    title="PDF 1MB 이하로 줄이기 - 무료 용량 맞춤 압축 | SlimIO",
    desc="과제 제출, 전자결재, 신청서 첨부용으로 PDF를 1MB 이하로 줄이세요. 대부분 글자가 선명하게 유지돼요. 회원가입 없이 무료.",
    keywords="PDF 1MB 줄이기, PDF 1MB 이하, PDF 용량 1MB, PDF 1MB 압축, PDF 용량 줄이기 1MB",
    short="PDF 1MB 이하로 줄이기 | SlimIO",
    app_name="SlimIO PDF 1MB 압축",
    app_desc="PDF를 1MB 이하로 줄이는 무료 도구. 대부분의 파일은 글자를 선명하게 유지해요.",
    features=["PDF 1MB 이하로 압축", "목표 용량 자동 맞춤", "회원가입 없음"],
    h1="PDF를<br /><b>1MB 이하로.</b>",
    lead="어떤 PDF든 1MB 안으로. 대부분은 글자가 선명한 채로 맞춰져요.",
    content="""
      <h2>PDF를 1MB로 줄이는 방법</h2>
      <ul>
          <li><b>1. PDF 올리기.</b> 목표 용량은 1MB로 맞춰져 있어요.</li>
          <li><b>2. 압축하기.</b> 글자를 유지하는 압축을 먼저 하고, 그래도 크면 이미지 해상도를 낮춰요.</li>
          <li><b>3. 다운로드.</b> 1MB 안에 맞춘 파일을 받으세요.</li>
      </ul>
      <h3>1MB 제한을 자주 만나는 곳</h3>
      <p>대학 과제 제출 시스템, 회사 전자결재·그룹웨어 첨부, 각종 온라인 신청서, 고객센터 문의 양식은 첨부 파일을 1MB로 제한하는 경우가 많아요. 사진이 많은 보고서나 PDF로 저장한 발표 자료가 주로 넘어가요.</p>
      <h3>어떻게 달라지나요?</h3>
      <p>글자 위주의 문서와 보고서는 대부분 글자가 선명한 채로 1MB 안에 들어가요. 전체 화면 사진이 많은 발표 자료는 이미지로 바꿔야 할 수 있지만, 그래도 1MB 안에서 가장 높은 해상도로 맞춰요.</p>
      <h3>그래도 크다면</h3>
      <ul>
          <li>긴 파일은 <a href="/ko/split.html">PDF 나누기</a>로 나눠서 따로 올리세요.</li>
          <li>부록이나 빈 페이지는 <a href="/ko/delete-pages.html">페이지 삭제</a>로 빼세요.</li>
          <li>화질을 직접 정하고 싶다면 <a href="/ko/">PDF 용량 줄이기</a>에서 설정을 바꿔 보세요.</li>
      </ul>""",
    faq_title="PDF 1MB 이하로 줄이기",
    faq=[
        ("PDF를 1MB보다 작게 만들려면요?", "이 페이지에 PDF를 넣고 압축하기를 누르세요. 목표는 이미 1MB이고, 그 안에서 가장 좋은 화질로 만들어 드려요."),
        ("발표 자료의 도표와 글자가 선명하게 남나요?", "1MB라면 도표와 글자는 대부분 선명하게 남아요. 크게 줄어드는 건 사진이에요."),
        ("30MB짜리 PDF도 1MB로 줄어드나요?", "용량 대부분이 사진이라면 대개 가능해요. 아주 긴 문서는 세밀함이 떨어질 수 있으니 나눠서 올리는 것도 방법이에요."),
        ("일반 PDF 압축과 뭐가 다른가요?", "일반 압축은 화질을 직접 고르는 방식이고, 이 페이지는 목표 용량을 정하면 그 안에 맞는 설정을 알아서 찾아 줘요."),
        SIZE_FAQ_PRIVACY,
    ],
)

KO["compress-pdf-for-email.html"] = dict(
    title="메일 첨부용 PDF 용량 줄이기 - 네이버·지메일 첨부 한도 | SlimIO",
    desc="PDF가 커서 메일 첨부가 안 되나요? 네이버 메일 10MB, 지메일·다음 메일 25MB 기준에 맞게 PDF 용량을 줄이세요. 회원가입 없이 무료.",
    keywords="메일 첨부 PDF 용량 줄이기, PDF 메일 첨부 용량, 네이버 메일 첨부 용량, 지메일 첨부 용량, PDF 용량 줄이기 메일",
    short="메일 첨부용 PDF 용량 줄이기 | SlimIO",
    app_name="SlimIO 메일 첨부용 PDF 압축",
    app_desc="메일 첨부 한도에 맞게 PDF 용량을 줄이는 무료 도구. 제한 안에서 가장 좋은 화질을 자동으로 찾아요.",
    features=["메일 첨부 한도에 맞춰 압축", "목표 용량 자동 맞춤", "회원가입 없음"],
    h1="PDF가 커서<br /><b>메일로 못 보낼 때.</b>",
    lead="네이버 메일, 지메일, 회사 메일 첨부 한도에 맞게 PDF를 줄여요. 화질은 최대한 그대로.",
    content="""
      <h2>메일로 보낼 PDF 줄이는 방법</h2>
      <ul>
          <li><b>1. PDF 올리기.</b> 목표 용량은 10MB로 맞춰져 있어요. 대부분의 메일에서 일반 첨부로 보낼 수 있는 크기예요.</li>
          <li><b>2. 한도 고르기.</b> 보낼 곳의 한도를 안다면 아래 표를 보고 목표 용량을 바꾼 뒤 압축하세요.</li>
          <li><b>3. 다운로드해서 첨부하세요.</b></li>
      </ul>
      <h3>메일 서비스별 첨부 한도</h3>
      <ul>
          <li><b>네이버 메일:</b> 파일 하나가 10MB를 넘으면 ‘대용량 첨부’로 바뀌어요. 대용량 첨부는 30일이 지나면 받을 수 없게 돼요.</li>
          <li><b>다음 메일:</b> 25MB까지 일반 첨부, 넘으면 대용량 첨부로 바뀌어요.</li>
          <li><b>지메일:</b> 메일 한 통에 25MB까지 첨부할 수 있어요.</li>
          <li><b>회사 메일:</b> 회사 메일 서버는 10MB 안팎으로 정해진 경우가 많고, 받는 쪽 서버의 한도도 함께 적용돼요.</li>
      </ul>
      <h3>한도보다 작은데도 반송된다면</h3>
      <p>첨부 파일은 보낼 때 인코딩되면서 크기가 약 3분의 1 커져요. 20MB PDF는 실제로 27MB 정도로 전송돼서 25MB 한도에 걸릴 수 있어요. 받는 사람의 메일 환경을 모른다면 10MB 이하로 줄이는 게 안전해요.</p>
      <h3>여러 파일을 보내야 한다면</h3>
      <p><a href="/ko/merge.html">PDF 합치기</a>로 먼저 하나로 묶은 다음 한 번에 압축하세요. 그래도 한 통에 다 들어가지 않으면 <a href="/ko/split.html">PDF 나누기</a>로 나눠 여러 통으로 보내세요.</p>""",
    faq_title="메일 첨부용 PDF 용량 줄이기",
    faq=[
        ("메일로 보낼 수 있게 PDF를 줄이려면요?", "이 페이지에 PDF를 넣고 압축하기를 누르세요. 기본 목표인 10MB는 대부분의 메일에서 일반 첨부로 보낼 수 있어요."),
        ("네이버 메일은 몇 MB까지 일반 첨부로 보낼 수 있나요?", "파일 하나가 10MB를 넘으면 대용량 첨부로 바뀌고, 30일이 지나면 받을 수 없게 돼요. 오래 보관해야 하는 서류라면 10MB 이하로 줄여서 일반 첨부로 보내세요."),
        ("지메일 첨부 한도는 얼마인가요?", "메일 한 통에 25MB까지예요. 다만 전송할 때 크기가 커지므로 PDF는 18MB 이하, 여유 있게는 10MB 이하로 줄이는 게 좋아요."),
        ("받는 사람이 보는 화질이 떨어지나요?", "가능하면 글자를 선명하게 유지하고, 이미지는 필요한 만큼만 줄여요. 일반적인 문서라면 차이를 느끼기 어려워요."),
        ("올릴 수 있는 파일 크기에 제한이 있나요?", "50MB까지는 서버에서 글자를 유지하며 압축해요. 그보다 큰 파일은 브라우저 안에서 압축해요."),
    ],
)

# --- helpers -----------------------------------------------------------------
def sub1(pattern, repl, s, what):
    out, n = re.subn(pattern, repl, s, count=1, flags=re.S)
    if n != 1:
        sys.exit(f"[{what}] pattern not found: {pattern[:70]}")
    return out


def faq_html(title, faq):
    items = "\n".join(
        f"      <details{' open' if i == 0 else ''}>\n          <summary>{html.escape(q)}</summary>\n          <p>{html.escape(a)}</p>\n      </details>"
        for i, (q, a) in enumerate(faq))
    return f'<section class="faq">\n      <h2>{html.escape(title)} — 자주 묻는 질문</h2>\n{items}\n</section>'


def faq_ld(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}


def ld_script(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=6) + "\n</script>"


def set_meta(s, d, page):
    url = SITE + ko_path(page)
    s = s.replace('<html lang="en">', '<html lang="ko">')
    s = sub1(r"<title>.*?</title>", f"<title>{html.escape(d['title'])}</title>", s, page)
    for attr, key, val in [("name", "description", d["desc"]), ("name", "keywords", d["keywords"]),
                           ("property", "og:title", d["title"]), ("property", "og:description", d["desc"]),
                           ("name", "twitter:title", d["short"]), ("name", "twitter:description", d["desc"]),
                           ("property", "og:url", url), ("property", "og:locale", "ko_KR")]:
        s = sub1(rf'(<meta {attr}="{re.escape(key)}" content=")[^"]*(")', lambda m: m.group(1) + html.escape(val, quote=True) + m.group(2), s, f"{page} {key}")
    s = sub1(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1) + url + m.group(2), s, page)
    return s


def set_ld(s, d, page):
    add_faq = '"FAQPage"' not in s   # some English pages have no FAQ; the Korean ones all do
    def fix(m):
        obj = json.loads(m.group(1))
        if obj.get("@type") == "WebApplication":
            obj.update(name=d["app_name"], url=SITE + ko_path(page), description=d["app_desc"],
                       featureList=d["features"], inLanguage="ko", browserRequirements="최신 웹 브라우저")
            out = ld_script(obj)
            if add_faq:
                out += "\n" + ld_script(faq_ld(d["faq"]))
            return out
        if obj.get("@type") == "FAQPage":
            return ld_script(faq_ld(d["faq"]))
        return m.group(0)
    return re.sub(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', fix, s, flags=re.S)


def rewrite_links(s):
    def fix(m):
        target = m.group(2)
        path, _, frag = target.partition("#")
        if path in ("", "/") and target.startswith("/"):
            return f'{m.group(1)}/ko/{("#" + frag) if frag else ""}"'
        if path.startswith("/") and (path[1:] in PAGES or path[1:] in INFO_PAGES):
            return f'{m.group(1)}/ko{target}"'
        return m.group(0)
    return re.sub(r'(href=")(/[^"]*)"', fix, s)


def lang_links(s, page, lang):
    """hreflang alternates + a visible switch, on both versions. Idempotent."""
    s = re.sub(r'\n<link rel="alternate" hreflang="[^"]+" href="[^"]+" />', "", s)
    alt = (f'\n<link rel="alternate" hreflang="en" href="{SITE}{en_path(page)}" />'
           f'\n<link rel="alternate" hreflang="ko" href="{SITE}{ko_path(page)}" />'
           f'\n<link rel="alternate" hreflang="x-default" href="{SITE}{en_path(page)}" />')
    s = sub1(r'(<link rel="canonical" href="[^"]*" />)', lambda m: m.group(1) + alt, s, f"{page} canonical")
    s = re.sub(r'\n\s*<a [^>]*class="lang-switch"[^>]*>.*?</a>', "", s)
    s = re.sub(r'\n\s*<div class="lang-foot">.*?</div>', "", s)
    other, label, code, flag = (ko_path(page), "한국어", "ko", "kr") if lang == "en" else (en_path(page), "English", "en", "us")
    link = (f'<a href="{other}" hreflang="{code}" lang="{code}" class="lang-switch">'
            f'<img src="/img/flag-{flag}.svg" alt="" width="20" height="14" style="vertical-align:-2px;border-radius:2px;margin-right:6px" />{label}</a>')
    s = sub1(r'(<div class="nav-links">.*?)(\n\s*</div>)', lambda m: m.group(1) + "\n              " + link + m.group(2), s, f"{page} nav")
    s = sub1(r'(<div class="foot">.*?)(\n\s*</div>\n\s*</footer>)', lambda m: m.group(1) + f'\n              <div class="lang-foot">{link}</div>' + m.group(2), s, f"{page} footer")
    return s


INDEX_EXTRA_CSS = """
    body { word-break: keep-all; overflow-wrap: break-word; }
    .content { max-width: 760px; margin: 0 auto; padding: 10px 20px 0; }
    .content h2 { font-size: 24px; margin: 36px 0 10px; }
    .content h3 { font-size: 18px; margin: 22px 0 8px; color: var(--text); }
    .content p, .content ul { color: var(--muted); font-size: 15px; margin: 10px 0; }
    .content ul { margin-left: 20px; }
    .content li { margin: 6px 0; }
    .content a { color: var(--accent); text-decoration: underline; text-underline-offset: 2px; }
    .faq { max-width: 760px; margin: 0 auto; padding: 36px 20px 0; }
    .faq h2 { font-size: 24px; margin-bottom: 18px; }
    .faq details { border: 1px solid var(--line); border-radius: 12px; margin: 10px 0; background: var(--card); padding: 14px 18px; }
    .faq summary { cursor: pointer; font-weight: 600; font-size: 15px; list-style: none; }
    .faq summary::-webkit-details-marker { display: none; }
    .faq summary::after { content: "+"; float: right; color: var(--accent); }
    .faq details[open] summary::after { content: "−"; }
    .faq p { color: var(--muted); font-size: 14px; margin: 10px 0 0; }
"""

ALLOWED_EN = {"PDF", "PDFs", "DS", "IBPS", "SBI", "JPEG", "mm", "cm", "px", "JPG", "PNG", "WebP", "ZIP", "KB", "MB", "GB", "SlimIO", "Ghostscript", "dpi", "pt",
              "Page", "of", "English", "OO", "Pro", "SNS", "EXIF", "HEIC", "GPS", "cm", "px"}


def leftover_english(s):
    body = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", " ", s, flags=re.S)
    found = []
    for m in re.finditer(r">([^<>]+)<", body):
        for w in re.findall(r"[A-Za-z]{2,}", m.group(1)):
            if w not in ALLOWED_EN:
                found.append((w, m.group(1).strip()[:60]))
    for m in re.finditer(r'(?:title|placeholder|alt|aria-label)="([^"]*[A-Za-z]{3,}[^"]*)"', body):
        if any(w not in ALLOWED_EN for w in re.findall(r"[A-Za-z]{3,}", m.group(1))):
            found.append(("attr", m.group(1)))
    return found


def build(page):
    d = KO[page]
    s = open(os.path.join(ROOT, page)).read()
    s = set_meta(s, d, page)
    s = set_ld(s, d, page)
    s = sub1(r'(<div class="hero">\s*<h1>).*?(</h1>\s*<p>).*?(</p>)', lambda m: m.group(1) + d["h1"] + m.group(2) + d["lead"] + m.group(3), s, f"{page} hero")
    image_page = page.startswith("compress-image") or page in ("compress-id-photo.html", "us-visa-photo.html")   # built from compress-image.html
    ui = (d.get("ui") or (KO["compress-image.html"]["ui"] if image_page else [])) + d.get("ui_extra", []) + (SIZE_UI if page in SIZE_PAGES else [])
    for en, ko in ui:
        if en not in s:
            sys.exit(f"[{page}] UI text not found (English page changed?): {en!r}")
        s = s.replace(en, ko)
    if page in SIZE_PAGES or image_page:
        s = re.sub(r">Under (\d+(?:KB|MB))<", r">\1 이하<", s)
    for en, ko in COMMON:
        s = s.replace(en, ko)
    block = f'<div class="content">{d["content"]}\n</div>\n\n{faq_html(d["faq_title"], d["faq"])}'
    if page == "index.html":
        s = sub1(r"(\n\s*<!-- pricing -->)", lambda m: "\n" + block + "\n" + m.group(1), s, "index content")
        s = sub1(r"(<style>)", lambda m: m.group(1) + INDEX_EXTRA_CSS, s, "index css")
    elif '<section class="faq">' in s:
        s = sub1(r'<div class="content">.*?</div>\s*<section class="faq">.*?</section>', lambda m: block, s, f"{page} content")
    else:
        s = sub1(r'<div class="content">.*?</div>', lambda m: block, s, f"{page} content")
    s = rewrite_links(s)
    s = sub1(r'(<script defer src="/lib\.js\?v=[a-z0-9]+"></script>)', lambda m: '<script defer src="/i18n/ko.js?v=0"></script>\n' + m.group(1), s, f"{page} lib.js")
    s = lang_links(s, page, "ko")
    left = leftover_english(s)
    if left:
        for w, ctx in left:
            print(f"  [{page}] untranslated: {w!r} in {ctx!r}")
        sys.exit(f"[{page}] has untranslated text")
    os.makedirs(os.path.join(ROOT, "ko"), exist_ok=True)
    open(os.path.join(ROOT, "ko", page), "w").write(s)


def write_sitemap():
    urls = [en_path(p) for p in PAGES + INFO_PAGES + EN_ONLY] + [ko_path(p) for p in PAGES + INFO_PAGES]
    body = "".join(f"""       <url>
           <loc>{SITE}{u}</loc>
           <lastmod>{TODAY}</lastmod>
           <changefreq>weekly</changefreq>
           <priority>{'1.0' if u in ('/', '/ko/') else '0.8' if 'compress-pdf-' in u else '0.9'}</priority>
       </url>
""" for u in urls)
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n")


COMMON += gen_related.ko_pairs()

if __name__ == "__main__":
    gen_related.run()
    missing = [p for p in PAGES if p not in KO]
    if missing:
        sys.exit(f"no Korean text for: {missing}")
    for p in PAGES:
        build(p)
        en_file = os.path.join(ROOT, p)
        en_html = lang_links(open(en_file).read(), p, "en")   # read fully before reopening for write
        open(en_file, "w").write(en_html)
        print("ok", ko_path(p))
    for p in INFO_PAGES:
        for path, lang in ((os.path.join(ROOT, p), "en"), (os.path.join(ROOT, "ko", p), "ko")):
            html_ = lang_links(open(path).read(), p, lang)
            open(path, "w").write(html_)
    write_sitemap()
    print(f"sitemap: {2 * len(PAGES + INFO_PAGES)} URLs")
