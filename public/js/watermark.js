const { PDFDocument, StandardFonts, rgb, degrees } = PDFLib;
const drop = $("drop");
const controls = $("controls");
const goBtn = $("go");
const result = $("result");
const dl = $("dl");
const prog = SlimIO.bindProgress("prog");
const COLORS = { gray: rgb(0.45, 0.45, 0.45), red: rgb(0.85, 0.1, 0.1), blue: rgb(0.1, 0.3, 0.85) };
const CSS_COLORS = { gray: "rgb(115,115,115)", red: "rgb(217,26,26)", blue: "rgb(26,77,217)" };

let file = null;

// How the watermark gets drawn. Latin text uses vector Helvetica. Anything
// Helvetica can't encode (Korean, Japanese, Arabic…) is rendered by the browser,
// which already has fonts for it, into an image (embedMark) — no font download.
// "size" works like a font size in both cases.
async function makeDrawer(doc, text, colorName) {
     const font = await doc.embedFont(StandardFonts.HelveticaBold);
     try {
             font.encodeText(text);
             return {
                     width: (size) => font.widthOfTextAtSize(text, size),
                     height: (size) => font.heightAtSize(size, { descender: false }),
                     draw: (page, x, y, size, angle, opacity) =>
                             page.drawText(text, { x, y, size, font, color: COLORS[colorName], opacity, rotate: degrees(angle) }),
             };
     } catch (e) { /* not Latin: draw it as an image */ }

     // 240px letters, but a long phrase gets smaller letters so the image stays about 800px wide. A diagonal mark
     // on A4 is about 10 inches long, so that is 80 dpi: plenty for a pale mark, and the file stays small.
     const cssFont = (px) => `bold ${px}px "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", "Noto Sans CJK KR", sans-serif`;
     const canvas = document.createElement("canvas");
     const ctx = canvas.getContext("2d");
     ctx.font = cssFont(240);
     const px = Math.max(48, Math.min(240, Math.floor((240 * 800) / ctx.measureText(text).width)));
     const css = cssFont(px);
     ctx.font = css;
     canvas.width = Math.ceil(ctx.measureText(text).width + px / 4);
     canvas.height = Math.ceil(px * 1.25);
     ctx.font = css;   // resizing a canvas resets its drawing state
     ctx.fillStyle = "#000";
     ctx.textBaseline = "middle";
     ctx.fillText(text, px / 8, canvas.height / 2);
     const img = await embedMark(doc, canvas, colorName);
     const ratio = canvas.width / canvas.height;
     return {
             width: (size) => size * 1.25 * ratio,
             height: (size) => size * 1.25,
             draw: (page, x, y, size, angle, opacity) =>
                     page.drawImage(img, { x, y, width: size * 1.25 * ratio, height: size * 1.25, opacity, rotate: degrees(angle) }),
     };
}

// The text drawn on a canvas as an image of one flat colour with the letters in its soft mask. A PNG
// through embedPng kept the letter edges in the colour channels too and pdf-lib deflates without a PNG
// predictor: "아르바이트 지원 서류 제출용 (2026.11)" added 76KB to a 3KB PDF, too much for a "100KB 이하"
// upload. Here the colour channels are all one value (they pack to almost nothing) and the mask rows
// are stored as differences from the row above (PNG "Up" predictor), which suits letters.
async function embedMark(doc, canvas, colorName) {
     const { width: w, height: h } = canvas;
     const px = canvas.getContext("2d").getImageData(0, 0, w, h).data;
     const mask = new Uint8Array((w + 1) * h);
     for (let y = 0; y < h; y++) {
             const row = y * (w + 1);
             mask[row] = 2;   // PNG filter "Up"
             for (let x = 0; x < w; x++) {
                     const a = px[(y * w + x) * 4 + 3], above = y ? px[((y - 1) * w + x) * 4 + 3] : 0;
                     mask[row + 1 + x] = (a - above) & 255;
             }
     }
     const [r, g, b] = CSS_COLORS[colorName].match(/\d+/g).map(Number);
     const flat = new Uint8Array(w * h * 3);
     for (let i = 0; i < flat.length; i += 3) { flat[i] = r; flat[i + 1] = g; flat[i + 2] = b; }
     const ctx = doc.context;
     const smask = ctx.register(ctx.flateStream(mask, {
             Type: "XObject", Subtype: "Image", Width: w, Height: h, ColorSpace: "DeviceGray", BitsPerComponent: 8,
             DecodeParms: { Predictor: 15, Colors: 1, BitsPerComponent: 8, Columns: w },
     }));
     const image = ctx.flateStream(flat, {
             Type: "XObject", Subtype: "Image", Width: w, Height: h, ColorSpace: "DeviceRGB", BitsPerComponent: 8, SMask: smask,
     });
     // drawImage wants a PDFImage: embed a 1×1 PNG, then put our image object in its place
     const one = document.createElement("canvas");
     one.width = one.height = 1;
     const blob = await new Promise((resolve) => one.toBlob(resolve, "image/png"));
     const img = await doc.embedPng(new Uint8Array(await blob.arrayBuffer()));
     await img.embed();
     ctx.assign(img.ref, image);
     return img;
}

