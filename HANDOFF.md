# SlimIO — Free PDF Tools · 핸드오프 문서

**최종 업데이트: 2026-09-29** · **상태: ✅ 서비스 LIVE (1 머신, pdfslimio.com)** · 도구 12개 · 47페이지(영·한) · **AdSense 심사 중**

---

> **작업 위치 변경 (2026-10-02):** 예전 `workspaces/mymy/trout` 폴더는 Orca 정리 중 삭제됨. 이제 **`~/orca/projects/slimio`** (GitHub `showboyz/slimio`, `trout` 브랜치)에서 작업. 배포는 여기서 `fly deploy --ha=false`.

## 👉 다음 세션에서 바로 할 것 (순서대로)
1. **AdSense 승인 대기** (2026-09-29 심사 요청, 보통 며칠~2주, 최대 4주. 결과는 Gmail로 옴)
   - 끝난 것: 계정(결제국가 한국) · 결제 정보 입력(사용자) · 메타 태그로 소유권 확인 · 심사 요청 · **EU 동의 메시지 = Google CMP 3선택지**(동의/동의 안 함/옵션 관리, Privacy & messaging에서 변경 가능)
   - 홈 카드 "Connect your site — Required ⚠️"와 Sites의 "Ads.txt: Not found"는 **심사 중이라 뜨는 것, 조치 불필요**. `https://pdfslimio.com/ads.txt`는 200 text/plain으로 정상 확인됨
   - **승인되면:** 전 페이지 head에 `<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5339352429300786" crossorigin="anonymous"></script>` 추가 → `#ad` 자리에 광고 단위 넣기(또는 Auto ads) → `bump_versions.py` → 배포. 이후 "일일 한도 도달 시 광고 보고 +N회" 보상형(공식 rewarded 포맷만) 검토, 그때는 IP 메모리 카운터 보강 필요
   - **거절되면:** 사유(콘텐츠 부족/탐색 문제 등)에 맞춰 보완 후 재신청
