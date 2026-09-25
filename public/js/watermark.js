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
// which already has fonts for it, into a transparent PNG — no font download.
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

     const px = 240;
     const css = `bold ${px}px "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", "Noto Sans CJK KR", sans-serif`;
     const canvas = document.createElement("canvas");
     const ctx = canvas.getContext("2d");
     ctx.font = css;
     canvas.width = Math.ceil(ctx.measureText(text).width + px / 4);
     canvas.height = Math.ceil(px * 1.25);
     ctx.font = css;   // resizing a canvas resets its drawing state
     ctx.fillStyle = CSS_COLORS[colorName];
     ctx.textBaseline = "middle";
     ctx.fillText(text, px / 8, canvas.height / 2);
     const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
     const img = await doc.embedPng(new Uint8Array(await blob.arrayBuffer()));   // embedded once, reused on every page
     const ratio = canvas.width / canvas.height;
     return {
             width: (size) => size * 1.25 * ratio,
             height: (size) => size * 1.25,
             draw: (page, x, y, size, angle, opacity) =>
                     page.drawImage(img, { x, y, width: size * 1.25 * ratio, height: size * 1.25, opacity, rotate: degrees(angle) }),
     };
}

function setFile(f) {
     if (!f || f.type !== "application/pdf") { SlimIO.showError(SlimIO.t("Please choose a PDF file.")); return; }
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
             const check = await SlimIO.consume();
             if (check && !check.ok) { SlimIO.showError(SlimIO.t("Daily limit reached. Come back tomorrow.")); return; }

             const doc = await PDFDocument.load(await file.arrayBuffer());
             const drawer = await makeDrawer(doc, text, $("color").value);
             const style = $("style").value;
             const opacity = parseInt($("opacity").value, 10) / 100;
             const pages = doc.getPages();

             for (let i = 0; i < pages.length; i++) {
                 const page = pages[i];
                 const v = SlimIO.page2user(page);
                 const w = v.width, h = v.height;
                 if (style === "tiled") {
                     const size = Math.max(14, Math.min(w, h) / 14);
                     const stepX = drawer.width(size) + size * 3;
                     const stepY = size * 5;
                     for (let row = 0, y = -h / 2; y < h * 1.5; row++, y += stepY) {
                         for (let x = -w / 2 + (row % 2) * (stepX / 2); x < w * 1.5; x += stepX) {
                             stamp(page, v, drawer, size, x, y, 30, opacity);
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
             SlimIO.showError(SlimIO.t("Watermark failed: {msg}", { msg: e.message }));
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
}

SlimIO.refreshStatus();
