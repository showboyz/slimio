# 숏폼 시험 1 — 스캔한 PDF 정리 (21초, 1080×1920)

블로그 #15(`marketing/naver/15-pdf-organize.html`)를 짧은 영상으로 만든 것. 장면은 `scene.html`(Web Animations API, `window.seek(t)`로 시간 이동), 이미지는 가상 동아리 보고서와 실제 SlimIO '페이지 순서 변경' 화면(after.png).

다시 만들기 (이 폴더에서):

    node render.mjs 21            # frames/00000.png … 30fps로 캡처
    ffmpeg -y -framerate 30 -i frames/%05d.png -f lavfi -i anullsrc=r=44100:cl=stereo -shortest \
      -c:v libx264 -pix_fmt yuv420p -crf 18 -preset slow -c:a aac -b:a 128k -movflags +faststart pdf-organize-short.mp4

render.mjs는 playwright-core가 필요해요(저장소 루트에서 `node marketing/clips/01-pdf-organize/render.mjs`처럼 돌리거나 이 폴더에 node_modules 링크).
