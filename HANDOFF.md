# SlimIO — Free PDF Tools · 핸드오프 문서

**최종 업데이트: 2026-09-29** · **상태: ✅ 서비스 LIVE (1 머신, pdfslimio.com)** · 도구 12개 · 47페이지(영·한) · **AdSense 심사 중**

---

## 👉 다음 세션에서 바로 할 것 (순서대로)
1. **AdSense 승인 대기** (2026-09-29 심사 요청, 보통 며칠~2주, 최대 4주. 결과는 Gmail로 옴)
   - 끝난 것: 계정(결제국가 한국) · 결제 정보 입력(사용자) · 메타 태그로 소유권 확인 · 심사 요청 · **EU 동의 메시지 = Google CMP 3선택지**(동의/동의 안 함/옵션 관리, Privacy & messaging에서 변경 가능)
   - 홈 카드 "Connect your site — Required ⚠️"와 Sites의 "Ads.txt: Not found"는 **심사 중이라 뜨는 것, 조치 불필요**. `https://pdfslimio.com/ads.txt`는 200 text/plain으로 정상 확인됨
   - **승인되면:** 전 페이지 head에 `<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5339352429300786" crossorigin="anonymous"></script>` 추가 → `#ad` 자리에 광고 단위 넣기(또는 Auto ads) → `bump_versions.py` → 배포. 이후 "일일 한도 도달 시 광고 보고 +N회" 보상형(공식 rewarded 포맷만) 검토, 그때는 IP 메모리 카운터 보강 필요
   - **거절되면:** 사유(콘텐츠 부족/탐색 문제 등)에 맞춰 보완 후 재신청
2. **모니터링 (1~2주):** Umami(Events → tool-used→downloaded 전환율, target-result의 fits=false 비율, 참조자). 첫 실사용자 2026-09-29: 인도(하이데라바드), google.com → /compress-pdf-to-500kb, Cloudflare Web Analytics, GSC(색인 수·검색어), 네이버 서치어드바이저
3. **사용자 확인할 것:** 다른 계정(네이버 메일 등)에서 `contact@pdfslimio.com`으로 테스트 메일 → Gmail 수신 확인 / 폰에서 `pdfslimio.com/?notrack` 한 번 열기
4. **홍보:** `marketing/PROMO.md` 순서대로 (AlternativeTo·SaaSHub 등록 → Show HN → GeekNews/디스콰이엇 → r/SideProject → X). 올린 날짜를 표에 기록
5. **페이지 추가·수정 후 배포하면** `tools/indexnow.sh` 실행 + GSC·네이버에서 새 URL 색인 요청
   - 2026-09-29: 증명사진·50KB·20KB 6개 GSC 색인 요청 + GSC 사이트맵 재제출, 네이버 `/ko/` 3개 수집 요청 완료 (Claude가 `orca computer`로 Chrome 조작 — 사용자 로그인 세션 사용)
   - 참고: 그날 GSC 개요는 '색인 0 / 미색인 1'로 표시(리포트 지연 가능). 1~2주 뒤 Pages 리포트 확인
6. 다음 개발 후보: PDF 암호 걸기/해제(qpdf), 가이드 글(Mac/iPhone에서 PDF 줄이기 등), 서명 전용 페이지, JPG 크기 줄이기 롱테일 (이미지 50KB/20KB·증명사진 페이지·픽셀 직접 입력은 2026-09-29 완료)

---

