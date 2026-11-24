// Stamp image maker: a photo of a stamp (도장·직인) on paper becomes a transparent PNG cut to the
// ink, or a round / square name seal is drawn from a typed name. Everything runs in the browser.
const $ = SlimIO.$;
let mode = "photo";
const RED = "#c8102e";   // the same red as the seal in Sign PDF
const MAX_SIDE = 1600;   // photos are worked on at this size at most

// ---------------------------------------------------------------- photo of a stamp

let uploaded = null;   // decoded image
let decoding = null;   // a big phone photo takes a moment; the button waits for it
let runAfterPick = false;   // the button was tapped before a photo was chosen: run once it's picked

// iPhone HEIC photos go through the decoder in lib.js; the button says "Opening HEIC photos…" meanwhile
async function decode(f) {
     const img = await SlimIO.openImage(f, $("pickimg"));
     if (!img) throw new Error(SlimIO.t("This image can't be opened in this browser. Save it as JPG and try again."));
     return img;
}

// Paper → transparent, judged against the paper around each pixel (phone photos are never evenly lit).
// colour "red" also drops everything that isn't red ink: printed text, a pen line, shadows.
function stampFromPhoto(img, colour, again = true) {
     const s = Math.min(1, MAX_SIDE / Math.max(img.width, img.height));
     const c = document.createElement("canvas");
     c.width = Math.max(1, Math.round(img.width * s));
     c.height = Math.max(1, Math.round(img.height * s));
     const ctx = c.getContext("2d", { willReadFrequently: true });
     ctx.drawImage(img, 0, 0, c.width, c.height);
     const W = c.width, H = c.height;
     const data = ctx.getImageData(0, 0, W, H);
     const p = data.data;
     const lum = new Float32Array(W * H);
     for (let i = 0, j = 0; j < lum.length; i += 4, j++) lum[j] = 0.299 * p[i] + 0.587 * p[i + 1] + 0.114 * p[i + 2];
     // the paper's brightness: the bright end of each block, spread one block outward
     const B = Math.max(16, Math.round(Math.max(W, H) / 24)), gw = Math.ceil(W / B), gh = Math.ceil(H / B);
     const paper = new Float32Array(gw * gh);
     const hist = new Uint32Array(256);
     for (let by = 0; by < gh; by++) for (let bx = 0; bx < gw; bx++) {
             hist.fill(0); let n = 0;
             for (let y = by * B; y < Math.min(H, by * B + B); y++) for (let x = bx * B; x < Math.min(W, bx * B + B); x++) { hist[lum[y * W + x] | 0]++; n++; }
             let k = 255, seen = 0;
             while (k > 0 && (seen += hist[k]) < n * 0.1) k--;   // 90th percentile
             paper[by * gw + bx] = k;
     }
     const bg = new Float32Array(gw * gh);
     for (let by = 0; by < gh; by++) for (let bx = 0; bx < gw; bx++) {
             let m = 0;
             for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
                     const yy = by + dy, xx = bx + dx;
                     if (yy >= 0 && yy < gh && xx >= 0 && xx < gw) m = Math.max(m, paper[yy * gw + xx]);
             }
             bg[by * gw + bx] = Math.max(m, 60);
     }
     const paperAt = (x, y) => {   // bilinear between block centres
             const fx = Math.min(Math.max(x / B - 0.5, 0), gw - 1), fy = Math.min(Math.max(y / B - 0.5, 0), gh - 1);
             const x0 = fx | 0, y0 = fy | 0, x1 = Math.min(x0 + 1, gw - 1), y1 = Math.min(y0 + 1, gh - 1), tx = fx - x0, ty = fy - y0;
             return (bg[y0 * gw + x0] * (1 - tx) + bg[y0 * gw + x1] * tx) * (1 - ty) + (bg[y1 * gw + x0] * (1 - tx) + bg[y1 * gw + x1] * tx) * ty;
     };
     const [rr, rg, rb] = hex(colour === "black" ? "#111111" : RED);
     const rows = new Uint32Array(H), cols = new Uint32Array(W);
     for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
             const j = y * W + x, i = j * 4;
             const r = lum[j] / paperAt(x, y);
             let a = r >= 0.88 ? 0 : r <= 0.66 ? 255 : Math.round(((0.88 - r) / 0.22) * 255);
             const chroma = Math.max(p[i], p[i + 1], p[i + 2]) - Math.min(p[i], p[i + 1], p[i + 2]);
             if (chroma >= 70 && lum[j] < 200) a = 255;   // solid coloured ink stays even where it fills a block
             if (colour === "red") {
                     // how much redder than green and blue: faded pink ink counts, grey print and shadows don't
                     const red = p[i] - Math.max(p[i + 1], p[i + 2]);
                     a = Math.min(a, red <= 28 ? 0 : red >= 70 ? 255 : Math.round(((red - 28) / 42) * 255));
             }
             a = Math.min(p[i + 3], a);
             p[i + 3] = a;
             if (colour !== "keep" && a) { p[i] = rr; p[i + 1] = rg; p[i + 2] = rb; }
             if (a > 24) { rows[y]++; cols[x]++; }
     }
     // crop to the ink; a stray speck or two doesn't count
     let x0 = 0, x1 = W - 1, y0 = 0, y1 = H - 1;
     const few = Math.max(2, Math.round(Math.min(W, H) / 400));
     while (x0 < W && cols[x0] < few) x0++;
     while (x1 >= 0 && cols[x1] < few) x1--;
     while (y0 < H && rows[y0] < few) y0++;
     while (y1 >= 0 && rows[y1] < few) y1--;
     // (with red, the caller tries again keeping the photo's colour before showing this)
     if (x1 < x0 || y1 < y0 || (x1 - x0) < 8 || (y1 - y0) < 8) throw new Error(SlimIO.t("No stamp found in this photo. Take it on plain white paper, in good light."));
     // A big photo or a whole A4 scan was shrunk to MAX_SIDE above, so the stamp came out small (a 15 mm
     // stamp on a 300 or 600 dpi A4 scan: about 170 px, whatever size was asked for). Now that we know
     // where it is, cut that part of the original, with paper around it, and do it again at full detail.
     if (again && s < 0.98) {
             const m = Math.round(Math.max(x1 - x0, y1 - y0) * 0.15) + 4;
             const sx = Math.max(0, (x0 - m) / s), sy = Math.max(0, (y0 - m) / s);
             const w = Math.min(img.width, (x1 + 1 + m) / s) - sx, h = Math.min(img.height, (y1 + 1 + m) / s) - sy;
             if (w * h < img.width * img.height * 0.6) {   // not most of the photo (then nothing to gain)
                     const k = Math.min(1, MAX_SIDE / Math.max(w, h));   // keeps the canvas small on phones
                     const part = document.createElement("canvas");
                     part.width = Math.max(1, Math.round(w * k));
                     part.height = Math.max(1, Math.round(h * k));
                     part.getContext("2d").drawImage(img, sx, sy, w, h, 0, 0, part.width, part.height);
                     try { return stampFromPhoto(part, colour, false); } catch (e) { /* keep the small result below */ }
             }
     }
     ctx.putImageData(data, 0, 0);
     return pad(c, x0, y0, x1 - x0 + 1, y1 - y0 + 1);
}

