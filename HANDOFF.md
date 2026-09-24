# SlimIO — Free PDF Tools · 핸드오프 문서

**최종 업데이트: 2026-09-24** · **상태: ✅ 서비스 LIVE (1 머신, pdfslimio.com)** · 도구 10개

---

## 👉 다음 세션에서 바로 할 것 (순서대로)
1. **Plausible 목표 설정** (1회): Site Settings → Goals → Custom event `Tool Used` 추가 → Custom Properties에 `tool` 추가
   → 대시보드에서 도구별 **실제 사용 수** 확인 (방문은 Top Pages / Entry Pages / Sources)
2. **GSC**: TXT 인증 레코드는 DNS에 있음 → 인증 완료 후 `sitemap.xml`(10 URL) 제출, 새 페이지 URL 검사로 색인 요청. Bing은 GSC import
3. **X 홍보 1차** — "파일이 기기 밖으로 안 나가는 무료 PDF 도구 모음" 앵글로 (초안 아래)
4. 광고 네트워크는 트래픽 1천+ 이후 (Medvance/Ezoic)
5. 다음 도구 후보: PNG→PDF 랜딩, PDF 암호 걸기/해제(서버 qpdf 필요), Word→PDF

---

## 지금 서비스 상태 (2026-09-24)
| 항목 | 상태 |
|---|---|
| `https://pdfslimio.com` | ✅ LIVE |
| 도구 | Compress(/) · Merge · Split · Remove Pages · Rotate · **Organize** · **Page Numbers** · **Watermark** · PDF→JPG · JPG→PDF |
| Plausible | ✅ 전 페이지 설치 + `Tool Used` 이벤트(props.tool) — 대시보드 Goal 설정 필요 |
| GitHub | ✅ `https://github.com/showboyz/slimio` (trout 브랜치) |
| Fly token | ✅ 재발급 완료 (2026-09-24) |
| Google Search Console | ⚠️ TXT 레코드 추가됨, 사이트맵 제출 필요 |
| 광고 슬롯 | ⚠️ 자리만 있음 |

### 2026-09-24 수정 내역 (중요)
- 도구 페이지 6개 전부 `$ is not defined`로 **작동 안 하던 문제** 수정 (`lib.js`가 전역 `$` export)
- Rotate(`.degrees`→`.angle`), Remove Pages(역순 삭제·Set.filter·버튼 비활성), Merge(`clearError`) 버그 수정
- 다운로드 버튼이 탭을 blob PDF로 이동시키던 문제 수정 (index, merge)
- 서버: 잘못된 URL(`%E0`)로 **프로세스 크래시** → 400 처리, 업로드 50MB 제한(413), 요청 예외 시 500(크래시 방지), X-Level 화이트리스트, 거부된 요청은 횟수 차감 안 함, 날짜 바뀌면 카운터 정리
- `robots.txt` → `text/plain`, 404.html 추가, 도구 페이지 nav `/how`·`/pricing` 404 → `/#how`·`/#pricing` + "All tools"

### 새 도구 추가 체크리스트
`public/<tool>.html` (rotate.html 구조 복사: meta/canonical/og/JSON-LD/FAQ/Plausible) → 모든 페이지 `.tools-row`에 링크 → `index.html` `.tools-grid` 카드 → `sitemap.xml` → `SlimIO.consume()` 호출 시 `Tool Used` 이벤트 자동 전송(pathname 기준)
회전 페이지에 텍스트 그릴 땐 `SlimIO.page2user(page)` 사용
⚠️ **Cloudflare가 .js/.css/.txt를 4시간 캐시함** → `lib.js`/`style.css` 수정 시 HTML의 `?v=` 해시를 갱신:
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
- **GS 10.08.0**: `/screen`(가장 작음), `/ebook`(96dpi 균형), `/printer`, `/prepress`

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
| `public/lib.js` | 공용 헬퍼(`$`, 다운로드, 한도, Plausible `track`, `page2user`) |
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
- **지금은 완전 무료 20회/일 유지** (광고 0원)
- 트래픽 1천+ → Medvance/Ezoic → 1천뷰+ → AdSense
- **Pro $5/월**(무제한/no-ad)은 보조, "Coming soon"으로预埋
- **$5/월 Fly 유지** (24/7 autostart 가치). 256MB 1머신 ~$2.75/월. **머신 1개로 유지**(2개면 4.5/월)

## 벤치마크 (iLovePDF/SmallPDF 반영)
- 네비→히어로→드롭존→3단계→보안배지→가격→푸터
- "무료 대체/비교" + "reduce pdf file size to 2mb" 등 롱테일 = 검색 트래픽 원천

## 알려진 제한
- **Browser mode**: PDJ.js가 `cdnjs` 로드 → 네트워크 필요, text 약간 부드러움
- **Server mode**: `/screen` 72dpi가 34% 축소, `/ebook` 균형(약 5% on test), `/printer` 오히려 커질 수 있음
- **rate-limit**: 메모리 기반이라 재배포 시 초기화 (무료라 OK)
- **모델 이미지 입력 불가** → 스크린샷 못 봄. `#log` 패널 텍스트로 디버깅

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