2. **모니터링 (1~2주):** Umami(Events → tool-used→downloaded 전환율, target-result의 fits=false 비율, 참조자). 첫 실사용자 2026-09-29: 인도(하이데라바드), google.com → /compress-pdf-to-500kb, Cloudflare Web Analytics, GSC(색인 수·검색어), 네이버 서치어드바이저
2-1. **네이버 유입 (2026-10-07 분석):** 30일간 네이버 검색 유입 6명(전부 10/5~7, 한국, PC 4·모바일 2). 랜딩: /ko/compress-id-photo 3, /ko/signature-image 1, /ko/compress-image-to-50kb 1, /ko/compress-pdf-to-50kb 1. 종로구 PC 사용자가 증명사진 페이지에서 12분, 다운로드 2회. 서치어드바이저 키워드는 /ko/sign-pdf의 도장 관련("pdf에 도장넣는 무료", "pdf에 직인 넣기", "이름도장pdf"). 티스토리 블로그 유입은 네이버가 아니라 다음 검색. Umami에서 보는 법: `…/sessions?date=30day&referrer=c.naver`, Breakdown에서 Fields → Referrer 추가. **후속 조치:** 증명사진에 시험 원서 프리셋(`kr-qnet` 300×400·200KB / `kr-gosi` 137×177·100KB / `kr-history` 120×160·100KB, compress-image.js의 `PRESET_TARGET`), 한국어 페이지에만 칩 줄 `.exams`(gen_ko ui_extra), `?resize=kr-qnet` 링크, specs.js 한국어(이하/미만/이상·가로/세로·픽셀·㎝), ko/sign-pdf 제목을 "PDF 도장 넣기·서명 넣기"로. 경쟁: mirifit.com, yeiid.itbrown.com (시험별 규격 페이지 운영) **2026-10-11 재확인(최근 7일, 한국):** 방문자 23명(전주 대비 +360%), 유입 네이버 PC 11·모바일 9·티스토리 1(구글 거의 0). 랜딩 증명사진 11, 50KB 3, 200KB 2, 홈 2. 도구 실행 25·파일 추가 20·다운로드 16, 실행 대부분 ko/compress-id-photo. 브라우저 Chrome 7·Edge 5·iOS 4·**Chrome webview 3(네이버 앱 안 브라우저 추정 — 다운로드 동작 미검증)**·Samsung 3. error 이벤트 0건(10/11 배포라 아직 판단 이르다) **2026-10-12 재확인(최근 7일, 한국):** 방문자 34명(전주 5명), 하루 방문자 10/10 6·10/11 5·10/12 10(최고). 유입 네이버 29/31(PC 15·모바일 14)·티스토리 2, 구글 0. 랜딩 증명사진 17(50%), 50KB 4, 홈 3. 이탈률 31%. 이벤트 사용자 24명: 도구 실행 38·파일 추가 30·다운로드 20. 브라우저 Chrome 9·Edge 8·**Chrome webview 7(21%)**·iOS 6·Samsung 3. 최근 24시간 전체 18명 중 한국 11·인도 7(/signature-image). error 2건: ① `__naverapp__.getElementFromPoint is not a function`(iOS 네이버 앱이 넣는 스크립트 — 우리 코드 아님) ② ko/compress-pdf-to-300kb에서 'PDF 파일을 선택해 주세요'(PDF 용량 페이지에 사진을 넣은 듯 — 사진 페이지로 안내할 여지) **2026-10-13 16시 재확인(최근 7일):** 전체 방문자 89명(+34%), 유입 네이버 43(PC 24·모바일 19, 전주 1명)·구글 35(google.com 23 + 안드로이드 구글 앱 12, 대부분 인도 /signature-image 37명)·티스토리 2. 네이버 하루 방문자 10/10 5·10/11 3·10/12 9·10/13 15(16시 기준, 최고). 네이버 랜딩: 증명사진 21(50%)·원서 사진 가이드 6·50KB 5·200KB 3·서명 이미지 2·여권/비자 가이드 각 1. 네이버 방문자 43명 중 27명(63%)이 이벤트: 도구 실행 49·파일 추가 31·다운로드 31. 다운로드 중 `app=naver` 5건(10/12 배포 이후, 네이버 앱 안에서도 저장 버튼 누름). error는 10/12 두 건뿐(수정 배포 전), 새 오류 없음. 서버 사용(/api/stats) 10/13 16시 기기 10대 19회
2-2. **GSC 분석 (2026-10-08, 데이터는 10/5까지):** 클릭 37·노출 691, 인도 36클릭. signature-image 185노출·평균 2.6위·CTR 18%(클릭 대부분). PDF 용량 페이지(500KB 130·1MB 137·100KB 146·200KB 45노출)는 70~80위. 8~20위 구간은 거의 없음(사이트가 2주 차). 조치: 모든 도구 페이지 '다른 무료 도구'에 용량 링크 줄(`.sizes`, gen_related.py `SIZE_LINKS_*`), 서명 페이지 본문에 서류 PDF 100/200/500KB·1MB 링크, signature-image 색인 재요청. 색인: 40개 indexed / 24개 not indexed(원인 미확인). 다음: 인도 시험별(SSC·UPSC·NEET·RRB) 사진·서명 페이지
2-3. **애드센스 거절 (2026-10-07, 'Low value content')** → 대응: 사이트 안에 가이드 글(`/guides/`, `/ko/guides/`). 원본은 `content/guides/<en|ko>/<slug>.html`(첫 줄 HTML 주석에 JSON 메타: title·seo_title·desc·published·updated·image·cta·faq), `tools/gen_guides.py`가 페이지·허브·모든 페이지 푸터 '가이드' 링크 생성. 생성 순서: `gen_size_pages → gen_image_pages → gen_guides → gen_ko → gen_llms → bump_versions` (사이트맵·llms.txt에 가이드 자동 포함). 2026-10-09 글 6개: EN 인도 시험 사진·서명(RRB CEN 06/2026 서명 30~49KB 등, 출처 포함)·PDF 무손실 압축·KB/픽셀/cm/DPI·서명 이미지, KO 원서 사진 규격 총정리(공무원 350KB 미만 공식 확인)·PDF 압축 원리. 서명 프리셋 추가 `rrb-sign/ssc-sign/upsc-sign/neet-sign`(목록에 없는 KB 범위는 직접 입력칸으로), 사진 `upsc-photo`. **재심사 요청은 약 3~4주 뒤(11월 초)**. 2026-10-09 보강 완료: 소개(누가·파일 처리·규격 확인 방법·오픈소스·**업데이트 기록** — 새 기능 낼 때마다 about.html·ko/about.html 기록에 한 줄 추가), 문의(제보 요령·규격 수정 요청), 개인정보처리방침 모드 이름 갱신, 얇은 도구 8개(PDF↔JPG·나누기·회전·순서·삭제·워터마크·쪽번호)에 설명 추가(영어 ~400~480단어, PDF↔JPG는 FAQ 신설). 초기 Ezoic 광고 주석(가짜 npm 주소 `@ezoic/ezic`) 전부 삭제. 2026-10-09 가이드 2개 추가: EN `us-visa-photo-requirements`, KO `us-visa-photo-size`(국무부 규정을 픽셀로 환산, 압축률 20:1 → 600×600은 54~240KB, 5×5cm 300dpi 스캔=591px로 미달, 업로드 실패 시 X 표시→인화 사진 지참, 주한미국대사관 5×5cm 지참 안내). 같이 고친 것: `us-visa` 프리셋은 결과가 54KB 미만이면 화질을 0.96/0.99/1로 올려 20:1 이하로 저장(목표 용량은 넘지 않음; 매끈한 샘플 39KB→58KB). `.table-wrap` 최소 너비 560px는 4열 이상 표에만 적용(모바일에서 2~3열 표가 화면에 맞음). **가이드 누적 11개(10/11 기준) — 다음 후보: 인도 RRB 단독 글은 india 가이드와 겹쳐서 보류, 대신 다른 주제**
2-4. **GSC 미색인 24개 원인 (2026-10-11 확인, 데이터는 10/4까지):** 22개는 'Discovered – currently not indexed'(9/22 사이트맵으로 발견했지만 아직 한 번도 크롤링 안 함 — 새 사이트의 크롤링 우선순위 문제, 기술 오류 아님: 22개 모두 200·자기 canonical·noindex 없음·사이트맵 포함). 대상: EN 2mb·300kb·50kb·sign-pdf·jpg-to-pdf·rotate·privacy·terms·contact, KO 1mb·2mb·300kb·50kb·sign-pdf·jpg-to-pdf·merge·pdf-to-jpg·split·rotate·privacy·terms·contact. 1개 'Crawled – not indexed' `/ko/compress-image-to-200kb.html`(9/29 크롤링), 1개 'Page with redirect' `http://pdfslimio.com/`(정상). **가이드 10개(10/9 발행)는 GSC에 'URL is unknown to Google'**(사이트맵을 그 뒤로 다시 안 읽음). 조치: 사이트맵 lastmod가 매 빌드마다 전 페이지 '오늘'로 찍혀 구글이 무시하던 것을 수정 — `tools/lastmod.py`가 페이지 본문(제목·설명·본문 텍스트, nav·'More free tools'·'More guides'·footer·script 제외) 해시가 바뀐 날만 기록(`tools/lastmod.json`, gen_ko가 사이트맵 쓸 때 갱신, `python3 tools/lastmod.py`로 git 기록에서 재구성). GSC 사이트맵 재제출(10/11, 마지막으로 읽은 날 10/10·73개). **10/11 색인 요청 완료 13개:** 가이드 9개(EN 미국 비자·인도 시험·KB/DPI·PDF 무손실·`/guides/`, KO 원서 사진·미국 비자·PDF 압축 원리·`/ko/guides/`; 서명 가이드는 이미 색인됨), compress-pdf-to-300kb·sign-pdf·ko/compress-pdf-to-1mb·ko/merge. **다음 날 할 것(한도 초과로 못 함/결과 불확실):** 새 가이드 `/guides/reduce-pdf-size-iphone-mac.html`·`/ko/guides/iphone-mac-pdf-size.html`·`/ko/guides/passport-photo-online.html`, compress-pdf-to-50kb·2mb, jpg-to-pdf, rotate, ko/sign-pdf, ko/pdf-to-jpg, ko/compress-pdf-to-2mb·300kb·50kb, ko/jpg-to-pdf·split·rotate, ko/compress-image-to-200kb. privacy·terms·contact는 요청 불필요. 1~2주 뒤 Pages 리포트 재확인. `tools/__pycache__`는 이제 gitignore
2-5. **2026-10-11 가이드 2개 + 서버 Ghostscript 업그레이드:** EN `reduce-pdf-size-iphone-mac`, KO `iphone-mac-pdf-size` — 같은 PDF 3개(휴대폰 사진처럼 만든 서류 3쪽 7.4MB/한글판 7.1MB, 휴대폰 캡처 3장 655KB, 글자 보고서 61KB/한글판 101KB)로 맥 미리보기 '파일 크기 줄이기'(Quartz 필터, macOS 27 설정: 144ppi·최대 2400px·JPEG 0.7), 단축어 'PDF 파일 크기 최적화'(`is.workflow.actions.compresspdf`, 세 파일 모두 변화 없음), SlimIO 비교. 발견: 미리보기 필터는 글자 PDF를 키움(영어 61→122KB, 한글 101→667KB + **한글을 선 모양으로 바꿔 복사·검색 불가**). **서버 버그 수정:** Debian bookworm의 Ghostscript 10.0.0이 한글 PDF 텍스트 레이어를 깨뜨림(복사 시 '작성'→'Ø성', '가입자가'→'가입×가'). Dockerfile `node:20-slim` → `node:22-trixie-slim`(gs 10.05.1)로 해결, 글자 PDF도 더 작아짐(한글 101→58KB, 예전 76KB). 시험 샘플·스크립트는 세션 스크래치패드(pdftest)에만 있음. 한국어 홈 설명·FAQ의 옛 '브라우저 모드=페이지를 이미지로' 문구를 '선명하게/기기 안에서만'에 맞게 수정. 소개 페이지 업데이트 기록에 10/11 줄 추가. 네이버 수집 요청 완료: /ko/guides/iphone-mac-pdf-size.html, /ko/guides/us-visa-photo-size.html, /ko/guides/, /ko/. GSC 색인 요청은 한도 초과로 다음 날(아래 목록 + 새 가이드 2개)
2-6. **오류 기록·자동 점검 (2026-10-11):** (1) Umami `error` 이벤트 — `SlimIO.reportError(kind, msg)`(lib.js). kind: `shown`(사용자에게 보인 오류 문구, showError가 자동 전송) · `fallback`(서버 압축 실패→브라우저 대체, compress.js·target.js) · `js`/`promise`(잡히지 않은 스크립트 오류, 확장 프로그램 오류·ResizeObserver 제외). 따옴표 안(파일 이름)은 지우고 140자, 페이지당 최대 5개. 개인정보처리방침(EN/KO)에 명시. Umami → Events → `error`에서 tool·kind·msg로 확인. (2) **`npm test`** (`tests/e2e.mjs`, playwright-core + Chrome + gs) — 자체 서버(:3099, 한도 해제)를 띄워 모든 도구를 EN/KO로 실행하고 결과 검증(PDF 쪽수·한글/영어 텍스트 보존·회전·ZIP 개수·이미지 픽셀·KB 범위, 사진 프리셋 8종·서명 프리셋 7종·용량 페이지 전부, 서버 장애 시 브라우저 대체, 깨진 PDF 안내) + 사이트맵 75쪽을 휴대폰 폭으로 열어 스크립트 오류·실패 요청·가로 스크롤·내부 링크 확인. 약 3분. `-- --mobile`(휴대폰 크기로 도구 실행), `-- merge sign`(이름 필터), `-- --pages`. **배포 전 `npm test`, 배포 후 `npm test -- --live`**(실사이트 서버 압축 3건 + 페이지 점검; Ghostscript 버전처럼 서버 환경 문제는 --live만 잡음). 첫 실행 결과 도구 94개·페이지 75개 모두 통과(워터마크 한글은 설계상 이미지로 그려짐 확인)
2-7. **여권 재발급 사진 가이드 (2026-10-11):** 한국 유입이 '네이버 검색 → 증명사진'이라 그 옆 주제로 KO 가이드 `/ko/guides/passport-photo-online.html`(외교부 온라인용 사진파일 안내: JPG/JPEG 500KB 이하, 413×531 권장·가로 395~431·세로 507~550만 업로드, 300dpi 권장 / 여권 사진 규정: 머리 길이 = **머리카락 제외** 정수리~턱 3.2~3.6cm / 정부24: 품질·안면비교 24시간 10회 실패 시 접수 제한, 휴대폰 사진은 규격 맞을 때만). 이미지 `passport-hero/frame-ko/result-ko.jpg`(예시 인물 visa-src.jpg, 1.75배 확대). 도구 수정: 여권(3.5×4.5) 규격의 얼굴 타원을 규정 머리 길이에 맞춤(`GUIDES.passport` cy 0.48·ry 0.378 ≈ 34mm, 기본 타원은 66%라 여권엔 머리가 작게 잘렸음) + 전용 안내 문구. 원서 사진 가이드 표에 여권 500KB 추가. 운전면허 온라인 사진 파일 규격(자주 인용되는 JPG 250KB·350×450)은 공식 확인 못 해서 글에 숫자 안 씀. 네이버 수집 요청 3건 완료(새 가이드·ko/compress-id-photo·원서 가이드). 티스토리 #7 → https://ddoua.tistory.com/15
2-8. **휴대폰 점검·수정 (2026-10-12):** 계기: Umami에서 네이버 앱(Android 웹뷰) 방문자가 /ko/compress-id-photo에서 4번 변환하고 `downloaded` 없이 나감. 휴대폰 크기 점검 결과 **모든 도구**가 버튼을 화면 아래쪽에서 누르면 결과가 화면 밖에 뜨고(자동 스크롤 없음) 다운로드가 작은 글씨 링크였음 → (1) `SlimIO.reveal(result)`(lib.js): 결과를 화면 안으로 스크롤 + 깜빡임(다시 돌려도 새 결과인 걸 알 수 있게), 모든 도구 showResult 끝에서 호출 (2) `.result a.dl` = 큰 초록 버튼(홈 index.html은 style.css를 안 써서 인라인 CSS에 같은 규칙) — 사진 1장일 때도 버튼 (3) **앱 안 브라우저**(UA: NAVER(inapp·KAKAOTALK·DaumApps·Instagram·FB·Line·`; wv)`) 결과 아래 안내 + 'Chrome으로 열기'(Android `intent://…;package=com.android.chrome`), 카카오톡은 `kakaotalk://web/openExternal`, iOS는 ⋯ 메뉴 안내. 이유: 안드로이드 웹뷰는 blob: 다운로드를 못 받는 경우가 많음(카카오톡은 실패 사례 확인, 네이버 앱은 미확인) (4) 터치 화면: 입력칸·선택칸 16px(iOS는 16px 미만이면 확대됨), ▲▼✕·←↻✕→·색 버튼 40px, PDF 서명 핸들 터치 영역 확대 (5) 정리 도구 'Page n' 영어 노출, 나누기 'Download ZIP' 번역 누락 수정. **새 Umami 이벤트:** `downloaded`에 `app`(앱 안 브라우저일 때), `open-browser`(Chrome으로 열기 누름), `held-image`(결과 사진 길게 누름 — Android만 잡힘). `npm test -- --mobile`이 이제 '버튼을 화면 맨 아래에서 눌러도 다운로드 버튼이 화면 안에 보이는지' 검사. 터치 드래그(증명사진 틀·서명 패드·PDF 서명 이동/크기)는 정상 확인. **2026-10-12 사용자 폰 확인: 아이폰 네이버 앱 안에서 증명사진 다운로드 정상** — 안드로이드 네이버 앱(Umami 'Chrome (webview)')은 미확인. 30일간 webview 세션 7개: 보기만 3, 실행 후 다운로드 2(10/8 200KB 1회, 10/11 22:51 증명사진 2회), 실행만 하고 나감 2(10/12 07:43 4회·08:49 1회 — 둘 다 수정 배포 전이라 결과가 화면 밖이었을 가능성) → 서버 경유 다운로드는 보류. 안내 문구는 일단 유지하고, 1~2주 뒤 Umami `downloaded`의 `app=naver` 비율이 다른 브라우저와 비슷하면 네이버 앱에서는 안내를 빼도 됨. 카카오톡 등 다른 앱에서 실패가 보이면 그때 서버를 거쳐 받는 다운로드(Content-Disposition, 앱 안 브라우저만, 개인정보 문구 수정 필요) 검토
2-9. **2026-10-12 오후:** (1) GSC 색인 요청 11건: ko/guides/passport-photo-online · ko/guides/iphone-mac-pdf-size · guides/reduce-pdf-size-iphone-mac · ko/sign-pdf · ko/compress-pdf-to-300kb · ko/compress-pdf-to-50kb · ko/compress-image-to-200kb · ko/jpg-to-pdf · ko/pdf-to-jpg · ko/split · ko/rotate(모두 '미색인' 상태였음). **내일 할 것:** ko/compress-pdf-to-2mb(라이브 테스트가 안 끝나 미확인), compress-pdf-to-50kb · compress-pdf-to-2mb · jpg-to-pdf · rotate(EN, 한도 초과로 못 함) → **2026-10-13 16시:** ko/guides/resume-photo-size 요청 완료, ko/compress-id-photo는 이미 색인됨(건너뜀), 그다음 바로 Quota Exceeded(전날 오후에 13건 써서 한도가 아직 안 찬 듯). **남은 것:** compress-pdf-to-50kb · compress-pdf-to-2mb · jpg-to-pdf · rotate(EN), ko/compress-pdf-to-2mb (2) PDF 도구에 사진을 넣으면 오류 문구 + 사진 도구 링크(`SlimIO.notPdf`: 압축·용량 페이지는 `compress-image.html?target=300KB`처럼 같은 용량, 나머지는 jpg-to-pdf). Umami error 메시지가 'PDF가 아니라 사진 파일이에요…'로 바뀌어서 사진을 넣은 경우만 따로 셀 수 있음 (3) `SlimIO.isPdf`: type이 비었거나 application/octet-stream이어도 이름이 .pdf면 받음(앱이 이렇게 넘기는 경우 대비) (4) 아이폰 네이버 앱에서는 앱 안 브라우저 안내 숨김(사용자 폰에서 저장 확인). 테스트: 사진 넣기 4페이지×EN/KO, octet-stream PDF (5) 네이버 서치어드바이저 수집 요청(2026-10-12): pdfslimio `/ko/guides/resume-photo-size.html`·`/ko/compress-id-photo.html`, 블로그 `ddoua.tistory.com/16` — 캡차 없음 **10/14 오전:** GSC 색인 요청 8건 완료 — ko/guides/computer-certificate-photo-size · guides/ugc-net-photo-signature-size · ko/guides/exam-application-photo-size · compress-pdf-to-50kb · compress-pdf-to-2mb · ko/compress-pdf-to-2mb · jpg-to-pdf · ko/jpg-to-pdf (rotate·india 가이드는 이미 색인됨, 할당량 초과 없음). 네이버 수집 요청 4건: pdfslimio ko 컴활 가이드·ko/compress-id-photo·ko 원서 가이드 + 블로그 /17. 남은 것: compress-id-photo(EN, 10/13 제목 변경) 재요청은 선택
2-10. **이력서 사진 (2026-10-12):** 프리셋 `kr-jobkorea` 103×132 · `kr-saramin` 100×140(compress-image.js `PRESETS`, 용량 목표 없음 — 제한이 5MB/10MB라서). 근거: 잡코리아 고객센터 FAQ '이력서에 사진이 등록되지 않습니다'(150×210px 초과 시 등록 안 됨, gif·jpg·jpeg·png, 5MB) + 잡코리아 사진 크기 조정 도구(103×132 권장), 사람인 도움말 idx=524(10MB, jpg·gif, 권장 100×140), 커리어 도구 기본값 300×400. 한국어 증명사진 페이지에 '이력서' 칩 줄(gen_ko ui_extra)과 본문 섹션, KO 가이드 `/ko/guides/resume-photo-size.html`(이미지 resume-hero.jpg·resume-chips-ko.jpg, 스크립트는 스크래치패드 resumeblog.mjs/resumehero.mjs), 티스토리 #8. 알바천국·고용24·주민등록증 온라인 파일 규격은 공식 숫자를 못 찾아 안 씀. **GSC 색인 요청은 아직(10/12 한도 소진)** — 내일 2-9 목록과 같이. 다음 후보: Umami에서 kr-jobkorea/kr-saramin 사용 여부(`?resize=` 링크·칩) 확인 후, 반응 있으면 공공기관 채용(잡알리오) 등 확장
2-11. **다음 후보 리서치 (2026-10-13):** 방향 = 편의성보다 '서류 사진·업로드 규격' 주제 확장(검색 유입은 걸리는 검색어 수로 늘어남). **데이터:** GSC 28일(9/21~10/10) 클릭 47·노출 1.04K, 클릭 44가 /signature-image(평균 2.65위, CTR 16.5%), 국가 India 44. 인도 사용자는 **원서 안내문을 통째로 구글에 붙여 넣음**("width 140px,height 110px. image should not exceed 50kb. (jpg format)", "should be between 30kb to 49kb", "aspect ratio of signature (height : width) = 1 : r, r between 2.75 and 3.75 … 3 kb and 300 kb") → 제목의 "Paste Your Form's Rules"가 먹히는 듯. specs.js는 이 문장들의 KB·px·jpg는 다 읽지만 **'1 : r' 비율은 못 읽음**. PDF 용량 페이지(500kb·1mb·100kb)는 노출만 많고 60~80위. 네이버 서치어드바이저 리포트는 웹문서만 잡혀서(30일 노출 51, 전부 /ko/sign-pdf 도장·서명 검색어, 'pdf도장지우기' 포함) 증명사진 유입은 안 보임 → 네이버는 Umami가 기준. **후보(추천 순):** ① **UGC NET Dec 2026(EN)** — 접수 10/8~10/28(지연 10/31), 사진 10–200KB·서명 10–50KB·장애증명 PDF 50–300KB, 라이브 사진 별도(정보 공보 08.10.2026 직접 확인: cdnbbsr.s3waas.gov.in/s301eee509ee2f68dc6014898c309e86bf/uploads/2026/10/202610081852912625.pdf). Testbook·Adda247은 서명 4–30KB(옛 숫자) ② EN 증명사진 페이지를 서명 페이지처럼 'paste your form's rules' 제목·설명으로 + specs.js '1:r' 비율 ③ **JEE Main 2027(EN)** — 접수 10월 말 예상(미발표), 2026 공보 기준 사진 10–200KB·서명 10–100KB(공보 안 화면은 서명 10–50KB → 10–50KB 권장), 10학년 PDF 50–300KB ④ **컴활 원서 사진(KO)** — 대한상공회의소: 400×500px로 바뀜, 1:1.25 비율(공지 num=245386), 업로드 창 "파일은 50kbyte를 초과할 수 없습니다"(registerMyImage_popup.do, 직접 확인). 문서딱은 '용량 안내 없음' ⑤ **JPG→PDF 목표 용량**(도구 기능, "jpg to pdf under 200kb/100kb" 자동완성 강함) ⑥ **인도 e-Visa 사진·여권 PDF(KO+EN)** — 사진 JPEG 10KB–1MB 정사각형, 여권 신원면 PDF 10–300KB(indianvisaonline.gov.in/evisa/tvoa.html), 최소 10KB 주의. 베트남 e-Visa 4×6cm·JPG·2MB 미만(evisa.gov.vn/instruction) ⑦ **TEPS·어학시험 사진 모음(KO)** — TEPS 3×4cm(126×165px)·50KB 이하 JPG, 토익스피킹 3×4·6MB 이하, JLPT 1MB 이하(12/6 시험 사진 변경 10/18 마감) ⑧ **India Post GDS(EN)** — 1~2월 예상, 새 공고: 사진 30–100KB·320×400, 서명 20–100KB·300×120(옛 팝업은 50KB/20KB라 혼란). **지켜볼 것:** SSC GD 2027(공고 늦음, 서명 10–20KB), CUET UG 2027(1월, 사진 10–200KB·서명 10–50KB), 중국 비자(한국인 무비자 2026-12-31 종료 예정 — 연장 안 되면 1월 수요), 경찰·소방(12~2월, 특정직 137×177·10MB 미만 — kr-gosi로 처리). **뺀 것:** 대학 정시 원서(진학사·유웨이가 업로드 화면에서 자동 크기 조절 + 자동완성 약함), 국가장학금·정부24·홈택스(공식 용량 숫자 없음), PAN(경쟁 심함, Protean 공식: 사진 3.5×2.5cm 200DPI 20KB 이하·서명 2×4.5cm 10KB 이하), GATE·CAT·CTET(접수 끝남). **경쟁:** 문서딱(docttak.com)이 9/30~10/12에 출처 달린 한국어 가이드 40여 개(경찰·공무원·국시원·대입·컴활·TEPS·JLPT·국가장학금…) → 범위 말고 정확도로. 압축소(apchukso.com)도 같은 분야. 인도 쪽 큰 사이트들은 숫자가 틀린 경우가 많음(UGC NET·GDS)
2-12. **UGC NET (2026-10-13 배포):** 2-11 후보 ①. 서명 프리셋 `ugcnet-sign`(400×160, 10–50KB, signature-image.js `PRESETS` + 메뉴 'Other Indian exams', KO 라벨 gen_ko, 안내 문구 ko.js), EN 가이드 `/guides/ugc-net-photo-signature-size.html`(라이브 사진·업로드 사진 10–200KB·서명 10–50KB·UDID PDF 50–300KB·일정·거절 사유·정정 기간, 출처: 2026-10-08 정보 공보 PDF + 서명 4–30KB였던 2020 NTA 공지 Notice_20200716081822.pdf). 사진은 공보에 픽셀이 없어서 `?resize=passport&target=200KB`로 안내(시험 날 '업로드한 것과 같은 여권 사진'을 가져가야 해서). 인도 시험 가이드 표·섹션·출처에 UGC NET 추가, 서명 페이지 본문에 링크, llms.txt 서명 프리셋 목록 갱신. **할 것:** GSC 색인 요청(오늘 한도 소진 → 10/14), 접수 마감 10/28 이후 2주쯤 Umami에서 `ugcnet-sign` 사용 확인. 다음: ② EN 증명사진 페이지 'paste your form's rules' 제목 + specs.js '1:r' 비율, ③ JEE Main 2027(접수 10월 말 예상)
2-13. **붙여넣기 칸 위로 + GATE 비율 (2026-10-13 배포):** 2-11 후보 ②. (1) 사진 페이지의 '원서 규격 붙여넣기' 칸이 사진을 올린 뒤에만 보였음(#controls 안) → `gen_image_pages.py` `paste_top` 플래그로 증명사진·20/50/100/200KB 페이지(EN/KO)에서 드롭 영역 바로 위로 옮김(KO는 시험·이력서 칩 아래). 한국어 가이드들이 이 칸을 쓰라고 안내하는데 안 보이던 문제도 해결 (2) EN 증명사진 페이지 제목 "Passport Size Photo Resize in KB — Paste Your Form’s Photo Rules", 설명·리드·0단계·FAQ 첫 질문을 서명 페이지처럼 '붙여넣기' 중심으로 (3) specs.js: "aspect ratio (height : width) = 1 : r, r between 2.75 and 3.75"(GATE 서명, GSC에 실제로 붙여넣은 검색어)처럼 **픽셀 없이 비율만** 있으면 긴 변 400px로 그 비율(r은 범위 가운데) → 400×123. 순서(height:width)가 적혀 있을 때만 (4) 버그 수정: 서명 사진이 아직 읽히는 중에 버튼을 누르면 "Choose a signature image first" → 읽기가 끝날 때까지 기다림 (5) 테스트: 실제 붙여넣기 문장 3개(EN/KO) — 사진을 올리기 전에 칸이 보이는지, 결과 크기·KB 확인. 1~2주 뒤 GSC에서 compress-id-photo 노출·순위(10/10까지 노출 14, 17위) 비교
2-14. **컴활·ITQ 사진 (2026-10-14 배포):** 2-11 후보 ④. 프리셋 `kr-korcham` 400×500·50KB(대한상의 컴활·워드 등: 공지 num=245386 '400×500으로 변경, 1:1.25' + 회원사진 등록 창 `registerMyImage_popup.do` 스크립트 `limitSize = 50 * 1024`, 확장자 jpg/jpeg/png만 — 공지의 GIF는 막힘, 처음 등록은 바로 적용·수정은 관리자 승인·합격 내역 있으면 담당자 승인+신분증 사본), `kr-kpc` 225×300·200KB(KPC ITQ·GTQ: 가로 115~235·세로 150~315px, 500KB 이하, PNG 권장, 시험 주 목요일 23:59까지 등록). compress-image.js `PRESETS`/`PRESET_TARGET`, compress-image.html 메뉴, KO 시험 원서 칩(컴활·워드, ITQ), KO 증명사진 제목·설명에 컴활. 새 KO 가이드 `/ko/guides/computer-certificate-photo-size.html`(대표 이미지 `korcham-hero.jpg`, 비율 비교 `korcham-ratio-ko.jpg`, 칩 `korcham-chips-ko.jpg`), 원서 사진 총정리 표·본문에 컴활·ITQ 추가. specs.js: '가로 115~235픽셀, 세로 150~315픽셀'처럼 범위면 큰 값(235×315). 테스트: 컴활 공지 문장·ITQ 범위 문장 붙여넣기. 경쟁: 압축소(apchukso.com)가 10/1에 컴활·KPC를 이미 다룸 → 우리는 등록 창 세부(51,200바이트, GIF 막힘, 변경 승인, '사진변경신청 건이 존재' 알림)와 비율 그림으로 차별화
2-15. **JPG→PDF 용량 제한 (2026-10-14):** 2-11 후보 ⑤. `jpg-to-pdf.html`에 'PDF size limit' 메뉴(100KB~5MB + 직접 입력 KB, `?target=200KB`/`?target=150KB`→직접 입력). 사진 합이 제한 안이면 원본 그대로, 넘으면 `fitToLimit`: 긴 변 2000px부터 JPEG 화질 0.3~0.9 이분 탐색(PDF 전체 크기로 확인), 안 되면 ×0.8씩 줄임. 페이지 크기는 원본 그대로. 긴 변 700px 미만이면 '작은 글씨 읽기 어려울 수 있음' 경고. Umami 이벤트 `jpg-to-pdf-result`(target·fits·kept·images·outKB). **버그 2개 수정:** (1) EXIF 방향(휴대폰 세로 사진)을 무시해서 페이지가 누워 들어갔음 → 방향 태그가 있는 JPG는 바로 세워 다시 그림 (2) WebP는 `<img>`에 toBlob을 불러서 항상 'Could not read' → decode+canvas로. 테스트: 200KB 제한·링크 ?target=150KB·누운 사진(EXIF 6, 예전 코드에서 실패 확인). EN 제목 'JPG to PDF Under 100KB, 200KB or 500KB', KO 제목 '사진을 PDF로, 용량 제한(200KB·500KB)까지'
2-16. **증명사진 페이지: 버튼 없이 바로 결과 (2026-10-14):** 사장님 지적 — '사진 용량 줄이기'를 먼저 눌러야 다운로드가 나와서 헷갈림. compress-id-photo·us-visa-photo(EN/KO, `.tool[data-live]`, gen_image_pages가 `resize` 있는 페이지에 붙임)는 사진 1장을 올리면 바로 만들고, 틀 끌기(손 뗄 때)·확대·처음으로·규격/용량/형식 변경·붙여넣은 규격마다 다시 만듦(0.3초 디바운스, 숫자 입력은 0.6초). 버튼 줄은 숨김, 결과 카드의 다운로드가 다음 단계. 다시 만드는 동안 `.result.busy`(0.15초 넘으면 흐려지고 다운로드 막힘), 화면은 스크롤 안 함(`SlimIO.reveal(box, {scroll:false})`). 미리보기용으로 디코드한 사진을 재사용해서 첫 결과 0.08초. 하루 한도는 사진 1장당 1회(다시 만들 때는 안 셈). 여러 장이면 예전처럼 버튼. **Umami 주의:** 이 두 페이지는 'tool-used'가 사진 올릴 때 바로 찍혀서 10/14 이후 '실행' 수가 '파일 추가'와 거의 같아짐 — 비교는 'downloaded'로. 안내 문구('사진 용량 줄이기 → 다운로드')는 두 페이지·가이드 6개(EN 비자, KO 이력서·원서·비자·여권·컴활)에서 '다운로드'로 바꿈. 티스토리 글 6개(/7 /11 /13 /15 /16 /17)도 2026-10-15에 초안(marketing/tistory)대로 본문 교체 — '결과 확인하고 다운로드'. 대표 이미지·발행일 그대로, 실제 글 = 초안 확인. 테스트: `photoResult()`(live면 busy 끝날 때까지 기다림), '버튼 없이 만들어지고 확대 따라감', '두 장은 버튼'
3. **사용자 확인할 것:** 다른 계정(네이버 메일 등)에서 `contact@pdfslimio.com`으로 테스트 메일 → Gmail 수신 확인 / 폰에서 `pdfslimio.com/?notrack` 한 번 열기
4. **티스토리 블로그 (2026-10-04~):** `ddoua.tistory.com` — 블로그 이름 "문서·사진 생활 꿀팁"(원래 여행 블로그 이름에서 변경). 글 #1 증명사진 용량 줄이기 → https://ddoua.tistory.com/7 (초안 `marketing/tistory/01-id-photo.html`, 이미지는 사이트 `public/img/blog/`에서 불러옴, 대표이미지는 티스토리에 직접 업로드). 네이버 서치어드바이저에 블로그 등록(메타 태그는 티스토리 '메타 태그 등록' 플러그인), 사이트맵·글 수집 요청 완료. 글 #2 서명 이미지 + PDF 서명 → https://ddoua.tistory.com/8 (2026-10-05, 초안 `marketing/tistory/02-signature.html`). 카테고리 "문서·사진 꿀팁". 글 #3 PDF 용량 줄이기 → https://ddoua.tistory.com/9 (2026-10-06, 예시 문서는 직접 만든 '플리마켓 결과 보고서'). 글 #4 시험 원서 사진 규격(큐넷·공무원·한능검·토익) → https://ddoua.tistory.com/11 (2026-10-07, 초안 `marketing/tistory/04-exam-photo.html`, 네이버 수집 요청 완료. 발행 패널 기본값이 비공개로 바뀌어 있었음 → 공개 라디오 확인 필수). 글 #5 PDF 도장·직인 넣기 → https://ddoua.tistory.com/12 (2026-10-07, 초안 `marketing/tistory/05-pdf-stamp.html`, 예시는 가상 견적서·'예시상회' 직인, 네이버 수집 요청 완료). 이때 sign-pdf 업로드 배경 제거를 지역 종이 밝기 기준으로 바꿈(예전엔 회색 종이 사진이 통째로 남았음; 책상 가장자리는 아직 남음), 빨간 네모 직인은 64pt·이름 도장은 42pt로 들어감. 글 #6 미국 비자 사진(DS-160) → https://ddoua.tistory.com/13 (2026-10-09, 초안 `marketing/tistory/06-us-visa-photo.html`, 이미지 visa-hero/step1/step3 + 가이드의 visa-frame-ko, 네이버 수집 요청 완료). 대표이미지는 처음엔 못 넣었다가 **2026-10-13에 추가**(visa-hero.jpg, 발행일 10/9 그대로). 방법: 수정 화면(`/manage/newpost/13`)은 기본모드로 열리고, HTML 모드로 바꾸면 이미 변환된 HTML이 보임(첫 사진 `text-align:center` 빠짐·`data-ke-size` 추가). 그래서 편집기 클릭 → Cmd+↑ → Cmd+Shift+↓로 전체 선택(Cmd+A는 안 먹음) → 원본 본문 붙여넣기 → 완료 → 대표이미지 → 공개 발행. 발행 후 본문 HTML이 이전과 똑같은 것 확인(달라진 건 공유 썸네일뿐). 이제 글 8개 모두 대표이미지 있음. 글 #7 여권 재발급 온라인 사진 → https://ddoua.tistory.com/15 (2026-10-11, 초안 `marketing/tistory/07-passport-photo.html`, 대표이미지 passport-hero.jpg 업로드 성공 — 파일 선택 창에서 Cmd+Shift+G로 경로 입력, 네이버 수집 요청 완료, 캡차 없음). 글 #8 이력서 사진 크기(잡코리아·사람인) → https://ddoua.tistory.com/16 (2026-10-12, 초안 `marketing/tistory/08-resume-photo.html`, 이미지 resume-hero·resume-chips-ko, 대표이미지 resume-hero.jpg 업로드, 태그 9개, 네이버 수집 요청 완료, 캡차 없음). 글 #9 컴활 사진 규격(대한상의 400×500·50KB, ITQ) → https://ddoua.tistory.com/17 (2026-10-14, 초안 `marketing/tistory/09-korcham-photo.html`, 이미지 korcham-hero/ratio/chips, 대표이미지 korcham-hero.jpg, 태그 9개. 새 글쓰기 창을 열면 한글 입력기 "한" 표시가 AX 트리를 가려서(트리에 대화상자+IME 버튼만) 빈 곳을 좌표 클릭한 뒤 읽어야 했음). 블로그는 티스토리만(네이버 블로그 안 함). 네이버 RSS 제출은 캡차 후에도 목록에 안 남음(미완) 비공개 임시저장(망가진 첫 시도) 1개 남음 — 삭제는 마우스 올려 ✕
5. **홍보:** `marketing/PROMO.md` 순서대로 (AlternativeTo·SaaSHub 등록 → Show HN → GeekNews/디스콰이엇 → r/SideProject → X). 올린 날짜를 표에 기록
6. **페이지 추가·수정 후 배포하면** `tools/indexnow.sh` 실행 + GSC·네이버에서 새 URL 색인 요청
   - 2026-09-29: 증명사진·50KB·20KB 6개 GSC 색인 요청 + GSC 사이트맵 재제출, 네이버 `/ko/` 3개 수집 요청 완료 (Claude가 `orca computer`로 Chrome 조작 — 사용자 로그인 세션 사용)
   - 참고: 그날 GSC 개요는 '색인 0 / 미색인 1'로 표시(리포트 지연 가능). 1~2주 뒤 Pages 리포트 확인
7. 다음 개발 후보: 규격별 페이지(인도 시험 사진+서명, 큐넷·정부24, 쉥겐 비자 35×45mm 등), PDF 암호 걸기/해제(qpdf), 가이드 글(Mac/iPhone에서 PDF 줄이기 등), JPG 크기 줄이기 롱테일 (이미지 50KB/20KB·증명사진 페이지·픽셀 직접 입력은 2026-09-29 완료)

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
| 분석 | **Umami Cloud 무료(Hobby)** (2026-09-29~) — website id `ab53f00a-b92a-4d4d-aaf0-6b5329869de7`, 전 페이지 head. 도구 사용 시 `tool-used` 이벤트(`{tool: "merge" / "ko/sign-pdf" / "compress" …}`, `lib.js`의 `SlimIO.track`). **이벤트 4종**: `file-added`(2026-09-30~, 파일 선택·드롭·서명 그리기, 페이지당 1회, `{how: pick/drop/draw}`, lib.js 전역 리스너) · `tool-used`(도구 실행) · `downloaded`(결과 다운로드, `SlimIO.download`·index `#dl`·사진 개별 링크) · `target-result`(용량 목표 페이지만: `{target, fits, method: original/server/raster, inKB, outKB}`) — 새 이벤트는 `SlimIO.event(name, props)`. **`?notrack` 한 번 열면 그 브라우저는 집계 제외**(localStorage `umami.disabled`). Cloudflare Web Analytics도 병행(참조자·Core Web Vitals) |
| GitHub | ✅ `https://github.com/showboyz/slimio` (trout 브랜치) |
| Fly token | ✅ 재발급 완료 (2026-09-24) |
| Google Search Console | ✅ `sc-domain:pdfslimio.com`, 사이트맵 제출·주요 URL 색인 요청 완료 |
| 네이버 서치어드바이저 | ✅ `https://pdfslimio.com` 등록·소유확인(홈 메타 태그)·사이트맵 제출·수집 요청 완료 |
| 광고 슬롯 | `<div class="ad" id="ad" hidden></div>` — 2026-10-15부터 '이 자리에 배너 광고가 표시될 수 있어요' 안내 상자를 숨김(심사 때 빈 광고 자리·안내 문구가 미완성 사이트처럼 보일 수 있어서). 승인 후 `hidden`을 빼고 광고 단위를 넣거나 자동 광고 사용. gen_related는 이 div 앞에 next-steps를 넣음 |

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
- 2026-09-30: **자르기 위치 조정** — 증명·여권·직접 입력 크기일 때 첫 사진 위에 초록 틀 + 점선 얼굴 가이드(canvas `#cropcv`), 드래그로 이동·`#zoom`으로 확대, `cropRect()`가 `{fx, fy, z}`로 잘라냄. 여러 장이면 첫 장만 틀 적용, 나머지는 가운데
- 2026-09-30: **증명사진 페이지 디자인** — 규격 타일(`.presets`, 생성기 `"picker": True`, SVG는 `gen_image_pages.py`의 `_tile`), 전/후 예시(`.demo`, `public/img/id-sample*.webp` 총 31KB). 예시 인물은 **Codex CLI 이미지 생성**(`codex exec --skip-git-repo-check -s workspace-write "…save as sample.png"`)으로 만든 가상 인물, 결과 사진은 우리 도구로 직접 잘라 만든 것. gen_ko는 페이지별 추가 UI 번역을 `ui_extra`로 받음
- 로컬 테스트 주의: 서버 메모리 한도 20회/일 — 테스트를 많이 돌리면 버튼이 비활성화됨. 서버 재시작으로 초기화
- 2026-09-30: **서명 이미지 만들기** `signature-image.html` + `js/signature-image.js` (+`/ko/`, 홈 카드·사진 페이지 링크·PDF 서명 관련 링크). 그리기 / 사진 업로드(종이 밝기 백분위 + 주변 대비로 잉크 판별 → 연결 덩어리 중 테두리에 닿거나 갈색(책상)인 것 제거 → 잉크에 맞춰 자르기). 크기: 자동/픽셀 직접, 용량: 제한 없음/10~20KB/20·50·100KB 이하, JPG(흰 배경)/PNG(투명). **최소 용량**은 화질 최대 후에도 작으면 JPEG COM 세그먼트·PNG tEXt 청크로 여백 데이터 추가(이미지 불변). 예시 사진은 Codex 생성(가상 서명), 결과는 도구로 직접 만든 것
- 2026-09-30: **모바일 스크롤 함정 수정** — 서명 칸(`#pad`, 서명 이미지·PDF 서명)이 터치를 가로채 페이지가 스크롤되지 않던 문제(첸나이 Android 사용자가 열자마자 이탈). 터치 기기(`pointer: coarse`)에선 `.padwrap` 위 "✍️ Tap here to sign" 오버레이로 잠금 → 누르면 `.live`. `file-added(draw)`는 실제 선을 그을 때만. **새 캔버스 UI를 만들면 모바일에서 '위로 쓸기'로 스크롤되는지 꼭 테스트**
- 2026-09-30: **서명 흐름 정리** — PDF 서명 버튼 "+ 이 페이지에 서명 넣기"(구 "페이지에 추가"), 넣은 서명은 화면에 보이는 부분 가운데에 배치 + 필요 시 스크롤. 서명 이미지: 탭 "📷 종이 서명 사진", 맨 위 "PDF 문서에 바로 서명하려면 → PDF 서명", 결과 아래 "이 서명으로 PDF에 서명하기"(sessionStorage `slimio.signature`로 PNG 전달 → PDF 서명이 업로드 탭에 불러옴). **한국어 기본값 PNG·제한 없음**(문서용), 영어는 JPG·10~20KB(원서용)
- 2026-09-30: **PDF 50KB·300KB·2MB 페이지** (+`/ko/`, `gen_size_pages.py` PAGES/SIBLINGS, gen_ko SIZE_PAGES·KO·COMMON, 홈 "Need an exact size?" 줄). 주제 분리: 50KB=증명서 한 장·흑백 스캔 팁·JPG 대안, 300KB=여러 장 증명서·합치기·폰 스캔, 2MB=기관 제출·검색 가능 유지. 실제 사진 PDF로 확인: 1장 0.45MB→33KB, 3장 6.5MB→102KB, 6장 18MB→0.68MB (모두 서버 GS, 0.3~3초). 서버 압축 결과 문구를 "페이지는 그대로 두고 이미지만 줄였어요"로 정정(스캔 PDF에 '글자 선택 가능'이라 하던 것)
- 2026-10-01: **도구 간 연결 재디자인** — `tools/gen_related.py`(도구 표 TOOLS 영·한 한 곳 관리). ① 다운로드 직후 "이어서 이런 것도 해 보세요" 카드 3개(`#next`, lib.js `trackDownload`가 표시, 페이지별 맥락 PAGES) ② 하단 추천 배너(PDF 페이지→증명사진, 사진 페이지→서명 이미지, 실제 예시 이미지) ③ 전체 도구 카드(PDF / 사진·서명). 마커 `<!-- next-steps:… -->`, `<!-- more-tools:… -->` 사이를 교체 → 여러 번 돌려도 동일. **gen_ko.py가 시작할 때 gen_related를 먼저 실행**하고 번역 쌍(`ko_pairs`)을 COMMON에 붙임. 새 도구 추가 시 TOOLS·PDF_TOOLS/PHOTO_TOOLS·PAGES에 등록
- **생성 순서(전체):** `cd public && python3 ../tools/gen_size_pages.py . x x x && cd ..` → `python3 tools/gen_image_pages.py` → `python3 tools/gen_ko.py`(gen_related·사이트맵 lastmod 포함) → `python3 tools/check_i18n.py` → `python3 tools/bump_versions.py`
- 2026-10-01: **미국 비자 사진** `us-visa-photo.html` (+`/ko/`, 홈 카드, gen_related TOOLS·PHOTO_TOOLS). 공식 기준(travel.state.gov 확인): 정사각형 600×600~1200×1200, JPEG 240kB 이하, 머리 50~69%, 흰/미색 배경, 6개월 이내, 안경·보정 불가. 사진 도구에 `us-visa` 프리셋(600×600) 추가 + 전용 가이드(`GUIDES`: 머리 타원 + 눈 높이 허용 구간 31~44% 점선). 생성기는 공용 목록에 없는 목표 용량(240KB)을 그 페이지에만 추가. 예시는 도구로 만든 600×600(머리 63%, 눈 38%)
- gen_ko `ALLOWED_EN`에 DS, JPEG, mm, cm, px 추가(한국어 페이지에서 허용하는 영문 표기)
- 2026-10-02: **하루 한도를 기기별로** — 브라우저가 localStorage의 무작위 ID(`slimio.device`)를 `X-Device` 헤더로 보냄(`SlimIO.apiHeaders()`), 서버는 **기기당 20회 + IP당 200회 상한**(`DAILY_LIMIT`, `IP_DAILY_LIMIT` 환경변수). 기기 ID 없으면(예전 캐시 페이지) IP당 20회. 인도 통신사 CGNAT(여러 사람이 IP 공유) 때문에 바꿈. IP는 `CF-Connecting-IP` 우선(조작 불가). 개인정보처리방침 영·한 반영
- **사용 현황 보기:** `curl -s https://pdfslimio.com/api/stats -H "X-Stats-Key: $(cat .dev/stats_key)"` → 오늘 사용 수, 기기 수, IP 수, 여러 기기가 같이 쓰는 IP 수(`ipsWithSeveralDevices`, `maxDevicesOnOneIp`), 한도에 걸린 횟수. 키는 `.dev/stats_key`(git 제외)와 Fly secret `STATS_KEY`. 한도 초과는 `fly logs`에 `limit-hit … ip#해시`(매일 바뀌는 솔트), 날 바뀔 때 `usage-summary`
- 2026-10-05: **인도 은행 시험 서류 세트** — `bank-exam-photo-signature.html`(영어 전용, gen_ko `EN_ONLY`로 사이트맵만, gen_related TOOLS `bank-exam`). 규격은 IBPS 공식 가이드(SBI 2026 공고 첨부 PDF)에서 확인: 사진 200×230 20~50KB / 서명 140×60 10~20KB / 왼손 엄지 지문 240×240 20~50KB / 손글씨 서약문 800×400 50~100KB, 서명·서약문 대문자 불가. SSC는 공식 PDF에 수치가 없어 제외. 서명 도구 `?preset=bank-sign|bank-thumb|bank-decl`, 사진 도구 `?resize=bank-photo&target=20-50KB`(+`20-50KB` 옵션). **최소 용량은 1024 기준, 최대는 1000 기준**(양쪽 해석 모두 통과), 최소 미달 JPEG는 COM 세그먼트로 패딩. 잉크 정리: 글씨 영역 안의 작은 점(i 점·마침표)은 유지
- 2026-10-06: **홈 압축 기본값 = 서버(Ghostscript)**, 라벨을 쉬운 말로("선명하게 (추천)" / "기기 안에서만", 단계 "균형 (추천)" 등). 사용자 100MB 파일에서 `Unexpected token '<'` 오류 → 원인: Cloudflare 무료 플랜이 100MB 초과 업로드를 HTML 413으로 차단(우리 서버 한도는 50MB, JSON). 수정: 50MB 초과면 자동으로 브라우저 압축, 서버 응답이 JSON이 아니거나 413/5xx·연결 끊김이면 브라우저 압축으로 대체(안내 문구 표시). 실사이트 테스트: 3MB 7초, 22MB 6초, 45MB 9초 정상
- 2026-10-06: **브라우저 압축 = 이미지만 줄이기** (`public/js/pdf-images.js`, `SlimImages.compress`). pdf-lib로 이미지 객체만 찾아 축소·JPEG 재인코딩(DCT, Flate 8bit RGB/Gray/ICC N=1·3, PNG predictor 지원 / CMYK·Indexed·ImageMask·Decode는 건너뜀), 글자·폰트·도형은 그대로 → 선명. 단계 small 100dpi q0.6 / balanced 150 q0.72 / high 200 q0.85 / `pages`(예전 방식: 페이지 전체를 이미지로, 글자 많은 PDF용). 10% 미만 감소면 안내 문구(서버 모드 또는 pages 권장). pdf-lib 파싱 실패 시 pages로 대체. 비교: 사진 PDF 22MB→833KB(small 326KB), 67MB→2.4MB, 글자 위주 교과서는 그대로(폰트 서브셋은 서버 GS만 가능 → 서버가 최선)
- 2026-10-07: **원서 안내문 붙여넣기** (`public/js/specs.js`, `SlimSpecs.parse`) — 서명·사진 도구 상단 입력칸에 원서 문구를 붙이면 픽셀(px / cm·mm + dpi, 없으면 200dpi 가정), KB 범위(between/to/-/under/not exceed/at least), 형식을 읽어 자동 설정 + "✓ 자동 설정: …" 표시. 두 도구에 **직접 입력 KB 범위**(`custom`, `#kmin/#kmax`) 추가. 계기: GSC 내보내기로 본 서명 페이지 검색어가 원서 안내문 통째("140 x 60 pixels… 30kb to 49kb", "6.0 cm x 2.0 cm at 300 dpi", "3 kb and 300 kb")와 "bna k do"·"im not able to do it". 서명 페이지 28일 평균 순위 2.9, 클릭 22 / PDF 500KB 페이지 70.9위. 서명 페이지 제목을 "Signature Resize to 10–20KB, 140×60 — Paste Your Form’s Rules"로. 파서 테스트 14/14
- **GSC 검색어 보는 법:** Performance → 페이지 필터(URL `&page=%2Asignature-image`) → EXPORT → Download CSV(zip, Queries.csv). 화면 표는 스크롤이 안 됨
- 홈 도구 카드 14개(증명사진·미국 비자·서명 이미지 포함) — 4열이라 마지막 줄 2개
- **목표 용량은 10진수(1KB=1000B)** — `compress-image.js`·`target.js`의 `parseSize`. 접수 사이트가 어느 정의로 검사해도 통과하도록

### AI 검색용 llms.txt (2026-10-08)
- `public/llms.txt` = AI 비서(ChatGPT·Perplexity·Claude)용 사이트 안내(llmstxt.org 형식). 각 페이지의 title·description에서 자동 생성: **페이지를 추가·수정하면 `python3 tools/gen_ko.py && python3 tools/gen_llms.py`**. 새 페이지는 `gen_llms.py`의 그룹(PDF_TOOLS/PHOTO_TOOLS)에 넣어야 함(빠지면 assert로 멈춤)

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
