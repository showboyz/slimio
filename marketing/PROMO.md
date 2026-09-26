# SlimIO 홍보 키트

복사해서 붙여 넣기만 하면 되는 문구 모음이에요. 이미지는 같은 폴더에 있어요.

| 파일 | 용도 |
|---|---|
| `logo-512.png` | 로고 / 아이콘 (512×512) |
| `shot-1-home.png` | 대표 스크린샷 (메인 압축) |
| `shot-2-organize.png` | 페이지 정리 (썸네일) |
| `shot-3-compress-to-100kb.png` | 100KB로 압축 결과 |
| `shot-4-email.png` | 이메일용 압축 결과 (24.8MB → 1.25MB) |

## 올릴 때 꼭 지킬 것
- **정확하게 말하기:** "대부분의 도구는 브라우저에서만 동작"은 맞지만, **서버 압축 모드와 목표 용량 압축은 파일을 서버로 보내요**(처리 직후 삭제). "아무것도 업로드 안 됨"이라고 쓰면 안 돼요. 댓글에서 바로 지적당해요.
- **만든 사람이라고 밝히기:** Reddit이나 커뮤니티에서 숨기면 스팸으로 신고되고, 도메인이 차단될 수 있어요.
- **같은 문구를 여러 곳에 동시에 뿌리지 않기:** 하루 1~2곳씩 올리고 댓글에 답하는 게 효과가 더 좋아요.
- 광고가 붙을 예정이라는 것, 하루 20회 제한도 물어보면 솔직하게 답하기

---

## 1. 한 번 등록해 두면 계속 남는 곳 (백링크)

### AlternativeTo — https://alternativeto.net
iLovePDF, Smallpdf, Adobe Acrobat Online, PDF24의 **대안(alternative)**으로 등록하세요. 대안을 찾는 사람이 들어오는 곳이라 전환율이 좋아요.
- **Name:** SlimIO
- **URL:** https://pdfslimio.com
- **Tagline:** Free PDF tools that mostly run in your browser — no signup, no watermark
- **Description:**
  > SlimIO is a free set of PDF tools: compress, compress to an exact size (100KB, 200KB, 500KB, 1MB, email), merge, split, remove pages, rotate, reorder pages with previews, add page numbers, watermark, PDF to JPG and JPG to PDF.
  >
  > Most tools run entirely in your browser, so the file never leaves your device. Server compression (Ghostscript) keeps text sharp and deletes files right after processing. No signup, no watermark on results.
- **Tags:** pdf, pdf-compressor, merge-pdf, split-pdf, privacy, web-based, free
- **License:** Free
- **Platforms:** Online / Web

### SaaSHub — https://www.saashub.com
- 위와 같은 설명을 쓰고, 경쟁 제품에 iLovePDF와 Smallpdf를 넣으세요.

### Uneed — https://www.uneed.best
- 무료로 등록하면 대기열 순서대로 소개돼요. 위 설명과 스크린샷 1~3번을 쓰세요.

### Product Hunt — https://www.producthunt.com
- **지금 말고, 나중에 올리세요.** 한 번뿐인 기회라서 기능이 더 쌓이고 한국어 페이지까지 준비된 다음이 좋아요.

---

## 2. 반응을 바로 볼 수 있는 곳

### Hacker News "Show HN" — https://news.ycombinator.com/submit
개발자가 많고, 브라우저에서 동작하는 프라이버시 중심 도구를 좋아해요. 1페이지에 오르면 하루에 수천 명이 들어와요. 안 올라가도 손해는 없어요.
- **올리는 시간:** 미국 동부 평일 오전 8~10시 = **한국 시간 밤 9~11시**(화~목)
- **Title:** `Show HN: SlimIO – Free PDF tools that mostly run in the browser`
- **URL:** `https://pdfslimio.com`
- **올린 직후 첫 댓글(본인):**
  > Hi HN, I built SlimIO because the popular PDF sites want an account, add watermarks or upload every file to their servers.
  >
  > Most tools (merge, split, rotate, reorder, page numbers, watermark, PDF↔JPG) run entirely in the browser with pdf.js and pdf-lib — the file never leaves your machine.
  >
  > Compression has two modes: in-browser (re-renders pages as images, fully local) or server-side Ghostscript, which keeps text sharp and selectable. Server files are written to a temp file and deleted right after the response.
  >
  > The newest part is "compress to an exact size": it tries Ghostscript first, and if the result is still over the target (say 100KB for a job portal), it steps resolution and JPEG quality down in the browser and keeps the best-looking version that fits.
  >
  > It's free with a daily limit of 20 operations, no signup. I'd love feedback — especially PDFs that come out worse than you'd expect.
- 댓글이 달리면 **몇 시간 동안 빠르게 답하는 게** 순위 유지에 제일 중요해요.

