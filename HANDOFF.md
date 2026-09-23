# SlimIO — PDF Compressor · 핸드오프 문서

**최종 업데이트: 2026-09-23** · **상태: ✅ 서비스 LIVE (1 머신, pdfslimio.com 200)**

---

## 👉 다음 세션에서 바로 할 것 (순서대로)
1. **GSC 제출** (검색 트래픽 1순위) — 아래 "⑤ Google Search Console":
   - https://search.google.com/search-console
   - `pdfslimio.com` Domain 추가 → **TXT 인증**(Cloudflare DNS에 GSC가 준 값 추가)
   - 인증 후 **Sitemaps tab → `pdfslimio.com/sitemap.xml` Add & Test**
   - Bing Webmaster 도 동일 (https://www.bing.com/webmasters)
2. **광고 네트워크 가입** — Medvance(0트래픽 승인) 또는 Ezoic → `index.html` `#ad` div의 HTML 주석에 코드 붙임 → 재배포
3. **og-cover.png는 생성됨** (`public/og-cover.png`, 1200×630) — 배포 시 live
4. **Fly token 재발급** — `~/.fly/config.yml`의 `access_token`이 대화에 노출됨
   (Dashboard → API Tokens → 새로 만들되 기존 삭제)
5. **X 홍보 1차** — 개인(1500 팔로워) → `@slimio` 브랜드계 병행 계획. 포스트 초안 아래 있음.

---

## 지금 서비스 상태 (확인됨, 2026-09-23)
| 항목 | 상태 |
|---|---|
| `https://pdfslimio.com` | ✅ **200 LIVE** |
| `https://glowing-meadowbrook-286.fly.dev` | ✅ 200 |
| 머신 수 | ✅ **1개** (7845741b401758, 256MB, ~$2.75/월) |
| 도메인 DNS | ✅ Cloudflare resolve |
| GS 압축 백엔드 | ✅ 동작 확인 (/screen 12% 등) |
| GitHub | ✅ `https://github.com/showboyz/slimio` (trout 브랜치) |
| `og-cover.png` | ✅ 생성됨 (public/og-cover.png, 1200×630) |
| 광고 슬롯 | ⚠️ `#ad` div에 Ezoic/AdSense/Medvance 코드 **자리(HTML 주석)预埋됨**, 실제 네트워크 코드 미삽입 |
| Google Search Console | ❌ 미제출 |
| Fly token | ⚠️ 재발급 필요 (대화에 노출됨) |

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
| `public/index.html` | SlimIO UI + 2모드 압축 로직 |
| `public/robots.txt` | `Sitemap: https://pdfslimio.com/sitemap.xml` |
| `public/sitemap.xml` | `pdfslimio.com/` 1url |
| `server/server.cjs` | 정적+GS+rate-limit 단일 서버 |
| `Dockerfile` | `node:20-slim` + `apt install ghostscript` + `node server/server.cjs` |
| `fly.toml` | app `glowing-meadowbrook-286`, region `sin`, 256MB, `force_https` |
| `worker/*` + `wrangler.toml` | (예전) KV rate-limit worker — **현재 미사용** |
| `.gitignore` | `.wrangler/`, `.dev/`, `node_modules/` 제외 |
| `HANDOFF.md` | 이 문서 |

### ⚠️ 시크릿
- `~/.fly/config.yml`의 `access_token`은 로컬에만, git 안 올라감 ✓
- 그 값이 **이 대화에 노출됨** → **반드시 재발급**

---

## 다음 작업 체크리스트
- [ ] **① GitHub repo 생성 + 푸시** (가장 긴급)
  ```
  cd /Users/home/orca/workspaces/mymy/trout
  git add -A
  git commit -m "SlimIO: production deploy (GS server + static + same-origin, pdfslimio.com)"
  gh repo create slimio --public --source . --push
  ```
- [ ] **② Fly 카드 등록 / 또는 Oracle Always-Free 이관** → 서비스 재기동
- [ ] **③ og-cover.png** (1200×630, "PDF Compressor"). `public/og-cover.png` → `index.html` og:image = `https://pdfslimio.com/og-cover.png`
- [ ] **④ 광고 슬롯预埋**: `index.html` `#ad` div에 Ezoic/Medvance/AdSense. 지금은 "No ads" 문구 + 빈 placeholder
- [ ] **⑤ Google Search Console 제출**: `pdfslimio.com` 등록 → TXT 인증(Cloudflare DNS) → `sitemap.xml` 제출
- [ ] **⑥ (선택) Bing Webmaster Tools**
- [ ] **⑦ (장기) 추가 도구 페이지**: merge/split/pdf-to-jpg → SEO 스케일

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
