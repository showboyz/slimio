// Signature image maker: draw or upload a signature, clean it up, and save a JPG/PNG
// at an exact pixel size and KB range. Everything runs in the browser.
const $ = SlimIO.$;
let mode = "draw";

// ---------------------------------------------------------------- draw

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
sizePad();
window.addEventListener("resize", sizePad);

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
     padCtx.lineWidth = 3 * (window.devicePixelRatio || 1);
     padCtx.lineCap = padCtx.lineJoin = "round";
     padCtx.beginPath();
     padCtx.arc(last.x, last.y, padCtx.lineWidth / 2, 0, Math.PI * 2);
     padCtx.fill();
     grow(last);
});
pad.addEventListener("pointermove", (e) => {
     if (!last) return;
     SlimIO.inputAdded("draw");   // an actual stroke, not just a touch
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
     return c;
}

// ---------------------------------------------------------------- upload

let uploaded = null;   // decoded image, before cleanup

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

// Paper becomes transparent and the result is cropped to the ink. Brightness is judged
// against the paper itself (a bright percentile), so grey-ish phone photos clean up too.
function uploadedSignature() {
     if (!uploaded) throw new Error(SlimIO.t("Choose a signature image first."));
     const s = Math.min(1, 1600 / Math.max(uploaded.width, uploaded.height));
     const c = document.createElement("canvas");
     c.width = Math.round(uploaded.width * s);
     c.height = Math.round(uploaded.height * s);
     const ctx = c.getContext("2d");
     ctx.drawImage(uploaded, 0, 0, c.width, c.height);
     if (!$("knockout").checked) return c;

     const data = ctx.getImageData(0, 0, c.width, c.height);
     const p = data.data;
     const hist = new Uint32Array(256);
     for (let i = 0; i < p.length; i += 4) hist[Math.round(0.299 * p[i] + 0.587 * p[i + 1] + 0.114 * p[i + 2])]++;
     let paper = 255;
     for (let acc = 0, v = 0; v < 256; v++) { acc += hist[v]; if (acc >= 0.7 * (p.length / 4)) { paper = Math.max(v, 60); break; } }

     // Ink is much darker than the paper AND than its own surroundings. The second test keeps
     // a desk or shadow at the photo's edge (dark, but evenly so) from counting as ink.
     const W = c.width, H = c.height;
     const lum = new Float32Array(W * H);
     for (let i = 0, j = 0; j < lum.length; i += 4, j++) lum[j] = 0.299 * p[i] + 0.587 * p[i + 1] + 0.114 * p[i + 2];
     const sat = new Float64Array((W + 1) * (H + 1));   // summed-area table for local means
     for (let y = 0; y < H; y++) {
             let row = 0;
             for (let x = 0; x < W; x++) { row += lum[y * W + x]; sat[(y + 1) * (W + 1) + x + 1] = sat[y * (W + 1) + x + 1] + row; }
     }
     const R = Math.max(8, Math.round(Math.min(W, H) / 40));
     const ramp = (v, full, none) => (v <= full ? 1 : v >= none ? 0 : (none - v) / (none - full));
     const alpha = new Uint8Array(W * H);
     for (let y = 0; y < H; y++) {
             const ya = Math.max(0, y - R), yb = Math.min(H, y + R + 1);
             for (let x = 0; x < W; x++) {
                     const xa = Math.max(0, x - R), xb = Math.min(W, x + R + 1);
                     const mean = (sat[yb * (W + 1) + xb] - sat[ya * (W + 1) + xb] - sat[yb * (W + 1) + xa] + sat[ya * (W + 1) + xa]) / ((xb - xa) * (yb - ya));
                     const l = lum[y * W + x];
                     alpha[y * W + x] = Math.round(255 * Math.min(ramp(l / paper, 0.5, 0.76), ramp(l / mean, 0.62, 0.9)));
             }
     }

     // Keep the ink blobs; drop blobs touching the photo's edge (desk, paper edge, shadow)
     // and specks. If the signature itself touches the edge, fall back to keeping those too.
     const keep = inkBlobs(alpha, p, W, H);
     if (!keep) throw new Error(SlimIO.t("No signature found in the photo. Try a darker pen or a brighter photo."));
     const near = dilate(keep.mask, W, H, 2);   // keep the soft edges around the strokes
     for (let j = 0; j < alpha.length; j++) p[j * 4 + 3] = near[j] ? Math.min(p[j * 4 + 3], alpha[j]) : 0;
     ctx.putImageData(data, 0, 0);
     const m = 2;
     const x0 = Math.max(0, keep.x0 - m), y0 = Math.max(0, keep.y0 - m);
     const x1 = Math.min(W - 1, keep.x1 + m), y1 = Math.min(H - 1, keep.y1 + m);
     const out = document.createElement("canvas");
     out.width = x1 - x0 + 1;
     out.height = y1 - y0 + 1;
     out.getContext("2d").drawImage(c, x0, y0, out.width, out.height, 0, 0, out.width, out.height);
     return out;
}

// 8-connected blobs of solid ink (alpha > 100). Returns the kept pixels and their bounds, or null.
// Brown blobs (wood grain showing past the paper) are dropped; black, blue and red ink stay.
function inkBlobs(alpha, px, W, H) {
     const N = W * H;
     const seen = new Uint8Array(N);
     const order = new Int32Array(N);
     const blobs = [];
     let top = 0;
     for (let s = 0; s < N; s++) {
             if (seen[s] || alpha[s] <= 100) continue;
             const start = top;
             let edge = false, r = 0, g = 0, b = 0, sx = 0, sy = 0;
             seen[s] = 1;
             order[top++] = s;
             for (let q = start; q < top; q++) {
                     const j = order[q], x = j % W, y = (j - x) / W;
                     r += px[j * 4]; g += px[j * 4 + 1]; b += px[j * 4 + 2]; sx += x; sy += y;
                     if (x === 0 || y === 0 || x === W - 1 || y === H - 1) edge = true;
                     for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
                             const nx = x + dx, ny = y + dy;
                             if (nx < 0 || ny < 0 || nx >= W || ny >= H) continue;
                             const k = ny * W + nx;
                             if (!seen[k] && alpha[k] > 100) { seen[k] = 1; order[top++] = k; }
                     }
             }
             const n = top - start;
             r /= n; g /= n; b /= n;
             const brown = r - b > 25 && g - b > 10 && r - g < 60;
             blobs.push({ start, end: top, edge, brown, cx: sx / n, cy: sy / n });
     }
     const minSize = Math.max(6, Math.round(N * 0.00002));
     const big = blobs.filter((b) => b.end - b.start >= minSize);
     let kept = big.filter((b) => !b.edge && !b.brown);
     if (!kept.length) kept = big.filter((b) => !b.brown);
     if (!kept.length) kept = big;
     if (!kept.length) return null;
     // Small marks inside the writing area are part of it — dots on i, periods, commas.
     // Only specks outside it (dust, paper texture) are dropped.
     let bx0 = W, by0 = H, bx1 = -1, by1 = -1;
     for (const b of kept) for (let q = b.start; q < b.end; q++) {
             const j = order[q], x = j % W, y = (j - x) / W;
             if (x < bx0) bx0 = x; if (x > bx1) bx1 = x; if (y < by0) by0 = y; if (y > by1) by1 = y;
     }
     const pad = Math.round(Math.max(W, H) * 0.01);
     kept = kept.concat(blobs.filter((b) => b.end - b.start < minSize && b.end - b.start >= 2 && !b.edge && !b.brown &&
             b.cx >= bx0 - pad && b.cx <= bx1 + pad && b.cy >= by0 - pad && b.cy <= by1 + pad));
     const mask = new Uint8Array(N);
     let x0 = W, y0 = H, x1 = -1, y1 = -1;
     for (const b of kept) for (let q = b.start; q < b.end; q++) {
             const j = order[q], x = j % W, y = (j - x) / W;
             mask[j] = 1;
             if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y;
     }
     return { mask, x0, y0, x1, y1 };
}