### GeekNews (한국) — https://news.hada.io
한국 개발자 커뮤니티예요. 제목을 **"Show GN:"**으로 시작하면 직접 만든 프로젝트 소개로 올릴 수 있어요.
- **제목:** `Show GN: SlimIO - 가입 없이 브라우저에서 동작하는 무료 PDF 도구 모음`
- **URL:** `https://pdfslimio.com/ko/`
- **본문:**
  > PDF 압축·합치기·나누기·페이지 정리·페이지 번호·워터마크 등을 무료로 쓸 수 있는 사이트를 만들었습니다.
  >
  > - 대부분의 도구는 pdf.js와 pdf-lib로 **브라우저 안에서만** 처리돼서 파일이 서버로 가지 않습니다.
  > - 압축은 브라우저 모드와 서버(Ghostscript) 모드가 있습니다. 서버 모드는 텍스트가 선명하게 유지되고, 처리 직후 파일을 삭제합니다.
  > - "100KB 이하로 압축"처럼 목표 용량을 정하면, 그 안에 들어가는 가장 좋은 화질을 자동으로 찾아 줍니다. 채용·관공서 사이트 업로드 제한 때문에 만들었습니다.
  > - 가입 없음, 워터마크 없음, 하루 20회 무료
  >
  > 한국어 페이지: https://pdfslimio.com/ko/
  >
  > 써 보시고 결과가 이상한 PDF가 있으면 알려 주세요!

### 디스콰이엇 (한국 메이커 커뮤니티) — https://disquiet.io
- 프로덕트를 등록하고, 위의 GeekNews 본문을 "메이커로그"로 올리세요. 만드는 과정을 꾸준히 올리면 팔로워가 생겨요.

### Reddit r/SideProject — https://www.reddit.com/r/SideProject
자기 프로젝트 소개가 허용되는 곳이에요.
- **Title:** `I made free PDF tools that mostly run in your browser — including "compress to exactly 100KB"`
- **Body:**
  > Job portals and government forms kept rejecting my PDFs for being over 100KB or 200KB, and most compressors just give you "low / medium / high" and hope for the best. So I built a tool that takes a target size and finds the best quality that fits.
  >
  > It's part of SlimIO (https://pdfslimio.com), a free set of PDF tools — merge, split, rotate, reorder with thumbnails, page numbers, watermark, PDF↔JPG. Most of them run entirely in the browser; server compression uses Ghostscript and deletes files right after.
  >
  > No signup, no watermark. Feedback welcome — especially anything confusing.
- 스크린샷 `shot-3-compress-to-100kb.png`를 같이 올리세요.

---

## 3. X (트위터)

**한국어**
> PDF 용량 줄이다가 "100KB 이하만 업로드 가능"에 막힌 적 있나요?
>
> 목표 용량을 고르면 그 안에 들어가는 가장 좋은 화질을 알아서 찾아 주는 도구를 만들었어요.
> 합치기·나누기·페이지 정리·한글 워터마크 등 10가지 도구가 있고, 대부분 브라우저 안에서만 동작해요.
>
> 가입 없음, 워터마크 없음, 무료
> https://pdfslimio.com/ko/compress-pdf-to-100kb.html
>
> 써 보고 불편한 점 알려 주세요 🙏

**English**
> Ever had a form reject your PDF for being over 100KB?
>
> I built a free tool that takes a target size and finds the best quality that fits — plus merge, split, reorder, watermark and more. Most of it runs right in your browser.
>
> No signup, no watermark.
> https://pdfslimio.com
>
> What PDF task annoys you most?

- 스크린샷 `shot-3` 또는 `shot-4`를 붙이면 반응이 훨씬 좋아요.

---

## 4. 질문에 답하면서 알리기 (꾸준히, 하루 1~2개)
"compress pdf to 100kb", "pdf too large to email", "merge pdf without upload" 같은 질문이 Reddit(r/pdf, r/techsupport 등)이나 Quora에 계속 올라와요.
- 먼저 **질문에 실제로 도움이 되는 답**을 쓰세요. 예를 들어 Mac 미리보기의 "Reduce File Size", 스캔할 때 흑백·150dpi로 하기 같은 팁이요.
- 그 다음에 "제가 만든 무료 도구도 있어요: (링크)"라고 **만든 사람임을 밝히고** 한 줄만 덧붙이세요.
- 링크는 질문에 딱 맞는 페이지로 거세요. 100KB 질문이면 `/compress-pdf-to-100kb.html`로요.

---

## 효과 확인
- **Cloudflare → Analytics & Logs → Web Analytics → 방문 → 참조자:** 어디서 들어왔는지(news.ycombinator.com, reddit.com, alternativeto.net 등)
- **같은 화면의 경로:** 어떤 페이지로 들어왔는지
- 올린 날짜를 이 파일 아래에 적어 두면, 나중에 어떤 채널이 효과가 있었는지 비교하기 쉬워요.

| 날짜 | 채널 | 링크 | 결과 |
|---|---|---|---|
| | | | |