## 지금 서비스 상태 (2026-09-29)
| 항목 | 상태 |
|---|---|
| `https://pdfslimio.com` | ✅ LIVE |
| 도구 | Compress(/) · Merge · Split · Remove Pages · Rotate · Organize · Page Numbers · Watermark · PDF→JPG · JPG→PDF · **Sign PDF** · **Compress Image** (2026-09-28 추가) |
| 한국어 사이트 | `/ko/` 아래 19페이지 (hreflang 연결, 사이트맵 38 URL) |
| 롱테일 SEO | `compress-pdf-to-100kb/200kb/500kb/1mb`, `compress-pdf-for-email` (목표 용량 압축, `public/target.js`) |
| 이메일 | `contact@pdfslimio.com` → Cloudflare Email Routing → todays777@gmail.com (수신 전용, 무료). 답장은 Gmail에서 |
| 정책 페이지 | about / terms / privacy / contact (영·한), 전 페이지 하단 링크. AdSense 심사용 |
| AdSense | 게시자 `ca-pub-5339352429300786`, 결제국가 한국. 전 페이지 `google-adsense-account` 메타 태그 + `/ads.txt`. **심사 중(2026-09-29 요청)**, EU 동의 메시지(Google CMP 3선택지) 설정 완료. 승인 후 광고 스크립트/광고 단위를 `#ad` 자리에 넣기 (위 '다음 할 것' 1번) |
| 분석 | **Umami Cloud 무료(Hobby)** (2026-09-29~) — website id `ab53f00a-b92a-4d4d-aaf0-6b5329869de7`, 전 페이지 head. 도구 사용 시 `tool-used` 이벤트(`{tool: "merge" / "ko/sign-pdf" / "compress" …}`, `lib.js`의 `SlimIO.track`). **이벤트 3종**(2026-09-29~): `tool-used`(도구 실행) · `downloaded`(결과 다운로드, `SlimIO.download`·index `#dl`·사진 개별 링크) · `target-result`(용량 목표 페이지만: `{target, fits, method: original/server/raster, inKB, outKB}`) — 새 이벤트는 `SlimIO.event(name, props)`. **`?notrack` 한 번 열면 그 브라우저는 집계 제외**(localStorage `umami.disabled`). Cloudflare Web Analytics도 병행(참조자·Core Web Vitals) |
| GitHub | ✅ `https://github.com/showboyz/slimio` (trout 브랜치) |
| Fly token | ✅ 재발급 완료 (2026-09-24) |
| Google Search Console | ✅ `sc-domain:pdfslimio.com`, 사이트맵 제출·주요 URL 색인 요청 완료 |
| 네이버 서치어드바이저 | ✅ `https://pdfslimio.com` 등록·소유확인(홈 메타 태그)·사이트맵 제출·수집 요청 완료 |
| 광고 슬롯 | ⚠️ `#ad` 자리만 있음 (AdSense 승인 후 채움) |

### 2026-09-24 수정 내역 (중요)
- 도구 페이지 6개 전부 `$ is not defined`로 **작동 안 하던 문제** 수정 (`lib.js`가 전역 `$` export)
- Rotate(`.degrees`→`.angle`), Remove Pages(역순 삭제·Set.filter·버튼 비활성), Merge(`clearError`) 버그 수정
- 다운로드 버튼이 탭을 blob PDF로 이동시키던 문제 수정 (index, merge)
- 서버: 잘못된 URL(`%E0`)로 **프로세스 크래시** → 400 처리, 업로드 50MB 제한(413), 요청 예외 시 500(크래시 방지), X-Level 화이트리스트, 거부된 요청은 횟수 차감 안 함, 날짜 바뀌면 카운터 정리
- `robots.txt` → `text/plain`, 404.html 추가, 도구 페이지 nav `/how`·`/pricing` 404 → `/#how`·`/#pricing` + "All tools"

### 목표 용량 압축 페이지 (롱테일 SEO)
- `public/target.js`: ① 서버 GS(`screen`, 1MB 이상 목표는 `ebook`) → 목표 이하면 끝(텍스트 유지) ② 아니면 브라우저에서 해상도 단계별 래스터화, 각 단계에서 목표에 맞는 최고 JPEG 품질 선택 ③ 못 맞추면 가장 작은 결과 + 안내
- 페이지는 **생성기로 만듦**: `tools/gen_size_pages.py` + `tools/size_template.html` (페이지별 문구·FAQ는 py 안의 `PAGES`)
  ```
  cd public && python3 ../tools/gen_size_pages.py . $(shasum lib.js|cut -c1-8) $(shasum style.css|cut -c1-8) $(shasum target.js|cut -c1-8)
  ```
  새 용량 추가 시 `PAGES`·`SIBLINGS`에 항목 추가 → 재생성 → `index.html` "Need an exact size?" 줄 + `sitemap.xml`
- 페이지마다 쓰임새/팁/FAQ를 실제로 다르게 유지할 것 (복제 페이지는 Google이 스팸 처리)
- `/api/consume`: 차감 **전에** 한도 판단 (이전엔 20번째 사용이 막혔음)