// Grow a 0/1 mask by r pixels (square), in two passes.
function dilate(mask, W, H, r) {
     const tmp = new Uint8Array(W * H), out = new Uint8Array(W * H);
     for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
             if (!mask[y * W + x]) continue;
             for (let d = Math.max(0, x - r); d <= Math.min(W - 1, x + r); d++) tmp[y * W + d] = 1;
     }
     for (let x = 0; x < W; x++) for (let y = 0; y < H; y++) {
             if (!tmp[y * W + x]) continue;
             for (let d = Math.max(0, y - r); d <= Math.min(H - 1, y + r); d++) out[d * W + x] = 1;
     }
     return out;
}

$("pickimg").addEventListener("click", () => $("sigfile").click());
$("sigfile").addEventListener("change", async () => {
     const f = $("sigfile").files[0];
     if (!f) return;
     SlimIO.clearError();
     try {
             uploaded = await decode(f);
             $("pickimg").firstChild.textContent = f.name;
     } catch (e) { SlimIO.showError(e.message); }
});

document.querySelectorAll(".tab").forEach((b) => b.addEventListener("click", () => {
     mode = b.dataset.mode;
     document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("on", t === b));
     for (const m of ["draw", "upload"]) $("panel-" + m).classList.toggle("hidden", m !== mode);
     if (mode === "draw") sizePad();
}));

