// Korean UI strings. Keys are the English text used in the code (see SlimIO.t in lib.js).
// Load this before lib.js on /ko/ pages.
window.SLIMIO_KO = {
   // common
   "Please choose a PDF file.": "PDF 파일을 선택해 주세요.",
   "Please choose PDF files.": "PDF 파일을 선택해 주세요.",
   "Please choose image files (JPG, PNG, WebP…).": "이미지 파일(JPG, PNG, WebP 등)을 선택해 주세요.",
   "Daily limit reached. Come back tomorrow.": "오늘 무료 사용 횟수를 모두 썼어요. 내일 다시 이용해 주세요.",
   "Daily limit reached. {limit} per day. Come back tomorrow.": "오늘 무료 사용 횟수({limit}회)를 모두 썼어요. 내일 다시 이용해 주세요.",
   "Operations left today: {remaining} / {limit}": "오늘 남은 횟수: {remaining} / {limit}",
   "Compressions left today: {remaining} / {limit}": "오늘 남은 압축 횟수: {remaining} / {limit}",
   "Limit service currently unavailable.": "남은 횟수를 확인할 수 없어요.",
   "↓ Download PDF": "↓ PDF 다운로드",
   "↓ Download ZIP": "↓ ZIP 다운로드",
   "{pages} in this PDF.": "이 PDF는 {pages}예요.",
   "Could not read file: {msg}": "파일을 읽을 수 없어요: {msg}",
   'Could not read "{name}".': "“{name}” 파일을 읽을 수 없어요.",
   'Could not read "{name}": {msg}': "“{name}” 파일을 읽을 수 없어요: {msg}",
   "Could not open this PDF: {msg}": "이 PDF를 열 수 없어요: {msg}",
   "Move up": "위로",
   "Move down": "아래로",
   "Move left": "왼쪽으로",
   "Move right": "오른쪽으로",
   "Remove": "빼기",

   // compress (main page)
   "Compress PDF": "PDF 압축하기",
   "Compressing…": "압축하는 중…",
   "Compressing with Ghostscript…": "Ghostscript로 압축하는 중…",
   "Converting pages to images to reach the target…": "목표 용량에 맞추려고 페이지를 이미지로 바꾸는 중…",
   "Something went wrong: {msg}": "문제가 생겼어요: {msg}",
   "Server error: {msg}": "서버 오류: {msg}",
   "Compression failed: {msg}": "압축하지 못했어요: {msg}",
   "0% (already optimized)": "0% (이미 최적화된 파일)",
   "Your file runs locally in your browser — nothing is uploaded.": "파일은 브라우저 안에서만 처리돼요. 서버로 올라가지 않아요.",
   "Text stays sharp and selectable. Files are deleted right after compressing.": "글자가 선명하고 복사도 그대로 돼요. 파일은 압축 직후 삭제돼요.",
   "Nothing is uploaded. Photos and scans inside the PDF are shrunk on your device.": "파일은 업로드되지 않아요. PDF 안의 사진·스캔만 내 기기에서 줄여요.",
   "This PDF is mostly text and graphics, which stay as they are. For a much smaller file, choose Level → Pages as images.": "글자와 도형이 대부분인 PDF라 그대로 두었어요. 훨씬 작게 만들려면 압축 정도에서 '페이지를 이미지로'를 고르세요.",
   "This PDF is mostly text and graphics, which stay as they are. Sharp mode shrinks fonts too and usually makes it much smaller.": "글자와 도형이 대부분인 PDF라 그대로 두었어요. '선명하게' 모드는 폰트까지 줄여서 보통 훨씬 작아져요.",
   "Best for most PDFs. Files up to 50MB; larger files are compressed in your browser.": "대부분의 PDF에 가장 좋아요. 50MB까지 가능하고, 더 큰 파일은 브라우저에서 압축해요.",
   "Pages are redrawn as images, so text can't be selected afterwards.": "페이지를 이미지로 다시 만들어서, 압축 후에는 글자를 선택할 수 없어요.",
   "This file is over 50MB, so it will be compressed in your browser.": "50MB가 넘는 파일이라 브라우저에서 압축해요.",
   "The server couldn't take this file right now, so it was compressed in your browser instead.": "지금은 서버에서 처리할 수 없어서 브라우저에서 대신 압축했어요.",
   "Your file is sent to the Ghostscript server to keep text perfectly sharp.": "글자를 선명하게 유지하려고 파일을 Ghostscript 서버로 보내요. 처리 직후 삭제돼요.",

   // compress to size
   "✓ under {size}": "✓ {size} 이하",
   "✗ over {size}": "✗ {size} 초과",
   "Your PDF is already under {size} — no compression needed.": "이미 {size}보다 작아서 압축할 필요가 없어요.",
   "Pages kept as they are — only the images inside were compressed, so any text stays sharp and selectable.": "페이지는 그대로 두고 안의 이미지만 줄였어요. 문서에 글자가 있다면 선명하고 복사도 그대로 돼요.",
   "This is the smallest we could make it. To get under {size}, remove pages you don't need or split the file into parts.": "이게 만들 수 있는 가장 작은 크기예요. {size} 이하로 맞추려면 필요 없는 페이지를 지우거나 파일을 나눠 주세요.",
   "To reach {size}, pages were converted to images at about {dpi} dpi. The text is no longer selectable.": "{size}에 맞추려고 페이지를 약 {dpi}dpi 이미지로 바꿨어요. 글자는 더 이상 선택·복사되지 않아요.",
   " Small print may be hard to read — removing pages you don't need will give a sharper result.": " 작은 글씨는 읽기 어려울 수 있어요. 필요 없는 페이지를 빼면 더 선명해져요.",

   // merge
   "Merge PDFs": "PDF 합치기",
   "Merging…": "합치는 중…",
   "Merge failed: {msg}": "합치지 못했어요: {msg}",

   // split
   "Split PDF": "PDF 나누기",
   "Splitting…": "나누는 중…",
   "Split failed: {msg}": "나누지 못했어요: {msg}",
   "No valid pages in that range.": "입력한 범위에 해당하는 페이지가 없어요.",

   // remove pages
   "Remove pages": "페이지 삭제하기",
   "Removing…": "삭제하는 중…",
   "Remove failed: {msg}": "삭제하지 못했어요: {msg}",
   "This PDF has {pages}. You are removing {removed}.": "이 PDF는 {pages}이고, 그중 {removed}페이지를 삭제해요.",
   "None of those page numbers exist in this PDF.": "입력한 페이지 번호가 이 PDF에 없어요.",
   "You can't remove every page — the result would be empty.": "모든 페이지를 삭제할 수는 없어요. 빈 파일이 돼요.",

   // rotate
   "Rotate PDF": "PDF 회전하기",
   "Rotating…": "회전하는 중…",
   "Rotate failed: {msg}": "회전하지 못했어요: {msg}",
   "No rotation": "회전 안 함",
   "{deg}° clockwise": "시계 방향 {deg}°",

   // organize
   "Save PDF": "PDF 저장하기",
   "Saving…": "저장하는 중…",
   "Save failed: {msg}": "저장하지 못했어요: {msg}",
   "Rotate this page": "이 페이지만 회전",
   "Remove this page": "이 페이지 삭제",

   // page numbers
   "Add page numbers": "페이지 번호 넣기",
   "Numbering…": "번호 넣는 중…",
   "Numbering failed: {msg}": "번호를 넣지 못했어요: {msg}",

   // watermark
   "Add watermark": "워터마크 넣기",
   "Watermarking…": "워터마크 넣는 중…",
   "Watermark failed: {msg}": "워터마크를 넣지 못했어요: {msg}",
   "Please type the watermark text.": "워터마크 문구를 입력해 주세요.",

   // pdf <-> jpg
   "Convert to JPG": "JPG로 변환하기",
   "Convert to PDF": "PDF로 변환하기",
   "Converting…": "변환하는 중…",
   "Conversion failed: {msg}": "변환하지 못했어요: {msg}",
   "{n} image": "이미지 {n}장",
   "{n} images": "이미지 {n}장",

   // compress image
   "Compress images": "사진 용량 줄이기",
   "Drag the frame and zoom: head inside the oval, eyes between the two dotted lines.": "틀을 옮기고 확대해서 머리는 타원 안에, 눈은 두 점선 사이에 오게 하세요.",
   "Drag the frame so your face sits inside the guide.": "틀을 끌어서 얼굴이 점선 안에 들어오게 하세요.",
   "Drag the frame to set the crop on the first photo. The others are cropped from the center.": "틀을 끌어서 첫 번째 사진의 자를 위치를 정하세요. 나머지 사진은 가운데를 기준으로 잘라요.",
   "No signature found in the photo. Try a darker pen or a brighter photo.": "사진에서 서명을 찾지 못했어요. 더 진한 펜으로 쓰거나 더 밝게 찍어 주세요.",
   "Padded to meet the {kb}KB minimum; the image itself is unchanged.": "최소 {kb}KB에 맞추려고 파일에 여백 데이터를 더했어요. 이미지는 그대로예요.",
   "Still over the limit at this pixel size. Try a smaller size.": "이 픽셀 크기로는 용량 제한을 넘어요. 크기를 더 작게 해 보세요.",
   "Still over the limit — choose JPG, which is much smaller.": "아직 용량 제한을 넘어요. 훨씬 작은 JPG를 골라 주세요.",
   "Sign on white paper with a black pen. Signatures in CAPITAL LETTERS are not accepted.": "흰 종이에 검은 펜으로 서명하세요. 대문자로 쓴 서명은 받아 주지 않아요.",
   "Press your left thumb on white paper with black or blue ink, then photograph it.": "검은색이나 파란색 잉크로 흰 종이에 왼손 엄지 지문을 찍은 뒤 사진을 찍으세요.",
   "Write the declaration text from the notice in English, in black ink, not in capital letters.": "공고문의 서약문을 영어로, 검은 펜으로, 대문자가 아닌 글씨로 쓰세요.",
   "padded to the minimum size; the image is unchanged": "최소 용량에 맞춰 여백 데이터를 더했어요(이미지는 그대로)",
   "Always check the exact numbers in your exam notice.": "정확한 숫자는 꼭 시험 공고문에서 확인하세요.",
   "Enter a width and height between 16 and 4000 pixels.": "가로와 세로를 16~4000픽셀 사이로 입력해 주세요.",
   "↓ Download": "↓ 다운로드",
   "Total: {before} → {after} ({change})": "전체: {before} → {after} ({change})",
   "already optimized, kept as is": "이미 최적화된 파일이라 그대로 두었어요",
   "This image can't be opened in this browser (HEIC photos, for example). Save it as JPG and try again.": "이 브라우저에서 열 수 없는 사진이에요(아이폰 HEIC 등). JPG로 저장한 뒤 다시 시도해 주세요.",

   // sign pdf
   "Page {n} / {total}": "{n} / {total}페이지",
   "Draw your signature first.": "먼저 서명을 그려 주세요.",
   "Type your name first.": "먼저 이름을 입력해 주세요.",
   "Choose a signature image first.": "먼저 서명이나 도장 이미지를 골라 주세요.",
   "Add a signature to the page first.": "먼저 페이지에 서명을 추가해 주세요.",
   "Signing…": "서명하는 중…",
   "Sign & download": "서명하고 다운로드",
   "Sign failed: {msg}": "서명하지 못했어요: {msg}",
   "{n} signature": "서명 {n}개",
   "{n} signatures": "서명 {n}개",
   "Seal": "도장",
   "Your name": "홍길동",
};
