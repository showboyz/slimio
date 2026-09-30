pdfjsLib.GlobalWorkerOptions.workerSrc =
        "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
const { PDFDocument, degrees } = PDFLib;
const drop = $("drop");
const controls = $("controls");
const goBtn = $("go");
const result = $("result");
const dl = $("dl");
const stage = $("stage");
const pageCanvas = $("pagecanvas");
const layer = $("layer");
const prog = SlimIO.bindProgress("prog");

let file = null;
let bytes = null;       // original PDF
let viewer = null;      // pdf.js document for the preview
let pageNo = 1;
let pageSize = null;    // current page as seen, in PDF points
let scale = 1;          // CSS px per PDF point on the stage
let renderTask = null;
let mode = "draw";
// Placed signatures. x/y/w/h are PDF points from the page's visible top-left corner.
let items = [];

const clamp = (v, lo, hi) => Math.min(Math.max(v, lo), Math.max(lo, hi));

// ---------------------------------------------------------------- file & pages

async function setFile(f) {
     if (!f || f.type !== "application/pdf") { SlimIO.showError(SlimIO.t("Please choose a PDF file.")); return; }
     SlimIO.clearError();
     try {
             const data = new Uint8Array(await f.arrayBuffer());
             const doc = await pdfjsLib.getDocument({ data: data.slice() }).promise;
             file = f;
             bytes = data;
             viewer = doc;
     } catch (e) {
             SlimIO.showError(SlimIO.t("Could not open this PDF: {msg}", { msg: e.message }));
             return;
     }
     drop.querySelector(".drop-title").textContent = f.name;
     drop.querySelector(".drop-or").textContent = SlimIO.formatSize(f.size);
     controls.classList.remove("hidden");
     result.style.display = "none";
     items = [];
     pageNo = 1;
     sizePad();
     await showPage();
     updateGo();
     SlimIO.refreshStatus();
}

async function showPage() {
     const page = await viewer.getPage(pageNo);
     const base = page.getViewport({ scale: 1 });
     pageSize = { w: base.width, h: base.height };
     scale = stage.clientWidth / base.width;
     const dpr = window.devicePixelRatio || 1;
     const vp = page.getViewport({ scale: scale * dpr });
     if (renderTask) renderTask.cancel();
     pageCanvas.width = Math.floor(vp.width);
     pageCanvas.height = Math.floor(vp.height);
     pageCanvas.style.height = base.height * scale + "px";
     renderTask = page.render({ canvasContext: pageCanvas.getContext("2d"), viewport: vp });
     try { await renderTask.promise; } catch (e) { if (e && e.name !== "RenderingCancelledException") throw e; }
     $("pageinfo").textContent = SlimIO.t("Page {n} / {total}", { n: pageNo, total: viewer.numPages });
     $("prev").disabled = pageNo === 1;
     $("next").disabled = pageNo === viewer.numPages;
     drawItems();
}

$("prev").addEventListener("click", () => { if (pageNo > 1) { pageNo--; showPage(); } });
$("next").addEventListener("click", () => { if (pageNo < viewer.numPages) { pageNo++; showPage(); } });
let resizeTimer = null;
window.addEventListener("resize", () => {
     clearTimeout(resizeTimer);
     resizeTimer = setTimeout(() => { if (viewer) showPage(); sizePad(); }, 200);
});

// ---------------------------------------------------------------- placed items

function place(el, it) {
     el.style.left = it.x * scale + "px";
     el.style.top = it.y * scale + "px";
     el.style.width = it.w * scale + "px";
     el.style.height = it.h * scale + "px";
}

function drawItems() {
     layer.replaceChildren(...items.filter((it) => it.page === pageNo).map(itemEl));
}

function itemEl(it) {
     const el = document.createElement("div");
     el.className = "item";
     const img = document.createElement("img");
     img.src = it.img.url;
     img.alt = "";
     const x = document.createElement("button");
     x.type = "button";
     x.className = "x";
     x.textContent = "✕";
     x.title = SlimIO.t("Remove");
     const handle = document.createElement("div");
     handle.className = "h";
     el.append(img, x, handle);
     place(el, it);
     x.addEventListener("pointerdown", (e) => e.stopPropagation());
     x.addEventListener("click", () => { items.splice(items.indexOf(it), 1); drawItems(); updateGo(); });
     drag(el, el, it, "move");
     drag(handle, el, it, "resize");
     return el;
}

