# SlimIO — PDF Compressor · 핸드오프 문서

**최종 업데이트: 2026-09-22** · **상태: 🛑 서비스 일시 중단 (Fly 크레딧 소진)**

---

## 🚨 당장 할 것 (순서대로)
1. **Fly 카드 등록** → `https://fly.io/trial`
   - 또는 **Oracle Cloud Always-Free**로 GS 서버 이관 (진짜 $0/월)
2. 카드 등록 후 **머신 재기동/배포**:
   ```
   cd /Users/home/orca/workspaces/mymy/trout
   flyctl deploy --app glowing-meadowbrook-286 --yes
   ```
3. **GitHub repo 생성 + 푸시** (아래 "다음 작업" ①)
4. **Fly token 재발급** — `~/.fly/config.yml`의 `access_token`이 대화에 노출됨
   (Dashboard → API Tokens → 새 토큰 생성 + 기존 삭제)

---

## 지금 서비스 상태
| 항목 | 상태 |
|---|---|
| `https://pdfslimio.com` | ❌ 525 (머신 정지/크레딧 소진) |
| `https://glowing-meadowbrook-286.fly.dev` | ❌ 000 (머신 없음) |
| 도메인 DNS | ✅ Cloudflare로 resolve됨 (A: 104.21.20.250 / 172.67.195.46) |
| GS 압축 백엔드 | ✅ 코드 정상 (머신 부팅 시 동작 확인: /screen 12% 감소 등) |
| GitHub | ✅ `showboyz`로 인증됨, **remote 미설정 / repo 미생성** |
| 광고 슬롯 | ⚠️ `#ad` placeholder div만, 실제 광고 코드 없음 |
| `og-cover.png` | ❌ 미생성 |
| Google Search Console | ❌ 미제출 |

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