// ---------------------------------------------------------------- output

// Exam document presets (IBPS / SBI guidelines): pixel size, KB range, JPG.
const PRESETS = {
     "bank-sign": { box: [140, 60], target: "10-20",
             hint: "Sign on white paper with a black pen. Signatures in CAPITAL LETTERS are not accepted." },
     "bank-thumb": { box: [240, 240], target: "20-50",
             hint: "Press your left thumb on white paper with black or blue ink, then photograph it." },
     "bank-decl": { box: [800, 400], target: "50-100",
             hint: "Write the declaration text from the notice in English, in black ink, not in capital letters." },
};
function syncSize() {
     const v = $("size").value, p = PRESETS[v];
     $("custom").hidden = v !== "custom";
     $("presethint").hidden = !p;
     if (p) {
             $("presethint").textContent = SlimIO.t(p.hint) + " " + SlimIO.t("Always check the exact numbers in your exam notice.");
             $("target").value = p.target;
             $("format").value = "jpeg";
             if (v !== "bank-sign") document.querySelector('.tab[data-mode="upload"]').click();   // ink on paper: photo it
     }
}
$("size").addEventListener("change", syncSize);
// ?preset=bank-thumb etc. (linked from the exam documents page)
const wanted = new URLSearchParams(location.search).get("preset");
if (wanted && PRESETS[wanted]) $("size").value = wanted;
syncSize();   // the browser may also restore a choice on back/refresh

// Signature on a canvas of the output size: fitted with a small margin (custom size)
// or trimmed with a margin (auto). JPG gets a white background.
function compose(sig, format, box, scale) {
     const margin = 0.08;
     let W, H;
     if (box) [W, H] = box;
     else {
             const cap = Math.min(1, 800 / Math.max(sig.width, sig.height)) * scale;
             W = Math.max(16, Math.round(sig.width * cap * (1 + 2 * margin)));
             H = Math.max(16, Math.round(sig.height * cap * (1 + 2 * margin)));
     }
     const c = document.createElement("canvas");
     c.width = W;
     c.height = H;
     const ctx = c.getContext("2d");
     if (format === "jpeg") { ctx.fillStyle = "#fff"; ctx.fillRect(0, 0, W, H); }
     const s = Math.min((W * (1 - 2 * margin)) / sig.width, (H * (1 - 2 * margin)) / sig.height);
     const w = sig.width * s, h = sig.height * s;
     ctx.imageSmoothingQuality = "high";
     ctx.drawImage(sig, (W - w) / 2, (H - h) / 2, w, h);
     return c;
}