### 성능·운영 (2026-09-25)
- Lighthouse 모바일: 성능 84~100, 접근성·권장사항·SEO 100. 하단 스크립트 `defer` + 페이지 코드 `type="module"` (새 페이지도 이 패턴 유지)
- `?v=` 붙은 자산은 1년 immutable 캐시, `/merge`→`/merge.html`, `/index.html`→`/` 301
- 서버 GS 압축은 **한 번에 1개**, 대기 10개까지, 초과 시 503(브라우저 모드로 폴백), GS 60초 타임아웃 — 256MB 머신 OOM 방지
- IndexNow 키: `public/<32hex>.txt` (삭제 금지)

### 한국어 사이트 (2026-09-25)
- **구조:** 페이지 JS는 전부 `public/js/<page>.js` (영어·한국어 공용). 사용자에게 보이는 문구는 `SlimIO.t("English text")`로 감싸고, 한국어는 `public/i18n/ko.js` 사전에서 가져옴 (`<html lang="ko">`일 때)
- **한국어 페이지는 생성기로 만듦:** `tools/gen_ko.py` — 영어 HTML을 읽어 한국어 텍스트(메타·구조화 데이터·본문·FAQ·UI 라벨)로 바꿔 `public/ko/`에 씀. hreflang·언어 전환 링크·sitemap.xml도 같이 갱신. 영어 페이지를 고치면 다시 실행 (기대한 영어 문구가 없으면 멈추고 알려 줌, 번역 누락도 검사)
- **영어 페이지나 JS를 고친 뒤 순서:**
  ```
  python3 tools/gen_ko.py        # 한국어 페이지 재생성 (+ 사이트맵)
  python3 tools/check_i18n.py    # JS에 새 문구를 넣었다면 ko.js에 번역 있는지 검사
  python3 tools/bump_versions.py # 모든 ?v= 해시 갱신 (JS/CSS 바꿨으면 필수)
  ```
- 워터마크: 영문은 Helvetica 벡터, 그 외 문자(한글 등)는 브라우저가 그린 투명 PNG로 삽입 (fontkit 서브셋은 글자가 깨지는 버그가 있어 안 씀)
- Ghostscript 프리셋 표기 수정: ebook 150dpi, printer 300dpi (이전 96/1200 표기는 틀렸음)

### 사진 용량 줄이기 · PDF 서명 (2026-09-28)
- `compress-image.html` + `js/compress-image.js`: 브라우저 전용. 목표 KB면 JPEG/WebP 품질 이진탐색 → 안 되면 20%씩 축소(증명사진 프리셋은 픽셀 고정이라 축소 안 함). EXIF 방향 반영, 재인코딩으로 EXIF(GPS) 제거. 결과가 원본보다 크고 형식·크기 동일하면 원본 유지(단 EXIF 있는 JPEG는 재인코딩본). HEIC는 브라우저가 못 열면 안내
- `sign-pdf.html` + `js/sign-pdf.js`: 그리기(pointer events, 터치 OK) / 이름(Google Fonts 손글씨·나눔 폰트, **도장** 스타일: 명조 빨간 원, 한글 세로·4자 2×2 우→좌) / 이미지 업로드(흰 배경 투명화). 미리보기에서 드래그·리사이즈, 여러 페이지. 저장 시 `SlimIO.page2user`로 회전 페이지 좌표 변환
- 한글 웹폰트는 unicode-range 조각이라 캔버스에 그리기 전 `document.fonts.load(font, text)` 필수 (`ensureGlyphs`)
- 사진 용량별 롱테일: `compress-image-to-100kb.html`, `-200kb.html` (+ `/ko/`). **생성기** `tools/gen_image_pages.py` (compress-image.html을 바탕으로 목표 용량 미리 선택 + 페이지별 문구·FAQ, "다른 용량" 링크 줄 관리). 한국어 문구는 `gen_ko.py`의 KO[...]. 새 용량 추가: `PAGES`·`SIZE_LINKS`에 항목 → `gen_image_pages.py` → `gen_ko.py`(KO 항목 + PAGES 목록 추가) → `bump_versions.py`
- 향후: "증명사진 용량 줄이기" 전용 페이지 (한국 검색량 큼)
- 2026-09-29: `compress-image-to-50kb`, `-20kb` 추가 (+`/ko/`). 인도 시험·채용 원서(사진 20~50KB, 서명 10~20KB) 수요 겨냥. 20KB 옵션을 `compress-image.html` 목표 목록에 추가
- 2026-09-29: **증명사진 전용 페이지** `compress-id-photo.html` (+`/ko/`, 키워드 "증명사진 용량 줄이기"). 생성기 `PAGES` 항목에 `"resize": "id-3x4"`로 크기 프리셋 미리 선택 가능. gen_ko는 `compress-image*` 또는 `compress-id-photo`를 사진 페이지로 취급(UI 번역 공유)
- 2026-09-29: **픽셀 직접 입력** — 크기 조절 `custom` 옵션 + `#cw`/`#ch`(16~4000px). 프리셋처럼 가운데 기준으로 비율에 맞게 자르고 정확히 그 픽셀로 저장(축소 안 함). 잘못된 값은 횟수 차감 전에 안내
- 2026-09-29: `#log` 디버그 패널은 **`?debug`로 열 때만 표시**(예전엔 오류·홈 압축 결과마다 사용자에게 보였음). 홈 압축은 결과가 원본보다 크면 원본을 돌려줌. 사진 합계 감소율은 최대 −99%로 표시
- **목표 용량은 10진수(1KB=1000B)** — `compress-image.js`·`target.js`의 `parseSize`. 접수 사이트가 어느 정의로 검사해도 통과하도록