// The ink plus a small even margin, so the edge of the stamp is never cut off.
function pad(src, x, y, w, h) {
     const m = Math.round(Math.max(w, h) * 0.04);
     const out = document.createElement("canvas");
     out.width = w + 2 * m;
     out.height = h + 2 * m;
     out.getContext("2d").drawImage(src, x, y, w, h, m, m, w, h);
     return out;
}

function hex(h) { return [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16)); }

SlimIO.acceptHeic($("stampfile"));   // computers: let the file dialog show HEIC files too (lib.js)
$("pickimg").addEventListener("click", () => { runAfterPick = false; $("stampfile").click(); });
$("stampfile").addEventListener("change", async () => {
     const f = $("stampfile").files[0];
     if (!f) return;
     SlimIO.clearError();
     decoding = decode(f);
     try {
             uploaded = await decoding;
             $("pickname").textContent = f.name;
     } catch (e) { uploaded = null; SlimIO.showError(e.message); }
     decoding = null;
     if (uploaded && runAfterPick) goBtn.click();
     runAfterPick = false;
});

// ---------------------------------------------------------------- name seal

const FONTS_CSS = "https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@800&display=swap";
const FACE = '800 40px "Nanum Myeongjo"';
let fontsReady = null;
let shape = "round";

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
     await Promise.race([document.fonts.load(FACE, text).catch(() => {}), new Promise((r) => setTimeout(r, 4000))]);
}

