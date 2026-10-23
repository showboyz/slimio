# 숏폼 시험 1 — 스캔한 PDF 정리 (21초, 1080×1920)

블로그 #15(`marketing/naver/15-pdf-organize.html`)를 짧은 영상으로 만든 것. 장면은 `scene.html`(Web Animations API, `window.seek(t)`로 시간 이동), 이미지는 가상 동아리 보고서와 실제 SlimIO '페이지 순서 변경' 화면(after.png).

다시 만들기 (이 폴더에서):

    node render.mjs 21            # frames/00000.png … 30fps로 캡처
    ffmpeg -y -framerate 30 -i frames/%05d.png -f lavfi -i anullsrc=r=44100:cl=stereo -shortest \
      -c:v libx264 -pix_fmt yuv420p -crf 18 -preset slow -c:a aac -b:a 128k -movflags +faststart pdf-organize-short.mp4

render.mjs는 playwright-core가 필요해요(저장소 루트에서 `node marketing/clips/01-pdf-organize/render.mjs`처럼 돌리거나 이 폴더에 node_modules 링크).

## 네이버 클립에 올리기 (2026-10-23 공식 도움말 확인)

- **블로그 앱 [+] → 클립 만들기** (휴대폰): 클립이 블로그(todayz777)에 붙어서 블로그에도 보여요. 예약은 안 돼요.
- **클립 크리에이터 PC 웹** https://clipcreators.naver.com/web (클립 프로필 필요): 이 mp4를 그대로 올리고 **최대 30일 뒤까지 예약**할 수 있어요. 대신 블로그 화면에는 안 나와요.
- 어느 쪽이든 올릴 때 **콘텐츠 링크 → 블로그**에서 같은 주제 글(#15)을 검색해 붙이면, 영상을 보다가 글로 넘어갈 수 있어요.
- 설명은 300자, 해시태그는 5개까지예요. 설명에 넣은 링크는 눌리지 않아요.