function drag(target, el, it, kind) {
     target.addEventListener("pointerdown", (e) => {
             e.preventDefault();
             e.stopPropagation();
             target.setPointerCapture(e.pointerId);
             const sx = e.clientX, sy = e.clientY, ox = it.x, oy = it.y, ow = it.w;
             const ratio = it.img.h / it.img.w;
             const move = (ev) => {
                     const dx = (ev.clientX - sx) / scale, dy = (ev.clientY - sy) / scale;
                     if (kind === "move") {
                             it.x = clamp(ox + dx, 0, pageSize.w - it.w);
                             it.y = clamp(oy + dy, 0, pageSize.h - it.h);
                     } else {
                             let w = clamp(ow + dx, 16, pageSize.w - it.x);
                             if (it.y + w * ratio > pageSize.h) w = (pageSize.h - it.y) / ratio;
                             it.w = w;
                             it.h = w * ratio;
                     }
                     place(el, it);
             };
             const end = () => {
                     target.removeEventListener("pointermove", move);
                     target.removeEventListener("pointerup", end);
                     target.removeEventListener("pointercancel", end);
             };
             target.addEventListener("pointermove", move);
             target.addEventListener("pointerup", end);
             target.addEventListener("pointercancel", end);
     });
}

function updateGo() { goBtn.disabled = !items.length; }

// ---------------------------------------------------------------- signature: draw

const pad = $("pad");
const padCtx = pad.getContext("2d");
let ink = "#111111";
let bounds = null;   // bounding box of what's been drawn, in canvas pixels

function sizePad() {
     const dpr = window.devicePixelRatio || 1;
     const w = Math.round(pad.clientWidth * dpr), h = Math.round(pad.clientHeight * dpr);
     if (!w || (pad.width === w && pad.height === h)) return;
     if (bounds) return;   // don't wipe a signature because the window changed size
     pad.width = w;
     pad.height = h;
}

function padPoint(e) {
     const r = pad.getBoundingClientRect();
     return { x: (e.clientX - r.left) * (pad.width / r.width), y: (e.clientY - r.top) * (pad.height / r.height) };
}

function grow(p) {
     const m = padCtx.lineWidth;
     if (!bounds) bounds = { x0: p.x, y0: p.y, x1: p.x, y1: p.y };
     bounds.x0 = Math.min(bounds.x0, p.x - m); bounds.y0 = Math.min(bounds.y0, p.y - m);
     bounds.x1 = Math.max(bounds.x1, p.x + m); bounds.y1 = Math.max(bounds.y1, p.y + m);
}

let last = null;
pad.addEventListener("pointerdown", (e) => {
     e.preventDefault();
     sizePad();
     pad.setPointerCapture(e.pointerId);
     last = padPoint(e);
     padCtx.strokeStyle = padCtx.fillStyle = ink;
     padCtx.lineWidth = 2.6 * (window.devicePixelRatio || 1);
     padCtx.lineCap = padCtx.lineJoin = "round";
     padCtx.beginPath();
     padCtx.arc(last.x, last.y, padCtx.lineWidth / 2, 0, Math.PI * 2);
     padCtx.fill();
     grow(last);
});
pad.addEventListener("pointermove", (e) => {
     if (!last) return;
     const p = padPoint(e);
     const mid = { x: (last.x + p.x) / 2, y: (last.y + p.y) / 2 };
     padCtx.beginPath();
     padCtx.moveTo(last.midX ?? last.x, last.midY ?? last.y);
     padCtx.quadraticCurveTo(last.x, last.y, mid.x, mid.y);   // smooth through the previous point
     padCtx.stroke();
     last = { ...p, midX: mid.x, midY: mid.y };
     grow(p);
});
const penUp = () => { last = null; };
$("padstart").addEventListener("click", () => { pad.parentElement.classList.add("live"); sizePad(); });
pad.addEventListener("pointerup", penUp);
pad.addEventListener("pointercancel", penUp);

$("clear").addEventListener("click", () => { padCtx.clearRect(0, 0, pad.width, pad.height); bounds = null; });
document.querySelectorAll(".swatch").forEach((b) => b.addEventListener("click", () => {
     document.querySelectorAll(".swatch").forEach((s) => s.classList.toggle("on", s === b));
     ink = b.dataset.color;
}));