function sealText() {
     let t = $("name").value.trim().replace(/\s+/g, " ");
     if (/[ㄱ-힝]/.test(t)) {   // a Korean name: up to 4 letters, no spaces
             t = [...t.replace(/ /g, "")].slice(0, 4).join("");
             if ($("yin").checked && [...t].length < 4) t += "인";
     }
     return t;
}

// A red name seal, drawn large so it prints sharp. Korean names read top-to-bottom, right-to-left.
function sealCanvas(text, shape, size = 600) {
     const k = size / 280, mid = size / 2;
     const c = document.createElement("canvas");
     c.width = c.height = size;
     const ctx = c.getContext("2d");
     ctx.strokeStyle = ctx.fillStyle = RED;
     ctx.lineWidth = 14 * k;
     ctx.beginPath();
     if (shape === "square") {
             const e = 12 * k, r = 22 * k, w = size - 2 * e;
             ctx.moveTo(e + r, e);
             ctx.arcTo(e + w, e, e + w, e + w, r); ctx.arcTo(e + w, e + w, e, e + w, r);
             ctx.arcTo(e, e + w, e, e, r); ctx.arcTo(e, e, e + w, e, r);
             ctx.closePath();
     } else ctx.arc(mid, mid, mid - 12 * k, 0, Math.PI * 2);
     ctx.stroke();
     ctx.textAlign = "center";
     ctx.textBaseline = "middle";
     const font = (px) => `800 ${px * k}px "Nanum Myeongjo", serif`;
     const chars = [...text];
     if (!/[ㄱ-힝]/.test(text)) {   // not Hangul: one line, fitted inside the ring
             const word = text.slice(0, 12);
             ctx.font = font(100);
             const px = Math.min(100, (100 * (280 - 70)) / Math.max(1, ctx.measureText(word).width / k));
             ctx.font = font(px);
             ctx.fillText(word, mid, mid);
             return c;
     }
     const sq = shape === "square";   // a square seal has room for bigger letters
     const at = {
             1: [[0, 0, sq ? 170 : 150]],
             2: [[0, -54, sq ? 104 : 96], [0, 54, sq ? 104 : 96]],
             3: [[0, -72, sq ? 74 : 70], [0, 0, sq ? 74 : 70], [0, 72, sq ? 74 : 70]],
             4: [[50, -50, sq ? 96 : 88], [50, 50, sq ? 96 : 88], [-50, -50, sq ? 96 : 88], [-50, 50, sq ? 96 : 88]],
     }[chars.length];
     chars.forEach((ch, i) => {
             const [dx, dy, px] = at[i];
             ctx.font = font(px);
             ctx.fillText(ch, mid + dx * k, mid + (dy + px * 0.04) * k);
     });
     return c;
}

async function renderShapes() {
     const text = sealText() || SlimIO.t("Hong Gildong");
     await ensureGlyphs(text);
     if (text !== (sealText() || SlimIO.t("Hong Gildong"))) return;   // the name changed meanwhile
     $("shapes").replaceChildren(...["round", "square"].map((s) => {
             const b = document.createElement("button");
             b.type = "button";
             b.className = "style" + (s === shape ? " on" : "");
             b.dataset.shape = s;
             b.title = s === "round" ? SlimIO.t("Round seal") : SlimIO.t("Square seal");
             b.appendChild(sealCanvas(text, s, 160));
             b.addEventListener("click", () => { shape = s; renderShapes(); });
             return b;
     }));
}

$("name").addEventListener("input", () => { SlimIO.inputAdded("type"); renderShapes(); });
$("yin").addEventListener("change", renderShapes);

// ---------------------------------------------------------------- tabs & making