function setFile(f) {
     if (!SlimIO.isPdf(f)) { SlimIO.notPdf(f); return; }
     SlimIO.clearError();
     file = f;
     drop.querySelector(".drop-title").textContent = f.name;
     drop.querySelector(".drop-or").textContent = SlimIO.formatSize(f.size);
     controls.classList.remove("hidden");
     goBtn.disabled = false;
     SlimIO.refreshStatus();
}

drop.addEventListener("click", () => $("pdf").click());
$("pdf").addEventListener("change", () => setFile($("pdf").files[0]));
drop.addEventListener("dragover", (e) => { e.preventDefault(); drop.classList.add("drag"); });
drop.addEventListener("dragleave", () => drop.classList.remove("drag"));
drop.addEventListener("drop", (e) => {
     e.preventDefault();
     drop.classList.remove("drag");
     if (e.dataTransfer.files.length) setFile(e.dataTransfer.files[0]);
});
$("opacity").addEventListener("input", () => { $("opv").textContent = $("opacity").value + "%"; });

goBtn.addEventListener("click", addWatermark);

// Draw the watermark centered on visual point (cx, cy) at visual angle theta (degrees).
function stamp(page, v, drawer, size, cx, cy, theta, opacity) {
     const tw = drawer.width(size);
     const th = drawer.height(size);
     const t = (theta * Math.PI) / 180;
     const vx = cx - (tw / 2) * Math.cos(t) + (th / 2) * Math.sin(t);
     const vy = cy - (tw / 2) * Math.sin(t) - (th / 2) * Math.cos(t);
     const p = v.map(vx, vy);
     drawer.draw(page, p.x, p.y, size, theta + p.angle, opacity);
}

async function addWatermark() {
     if (!file) return;
     const text = $("text").value.trim();
     if (!text) { SlimIO.showError(SlimIO.t("Please type the watermark text.")); return; }
     SlimIO.clearError();
     goBtn.disabled = true;
     goBtn.textContent = SlimIO.t("Watermarking…");
     prog.show();
     result.style.display = "none";
     try {
             const doc = await PDFDocument.load(await file.arrayBuffer());
             const check = await SlimIO.consume();
             if (check && !check.ok) { SlimIO.showError(SlimIO.t("Daily limit reached. Come back tomorrow.")); return; }
             const drawer = await makeDrawer(doc, text, $("color").value);
             const style = $("style").value;
             const opacity = parseInt($("opacity").value, 10) / 100;
             const pages = doc.getPages();

             for (let i = 0; i < pages.length; i++) {
                 const page = pages[i];
                 const v = SlimIO.page2user(page);
                 const w = v.width, h = v.height;
                 if (style === "tiled") {
                     // Rows run along the 30° text itself, so a long phrase never runs into the next row.
                     const size = Math.max(14, Math.min(w, h) / 14);
                     const t = (30 * Math.PI) / 180;
                     const along = drawer.width(size) + size * 3;
                     const across = size * 4.5;
                     const reach = Math.hypot(w, h);
                     const rows = Math.ceil(reach / across), cols = Math.ceil(reach / along) + 1;
                     for (let j = -rows; j <= rows; j++) {
                         for (let i = -cols; i <= cols; i++) {
                             const a = i * along + (j % 2) * (along / 2);
                             const cx = w / 2 + a * Math.cos(t) - j * across * Math.sin(t);
                             const cy = h / 2 + a * Math.sin(t) + j * across * Math.cos(t);
                             if (cx < -along || cx > w + along || cy < -along || cy > h + along) continue;
                             stamp(page, v, drawer, size, cx, cy, 30, opacity);
                         }
                     }
                 } else {
                     const theta = style === "diagonal" ? (Math.atan2(h, w) * 180) / Math.PI : 0;
                     const span = style === "diagonal" ? Math.hypot(w, h) : w;
                     const size = Math.min(span * 0.7 / drawer.width(1), Math.min(w, h) / 4);
                     stamp(page, v, drawer, size, w / 2, h / 2, theta, opacity);
                 }
                 prog.set(Math.round(((i + 1) / pages.length) * 100));
             }
             const out = await doc.save();
             showResult(pages.length, text, out);
     } catch (e) {
             SlimIO.showError(SlimIO.pdfError("Watermark failed: {msg}", e));
     } finally {
             goBtn.disabled = false;
             goBtn.textContent = SlimIO.t("Add watermark");
             prog.hide();
     }
}

function showResult(count, text, bytes) {
     result.style.display = "block";
     $("after").textContent = SlimIO.pages(count);
     $("wm").textContent = text;
     dl.onclick = () => SlimIO.download(bytes, "slimio_watermarked.pdf", "application/pdf");
     SlimIO.reveal(result);
}

SlimIO.refreshStatus();