function drawnSignature() {
     if (!bounds) throw new Error(SlimIO.t("Draw your signature first."));
     const x0 = Math.max(0, Math.floor(bounds.x0)), y0 = Math.max(0, Math.floor(bounds.y0));
     const x1 = Math.min(pad.width, Math.ceil(bounds.x1)), y1 = Math.min(pad.height, Math.ceil(bounds.y1));
     const c = document.createElement("canvas");
     c.width = x1 - x0;
     c.height = y1 - y0;
     c.getContext("2d").drawImage(pad, x0, y0, c.width, c.height, 0, 0, c.width, c.height);
     return { canvas: c, kind: "signature" };
}

// ---------------------------------------------------------------- signature: type

const FONTS_CSS = "https://fonts.googleapis.com/css2?family=Caveat:wght@600&family=Dancing+Script:wght@600" +
        "&family=Nanum+Brush+Script&family=Nanum+Pen+Script&family=Nanum+Myeongjo:wght@800&display=swap";
const STYLES = [
     { font: '600 {px}px "Dancing Script", "Nanum Pen Script", cursive' },
     { font: '600 {px}px "Caveat", "Nanum Pen Script", cursive' },
     { font: '{px}px "Nanum Pen Script", cursive' },
     { font: '{px}px "Nanum Brush Script", cursive' },
     { seal: true },
];
let styleIdx = 0;
let fontsReady = null;

const FACES = ['600 40px "Dancing Script"', '600 40px "Caveat"', '40px "Nanum Pen Script"',
        '40px "Nanum Brush Script"', '800 40px "Nanum Myeongjo"'];

function loadFonts() {
     if (fontsReady) return fontsReady;
     const link = document.createElement("link");
     link.rel = "stylesheet";
     link.href = FONTS_CSS;
     document.head.appendChild(link);
     fontsReady = new Promise((resolve) => {
             link.addEventListener("load", resolve, { once: true });
             link.addEventListener("error", resolve, { once: true });
     });
     return fontsReady;
}

// Korean web fonts come in unicode-range slices, and canvas text won't fetch a
// missing slice by itself — so load the glyphs for this exact text first.
async function ensureGlyphs(text) {
     await loadFonts();
     const load = Promise.all(FACES.map((f) => document.fonts.load(f, text).catch(() => {})));
     await Promise.race([load, new Promise((r) => setTimeout(r, 4000))]);   // never hang on a slow font
}

function textCanvas(text, style, color) {
     const px = 110;
     const font = style.font.replace("{px}", px);
     const probe = document.createElement("canvas").getContext("2d");
     probe.font = font;
     const w = Math.ceil(probe.measureText(text).width);
     const c = document.createElement("canvas");
     c.width = Math.max(40, w + px * 0.5);
     c.height = Math.round(px * 1.5);
     const ctx = c.getContext("2d");
     ctx.font = font;
     ctx.fillStyle = color;
     ctx.textBaseline = "middle";
     ctx.fillText(text, px * 0.25, c.height / 2);
     return c;
}

// A round red name seal (도장). Korean names read top-to-bottom, right-to-left.
function sealCanvas(text) {
     const size = 280, mid = size / 2, red = "#c8102e";
     const c = document.createElement("canvas");
     c.width = c.height = size;
     const ctx = c.getContext("2d");
     ctx.strokeStyle = ctx.fillStyle = red;
     ctx.lineWidth = 14;
     ctx.beginPath();
     ctx.arc(mid, mid, mid - 12, 0, Math.PI * 2);
     ctx.stroke();
     ctx.textAlign = "center";
     ctx.textBaseline = "middle";
     const chars = [...text.replace(/\s+/g, "")].slice(0, 4);
     const font = (px) => `800 ${px}px "Nanum Myeongjo", serif`;
     if (!/[ㄱ-힝]/.test(text)) {   // not Hangul: one line, fitted inside the ring
             const word = text.trim().slice(0, 12);
             ctx.font = font(100);
             const px = Math.min(100, (100 * (size - 70)) / Math.max(1, ctx.measureText(word).width));
             ctx.font = font(px);
             ctx.fillText(word, mid, mid);
             return c;
     }
     const at = {
             1: [[0, 0, 150]],
             2: [[0, -52, 96], [0, 52, 96]],
             3: [[0, -70, 70], [0, 0, 70], [0, 70, 70]],
             4: [[48, -48, 88], [48, 48, 88], [-48, -48, 88], [-48, 48, 88]],
     }[chars.length];
     chars.forEach((ch, i) => {
             const [dx, dy, px] = at[i];
             ctx.font = font(px);
             ctx.fillText(ch, mid + dx, mid + dy + px * 0.04);
     });
     return c;
}