function encode(canvas, format, quality) {
     return new Promise((resolve, reject) =>
             canvas.toBlob((b) => (b ? resolve(b) : reject(new Error("encode failed"))), "image/" + format, quality));
}

// "10-20" -> {min: 10240, max: 20000}; "20" -> {max: 20000}. The maximum uses 1KB = 1000 bytes
// and the minimum 1024, so the file passes whichever definition the form checks.
function parseTarget(v) {
     if (!v) return {};
     const [a, b] = v.split("-").map(Number);
     return b ? { min: a * 1024, max: b * 1000 } : { max: a * 1000 };
}

// Best-looking file under `max`: JPG quality first, then (auto size only) scale down 20% at a time.
async function fit(sig, format, box, max) {
     let smallest = null;
     for (let step = 0, scale = 1; step < 8; step++, scale *= 0.8) {
             const c = compose(sig, format, box, scale);
             const out = (blob) => ({ blob, w: c.width, h: c.height });
             if (format === "png") {
                     const b = await encode(c, "png");
                     if (!max || b.size <= max) return { ...out(b), fits: true };
                     if (!smallest || b.size < smallest.blob.size) smallest = out(b);
             } else {
                     let hi = 1, lo = 0.3;
                     const top = await encode(c, "jpeg", hi);
                     if (!max || top.size <= max) return { ...out(top), fits: true };
                     let best = await encode(c, "jpeg", lo);
                     if (best.size <= max) {
                             for (let i = 0; i < 6; i++) {
                                     const mid = (lo + hi) / 2;
                                     const b = await encode(c, "jpeg", mid);
                                     if (b.size <= max) { best = b; lo = mid; } else hi = mid;
                             }
                             return { ...out(best), fits: true };
                     }
                     if (!smallest || best.size < smallest.blob.size) smallest = out(best);
             }
             if (box) break;   // an exact pixel size must be kept
     }
     return { ...smallest, fits: false };
}

// Some forms also have a minimum size. The picture can't honestly get bigger, so we add
// inert padding: a JPEG comment segment, or a PNG text chunk. Viewers ignore both.
const CRC = (() => {
     const t = new Uint32Array(256);
     for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; }
     return (bytes) => { let c = 0xffffffff; for (const b of bytes) c = t[(c ^ b) & 0xff] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };
})();

function padTo(bytes, format, min) {
     const need = min - bytes.length + 256;   // land a little above the minimum
     if (need <= 256) return bytes;
     if (format === "jpeg") {
             const segs = [];
             for (let left = need; left > 0;) {
                     const n = Math.min(left, 65000);
                     const seg = new Uint8Array(4 + n).fill(0x20);
                     seg[0] = 0xff; seg[1] = 0xfe; seg[2] = ((n + 2) >> 8) & 0xff; seg[3] = (n + 2) & 0xff;
                     segs.push(seg);
                     left -= n;
             }
             const size = bytes.length + segs.reduce((a, s) => a + s.length, 0);
             const out = new Uint8Array(size);
             out.set(bytes.subarray(0, 2), 0);   // SOI, then the comments
             let o = 2;
             for (const s of segs) { out.set(s, o); o += s.length; }
             out.set(bytes.subarray(2), o);
             return out;
     }
     // PNG: tEXt chunk right before IEND (the last 12 bytes)
     const key = new TextEncoder().encode("Comment\0");
     const data = new Uint8Array(key.length + need).fill(0x20);
     data.set(key, 0);
     const type = new TextEncoder().encode("tEXt");
     const chunk = new Uint8Array(12 + data.length);
     new DataView(chunk.buffer).setUint32(0, data.length);
     chunk.set(type, 4);
     chunk.set(data, 8);
     const crcIn = new Uint8Array(4 + data.length);
     crcIn.set(type, 0);
     crcIn.set(data, 4);
     new DataView(chunk.buffer).setUint32(8 + data.length, CRC(crcIn));
     const cut = bytes.length - 12;
     const out = new Uint8Array(bytes.length + chunk.length);
     out.set(bytes.subarray(0, cut), 0);
     out.set(chunk, cut);
     out.set(bytes.subarray(cut), cut + chunk.length);
     return out;
}