document.querySelectorAll(".tab").forEach((b) => b.addEventListener("click", () => {
     mode = b.dataset.mode;
     document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("on", t === b));
     for (const m of ["photo", "make"]) $("panel-" + m).classList.toggle("hidden", m !== mode);
     $("colourrow").hidden = mode !== "photo";
     if (mode === "make") renderShapes();
}));

// Long side at the chosen size; a small photo is not blown up beyond twice its size.
function sized(src) {
     const want = Number($("size").value) || Math.max(src.width, src.height);
     const long = Math.max(src.width, src.height);
     const k = Math.min(want / long, mode === "photo" ? 2 : 1e9);
     if (Math.abs(k - 1) < 0.01) return src;
     const out = document.createElement("canvas");
     out.width = Math.max(1, Math.round(src.width * k));
     out.height = Math.max(1, Math.round(src.height * k));
     const ctx = out.getContext("2d");
     ctx.imageSmoothingQuality = "high";
     ctx.drawImage(src, 0, 0, out.width, out.height);
     return out;
}

const goBtn = $("go");
let outUrl = null;
let lastStamp = null;   // the canvas behind the latest result

// Hand the stamp to Sign PDF in this tab (sessionStorage: stays in the browser).
$("topdf").addEventListener("click", () => {
     try { if (lastStamp) sessionStorage.setItem("slimio.signature", lastStamp.toDataURL("image/png")); } catch (e) { /* storage off: Sign PDF just opens empty */ }
});

goBtn.addEventListener("click", async () => {
     // Photo tab with no photo yet: open the picker instead of an error (most people tap this first)
     if (mode === "photo" && !uploaded && !decoding) { runAfterPick = true; $("stampfile").click(); return; }
     SlimIO.clearError();
     $("result").style.display = "none";   // never leave an old result next to a new error
     goBtn.disabled = true;
     try {
             let stamp, note = "";
             if (mode === "photo") {
                     if (decoding) await decoding.catch(() => {});
                     if (!uploaded) return;
                     const colour = $("colour").value;
                     try { stamp = stampFromPhoto(uploaded, colour); }
                     catch (e) {
                             // Red is the default, but company and office stamps are often blue, purple or black:
                             // people got "no red stamp", switched the colour by hand and ran it again (Umami, 11/24).
                             // Do that for them, and say so under the result.
                             if (colour !== "red") throw e;
                             stamp = stampFromPhoto(uploaded, "keep");
                             $("colour").value = "keep";
                             note = SlimIO.t("No red ink found, so the stamp keeps the colour it has in the photo.");
                             SlimIO.event("stamp-colour-fallback", { to: "keep" });
                     }
             } else {
                     const text = sealText();
                     if (!text) throw new Error(SlimIO.t("Type your name first."));
                     await ensureGlyphs(text);
                     stamp = sealCanvas(text, shape);
             }
             const check = await SlimIO.consume();
             if (check && !check.ok) { SlimIO.showError(SlimIO.t("Daily limit reached. Come back tomorrow.")); return; }
             const out = sized(stamp);
             const blob = await new Promise((resolve, reject) => out.toBlob((b) => (b ? resolve(b) : reject(new Error("toBlob failed"))), "image/png"));
             lastStamp = out;
             showResult(new Uint8Array(await blob.arrayBuffer()), out, note);
     } catch (e) {
             SlimIO.showError(e.message);
     } finally {
             goBtn.disabled = false;
     }
});

function showResult(bytes, c, note) {
     if (outUrl) URL.revokeObjectURL(outUrl);
     outUrl = URL.createObjectURL(new Blob([bytes], { type: "image/png" }));
     $("outimg").src = outUrl;
     const meta = $("outmeta");
     meta.innerHTML = "";
     const b = document.createElement("b");
     b.textContent = `${c.width}×${c.height}px · ${SlimIO.formatSize(bytes.length)} · PNG`;
     meta.append(b, document.createElement("br"), SlimIO.t("Transparent background: put it on any document."));
     if (note) meta.append(document.createElement("br"), note);
     $("result").style.display = "block";
     $("dl").onclick = () => SlimIO.download(bytes, `stamp_${c.width}x${c.height}.png`, "image/png");
     SlimIO.reveal($("result"));
}

SlimIO.refreshStatus();