### 새 도구 추가 체크리스트
`public/<tool>.html` (rotate.html 구조 복사: meta/canonical/og/JSON-LD/FAQ) → 모든 페이지 `.tools-row`에 링크 → `index.html` `.tools-grid` 카드 → `sitemap.xml` → `SlimIO.consume()` 호출 시 `Tool Used` 이벤트 자동 전송(pathname 기준)
회전 페이지에 텍스트 그릴 땐 `SlimIO.page2user(page)` 사용
⚠️ **Cloudflare가 .js/.css/.txt를 4시간 캐시함** → JS/CSS 수정 시 `python3 tools/bump_versions.py` (아래 명령은 예전 방식, 참고용):
```
cd public && JS=$(shasum lib.js|cut -c1-8) CSS=$(shasum style.css|cut -c1-8) && for f in *.html; do sed -i '' -E "s#/lib\.js(\?v=[a-z0-9]+)?\"#/lib.js?v=$JS\"#g; s#/style\.css(\?v=[a-z0-9]+)?\"#/style.css?v=$CSS\"#g" "$f"; done
```
robots.txt·sitemap.xml 변경은 Cloudflare 대시보드 → Caching → Purge 로 즉시 반영

---

## 아키텍처 (배포 후 same-origin)
```
사용자 → pdfslimio.com (Cloudflare DNS) → glowing-meadowbrook-286.fly.dev (Fly, GS 서버)
```
- **단일 Node 프로세스** (`server/server.cjs`)가 정적 서빙 + GS 압축 + rate-limit 전부 처리
- `index.html`의 `API_BASE`/`SERVER_BASE` = `""` (same-origin)
- 포트 3001, `force_https`
- **rate-limit**: IP당 하루 20회, 서버 메모리 `Map`에 저장 (재시작/재배포 시 초기화 — 무료라 OK)
- **GS 10.08.0**: `/screen`(가장 작음), `/ebook`(150dpi 균형), `/printer`, `/prepress`

### 두 압축 모드
1. **Browser mode**: pdf.js + pdf-lib, 파일 안 나옴. Quality/Resolution 슬라이더. CDN `cdnjs` pdf.js 3.11.174 + pdf-lib 1.17.1
2. **Server mode**: `POST /api/compress`, `X-Level` 헤더로 GS preset → base64 PDF 반환

### 엔드포인트
- `GET /` 정적 (index.html / robots.txt / sitemap.xml)
- `GET /api/check` → `{ok, remaining, limit:20}`
- `POST /api/consume` → 카운트 +1
- `POST /api/compress` (body=PDF, `X-Level` 헤더) → `{ok, inBytes, outBytes, savedPct, remaining, limit, pdf(base64)}`
- `429` = 일일 한도 초과