function sizeChoice() {
     if (PRESETS[$("size").value]) return PRESETS[$("size").value].box;
     if ($("size").value !== "custom") return null;
     const w = Math.round(Number($("cw").value)), h = Math.round(Number($("ch").value));
     if (!(w >= 16 && w <= 4000 && h >= 16 && h <= 4000)) throw new Error(SlimIO.t("Enter a width and height between 16 and 4000 pixels."));
     return [w, h];
}

const goBtn = $("go");
let outUrl = null;
let lastSig = null;   // the trimmed, transparent signature behind the latest result

// Hand the signature to Sign PDF in this tab (sessionStorage: stays in the browser).
$("topdf").addEventListener("click", () => {
     try { if (lastSig) sessionStorage.setItem("slimio.signature", lastSig.toDataURL("image/png")); } catch (e) { /* storage off: Sign PDF just opens empty */ }
});

goBtn.addEventListener("click", async () => {
     SlimIO.clearError();
     $("result").style.display = "none";   // never leave an old result next to a new error
     let sig, box;
     try {
             box = sizeChoice();
             sig = mode === "draw" ? drawnSignature() : uploadedSignature();
     } catch (e) { SlimIO.showError(e.message); return; }
     const format = $("format").value;
     const { min, max } = parseTarget($("target").value);
     goBtn.disabled = true;
     try {
             const check = await SlimIO.consume();
             if (check && !check.ok) { SlimIO.showError(SlimIO.t("Daily limit reached. Come back tomorrow.")); return; }
             const r = await fit(sig, format, box, max);
             let bytes = new Uint8Array(await r.blob.arrayBuffer());
             const padded = min && bytes.length < min;
             if (padded) bytes = padTo(bytes, format, min);
             lastSig = sig;
             showResult(bytes, r, format, { min, max, padded });
     } catch (e) {
             SlimIO.showError(SlimIO.t("Something went wrong: {msg}", { msg: e.message }));
     } finally {
             goBtn.disabled = false;
     }
});

function showResult(bytes, r, format, t) {
     const type = "image/" + format;
     if (outUrl) URL.revokeObjectURL(outUrl);
     outUrl = URL.createObjectURL(new Blob([bytes], { type }));
     $("outimg").src = outUrl;
     const meta = $("outmeta");
     meta.innerHTML = "";
     const b = document.createElement("b");
     b.textContent = `${r.w}×${r.h}px · ${SlimIO.formatSize(bytes.length)} · ${format === "jpeg" ? "JPG" : "PNG"}`;
     meta.appendChild(b);
     let note = "";
     if (!r.fits) note = format === "png"
             ? SlimIO.t("Still over the limit — choose JPG, which is much smaller.")
             : SlimIO.t("Still over the limit at this pixel size. Try a smaller size.");
     else if (t.padded) note = SlimIO.t("Padded to meet the {kb}KB minimum; the image itself is unchanged.", { kb: Math.round(t.min / 1024) });
     if (note) meta.append(document.createElement("br"), note);
     $("result").style.display = "block";
     const ext = format === "jpeg" ? "jpg" : "png";
     $("dl").onclick = () => SlimIO.download(bytes, `signature_${r.w}x${r.h}.${ext}`, type);
}

SlimIO.refreshStatus();