async function renderStyles() {
     const box = $("styles");
     const text = $("name").value.trim() || SlimIO.t("Your name");
     await ensureGlyphs(text);
     if (text !== ($("name").value.trim() || SlimIO.t("Your name"))) return;   // the name changed meanwhile
     box.replaceChildren(...STYLES.map((s, i) => {
             const b = document.createElement("button");
             b.type = "button";
             b.className = "style" + (i === styleIdx ? " on" : "");
             if (s.seal) b.title = SlimIO.t("Seal");
             b.appendChild(s.seal ? sealCanvas(text) : textCanvas(text, s, "#111111"));
             b.addEventListener("click", () => { styleIdx = i; renderStyles(); });
             return b;
     }));
}

$("name").addEventListener("input", () => renderStyles());

async function typedSignature() {
     const text = $("name").value.trim();
     if (!text) throw new Error(SlimIO.t("Type your name first."));
     await ensureGlyphs(text);
     const s = STYLES[styleIdx];
     return s.seal ? { canvas: sealCanvas(text), kind: "seal" } : { canvas: textCanvas(text, s, "#111111"), kind: "signature" };
}

// ---------------------------------------------------------------- signature: upload

let uploaded = null;   // decoded image, before background removal

async function decode(f) {
     try {
             if (window.createImageBitmap) return await createImageBitmap(f, { imageOrientation: "from-image" });
     } catch (e) { /* fall back to <img> below */ }
     const url = URL.createObjectURL(f);
     try {
             const img = new Image();
             img.src = url;
             await img.decode();
             return img;
     } catch (e) {
             throw new Error(SlimIO.t("This image can't be opened in this browser (HEIC photos, for example). Save it as JPG and try again."));
     } finally {
             URL.revokeObjectURL(url);
     }
}

// Near-white pixels become transparent (with a soft edge), then crop to the ink.
function uploadCanvas() {
     const s = Math.min(1, 1200 / Math.max(uploaded.width, uploaded.height));
     const c = document.createElement("canvas");
     c.width = Math.round(uploaded.width * s);
     c.height = Math.round(uploaded.height * s);
     const ctx = c.getContext("2d");
     ctx.drawImage(uploaded, 0, 0, c.width, c.height);
     if (!$("knockout").checked) return c;
     const data = ctx.getImageData(0, 0, c.width, c.height);
     const p = data.data;
     let x0 = c.width, y0 = c.height, x1 = -1, y1 = -1;
     for (let i = 0; i < p.length; i += 4) {
             const lum = 0.299 * p[i] + 0.587 * p[i + 1] + 0.114 * p[i + 2];
             const a = lum >= 225 ? 0 : lum <= 170 ? 255 : Math.round(((225 - lum) / 55) * 255);
             p[i + 3] = Math.min(p[i + 3], a);
             if (p[i + 3] > 24) {
                     const px = (i / 4) % c.width, py = Math.floor(i / 4 / c.width);
                     if (px < x0) x0 = px; if (px > x1) x1 = px; if (py < y0) y0 = py; if (py > y1) y1 = py;
             }
     }
     ctx.putImageData(data, 0, 0);
     if (x1 < 0) return c;
     const out = document.createElement("canvas");
     out.width = x1 - x0 + 1;
     out.height = y1 - y0 + 1;
     out.getContext("2d").drawImage(c, x0, y0, out.width, out.height, 0, 0, out.width, out.height);
     return out;
}

function showUpload() {
     $("upimg").src = uploaded ? uploadCanvas().toDataURL("image/png") : "";
}

$("pickimg").addEventListener("click", () => $("sigfile").click());
$("sigfile").addEventListener("change", async () => {
     const f = $("sigfile").files[0];
     if (!f) return;
     SlimIO.clearError();
     try { uploaded = await decode(f); showUpload(); } catch (e) { SlimIO.showError(e.message); }
});
$("knockout").addEventListener("change", showUpload);

function uploadedSignature() {
     if (!uploaded) throw new Error(SlimIO.t("Choose a signature image first."));
     return { canvas: uploadCanvas(), kind: "signature" };
}

