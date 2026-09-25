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
   "Your file is sent to the Ghostscript server to keep text perfectly sharp.": "글자를 선명하게 유지하려고 파일을 Ghostscript 서버로 보내요. 처리 직후 삭제돼요.",

   // compress to size
   "✓ under {size}": "✓ {size} 이하",
   "✗ over {size}": "✗ {size} 초과",
   "Your PDF is already under {size} — no compression needed.": "이미 {size}보다 작아서 압축할 필요가 없어요.",
   "Text kept sharp and selectable.": "글자가 선명하고, 복사도 그대로 돼요.",
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
};