---

## 파일 목록
| 파일 | 설명 |
|---|---|
| `public/index.html` | 메인 압축 UI + 2모드 압축 로직 + 도구 그리드 |
| `public/*.html` | 도구 페이지 9개 + `404.html` |
| `public/lib.js` | 공용 헬퍼(`$`, `t()` 번역, 다운로드, 한도, `page2user`) |
| `public/style.css` | 도구 페이지 공용 스타일 |
| `public/robots.txt` | `Sitemap: https://pdfslimio.com/sitemap.xml` |
| `public/sitemap.xml` | 10 URL |
| `server/server.cjs` | 정적+GS+rate-limit 단일 서버 |
| `Dockerfile` | `node:20-slim` + `apt install ghostscript` + `node server/server.cjs` |
| `fly.toml` | app `glowing-meadowbrook-286`, region `sin`, 256MB, `force_https` |
| `worker/*` + `wrangler.toml` | (예전) KV rate-limit worker — **현재 미사용** |
| `.gitignore` | `.wrangler/`, `.dev/`, `node_modules/` 제외 |
| `HANDOFF.md` | 이 문서 |

### ⚠️ 시크릿
- `~/.fly/config.yml`의 `access_token`은 로컬에만, git 안 올라감 ✓
- 2026-09-24 재발급 완료

---

## 수익화 전략 (결정됨)
- **지금은 완전 무료 20회/일 유지**
- 2026-09-29 AdSense 바로 신청함(심사 중). 승인되면 광고 게재, 이후 보상형 광고로 한도 추가 검토
- **Pro $5/월**(무제한/no-ad)은 보조, "Coming soon"으로预埋
- **$5/월 Fly 유지** (24/7 autostart 가치). 256MB 1머신 ~$2.75/월. **머신 1개로 유지**(2개면 4.5/월)

## 벤치마크 (iLovePDF/SmallPDF 반영)
- 네비→히어로→드롭존→3단계→보안배지→가격→푸터
- "무료 대체/비교" + "reduce pdf file size to 2mb" 등 롱테일 = 검색 트래픽 원천

## 알려진 제한
- **Browser mode**: PDJ.js가 `cdnjs` 로드 → 네트워크 필요, text 약간 부드러움
- **Server mode**: `/screen` 72dpi가 34% 축소, `/ebook` 균형(약 5% on test), `/printer` 오히려 커질 수 있음
- **rate-limit**: 메모리 기반이라 재배포 시 초기화 (무료라 OK)
- 디버깅: 아무 페이지나 `?debug`를 붙여 열면 `#log` 패널 표시. (이제 모델이 스크린샷을 읽을 수 있음 — Umami 분석도 캡처로)

## 로컬 실행
```
cd /Users/home/orca/workspaces/mymy/trout
node server/server.cjs        # http://127.0.0.1:3001 (정적+GS)
# 정적만: python3 -m http.server 8000 --directory public
```

## X 홍보 + 피드백 (1500 팔로워 활용)
- **전략**: 개인계(1500) 1차 홍보 → `@slimio` 신규 브랜드계 병행(장기 자산/광고 전용, 이탈 방지)
- **피드백 채널**: X 리플/DM(1순위) + Google Form 1개(수집용)
- **X 첫 포스트 초안**(질문 포함 → 리플↑):
    > I built a free PDF compressor that runs **in your browser** so your files never leave your device. No signup, no install.
    > https://pdfslimio.com
    > (server mode keeps text sharp via Ghostscript)
    > — what PDF tools do you actually rely on? /feedback welcome 🐟
- **Product Hunt**(해당 1~2개월 후, 1회성 500–2000 트래픽, "프라이버시: 파일 안 나옴" 앵글)

## SEO/수익화 (결정)
- 검색 트래픽 = GSC 제출 **+ 롱테일 페이지** (merge/split/pdf-to-jpg 추가, "free ilovepdf alternative" 등)
- 광고: 트래픽 1천+ → Medvance/Ezoic → 1천뷰+ → AdSense. Pro $5/월(aux).
- 지금 무료 20회/일 유지.