// ---------------------------------------------------------------- tabs & adding

document.querySelectorAll(".tab").forEach((b) => b.addEventListener("click", async () => {
     mode = b.dataset.mode;
     document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("on", t === b));
     for (const m of ["draw", "type", "upload"]) $("panel-" + m).classList.toggle("hidden", m !== mode);
     if (mode === "draw") sizePad();
     if (mode === "type") renderStyles();
}));

function toPng(canvas) {
     return new Promise((resolve, reject) => canvas.toBlob(async (b) => {
             if (!b) return reject(new Error("toBlob failed"));
             resolve(new Uint8Array(await b.arrayBuffer()));
     }, "image/png"));
}

$("add").addEventListener("click", async () => {
     if (!viewer) return;
     SlimIO.clearError();
     try {
             const sig = mode === "draw" ? drawnSignature() : mode === "type" ? await typedSignature() : uploadedSignature();
             const png = await toPng(sig.canvas);
             const img = { png, url: URL.createObjectURL(new Blob([png], { type: "image/png" })), w: sig.canvas.width, h: sig.canvas.height };
             // a seal is about 2 cm across; a signature about a third of the page wide
             const w = sig.kind === "seal" ? 56 : Math.min(pageSize.w * 0.32, 190);
             const h = (w * img.h) / img.w;
             const nth = items.filter((it) => it.page === pageNo).length;
             items.push({
                     page: pageNo, img, w, h,
                     x: clamp(pageSize.w * 0.88 - w - nth * 14, 0, pageSize.w - w),
                     y: clamp(pageSize.h * 0.86 - h - nth * 14, 0, pageSize.h - h),
             });
             drawItems();
             updateGo();
     } catch (e) {
             SlimIO.showError(e.message);
     }
});

// ---------------------------------------------------------------- save

async function sign() {
     if (!items.length) { SlimIO.showError(SlimIO.t("Add a signature to the page first.")); return; }
     SlimIO.clearError();
     goBtn.disabled = true;
     goBtn.textContent = SlimIO.t("Signing…");
     prog.show();
     result.style.display = "none";
     try {
             const check = await SlimIO.consume();
             if (check && !check.ok) { SlimIO.showError(SlimIO.t("Daily limit reached. Come back tomorrow.")); return; }

             const doc = await PDFDocument.load(bytes);
             const embedded = new Map();
             for (let i = 0; i < items.length; i++) {
                     const it = items[i];
                     if (!embedded.has(it.img)) embedded.set(it.img, await doc.embedPng(it.img.png));
                     const page = doc.getPage(it.page - 1);
                     const v = SlimIO.page2user(page);
                     // visual top-left box -> the image's visual bottom-left corner in user space
                     const p = v.map(it.x, v.height - it.y - it.h);
                     page.drawImage(embedded.get(it.img), { x: p.x, y: p.y, width: it.w, height: it.h, rotate: degrees(p.angle) });
                     prog.set(((i + 1) / items.length) * 100);
             }
             const out = await doc.save();
             showResult(doc.getPageCount(), items.length, out);
     } catch (e) {
             SlimIO.showError(SlimIO.t("Sign failed: {msg}", { msg: e.message }));
     } finally {
             updateGo();
             goBtn.textContent = SlimIO.t("Sign & download");
             prog.hide();
     }
}

function showResult(pages, count, out) {
     result.style.display = "block";
     $("after").textContent = SlimIO.pages(pages);
     $("count").textContent = SlimIO.t(count === 1 ? "{n} signature" : "{n} signatures", { n: count });
     const name = file.name.replace(/\.pdf$/i, "") + "_signed.pdf";
     dl.onclick = () => SlimIO.download(out, name, "application/pdf");
}

goBtn.addEventListener("click", sign);
drop.addEventListener("click", () => $("pdf").click());
$("pdf").addEventListener("change", () => setFile($("pdf").files[0]));
drop.addEventListener("dragover", (e) => { e.preventDefault(); drop.classList.add("drag"); });
drop.addEventListener("dragleave", () => drop.classList.remove("drag"));
drop.addEventListener("drop", (e) => {
     e.preventDefault();
     drop.classList.remove("drag");
     if (e.dataTransfer.files.length) setFile(e.dataTransfer.files[0]);
});

SlimIO.refreshStatus();
