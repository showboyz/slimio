const drop = $("drop");
const controls = $("controls");
const goBtn = $("go");
const result = $("result");
const list = $("list");
const dlzip = $("dlzip");
const prog = SlimIO.bindProgress("prog");

// ID photo presets: crop to this shape from the center, then scale to these pixels
const PRESETS = { "id-3x4": [354, 472], passport: [413, 531], "us-visa": [600, 600], "bank-photo": [200, 230],
     "kr-qnet": [300, 400], "kr-gosi": [137, 177], "kr-history": [120, 160] };
// Korean exam sites: picking the size also picks a KB limit that passes their upload check
// (Q-Net: JPG ≤200KB; civil service: notices say under 100KB or 350KB; history exam: none stated).
const PRESET_TARGET = { "kr-qnet": "200KB", "kr-gosi": "100KB", "kr-history": "100KB" };
// Face guide drawn on the crop frame, as fractions of the frame: head oval (centre y, radii)
// and, for US visas, the band the eyes must sit in (31–44% from the top = 56–69% from the bottom).
const GUIDES = {
     default: { cy: 0.44, rx: 0.29, ry: 0.33 },
     "us-visa": { cy: 0.38, rx: 0.22, ry: 0.3, eyes: [0.31, 0.44] },   // head ≈ 60% (rule: 50–69%), eyes mid-band
};
const EXT = { jpeg: "jpg", webp: "webp", png: "png" };

// "200KB" -> bytes. Decimal (1KB = 1000 bytes) so the file passes whichever
// definition an upload form checks against.
// Also "20-50KB": a range, for forms with a minimum. parseSize gives the maximum.
function parseSize(s) {
     const m = String(s).match(/^(?:\d+-)?(\d+(?:\.\d+)?)\s*(kb|mb)$/i);
     return m ? Math.round(parseFloat(m[1]) * (m[2].toLowerCase() === "mb" ? 1e6 : 1e3)) : 0;
}
// Minimums use 1KB = 1024 bytes (the larger reading), maximums 1000: the file passes either way.
function parseMin(s) {
     const m = String(s).match(/^(\d+)-\d+\s*kb$/i);
     return m ? parseInt(m[1], 10) * 1024 : 0;
}

// A file under a form's minimum can't honestly get bigger as a picture, so we add inert
// padding: a JPEG comment segment right after SOI. Viewers ignore it; the image is unchanged.
async function padJpeg(blob, min) {
     const bytes = new Uint8Array(await blob.arrayBuffer());
     const need = min - bytes.length + 256;
     if (need <= 256) return blob;
     const segs = [];
     for (let left = need; left > 0;) {
             const n = Math.min(left, 65000);
             const seg = new Uint8Array(4 + n).fill(0x20);
             seg[0] = 0xff; seg[1] = 0xfe; seg[2] = ((n + 2) >> 8) & 0xff; seg[3] = (n + 2) & 0xff;
             segs.push(seg);
             left -= n;
     }
     return new Blob([bytes.subarray(0, 2), ...segs, bytes.subarray(2)], { type: "image/jpeg" });
}

let files = [];
let urls = [];   // object URLs from the last run, revoked before the next one

function setFiles(fileList) {
     const picked = [...fileList].filter((f) => f.type.startsWith("image/") || /\.(heic|heif)$/i.test(f.name));
     if (!picked.length) { SlimIO.showError(SlimIO.t("Please choose image files (JPG, PNG, WebP…).")); return; }
     SlimIO.clearError();
     files = picked;
     const total = files.reduce((s, f) => s + f.size, 0);
     drop.querySelector(".drop-title").textContent = files.length === 1
             ? files[0].name
             : SlimIO.t("{n} images", { n: files.length });
     drop.querySelector(".drop-or").textContent = SlimIO.formatSize(total);
     controls.classList.remove("hidden");
     result.style.display = "none";
     goBtn.disabled = false;
     SlimIO.refreshStatus();
     loadPreview();
}

drop.addEventListener("click", () => $("images").click());
$("images").addEventListener("change", () => setFiles($("images").files));
drop.addEventListener("dragover", (e) => { e.preventDefault(); drop.classList.add("drag"); });
drop.addEventListener("dragleave", () => drop.classList.remove("drag"));
drop.addEventListener("drop", (e) => {
     e.preventDefault();
     drop.classList.remove("drag");
     if (e.dataTransfer.files.length) setFiles(e.dataTransfer.files);
});

goBtn.addEventListener("click", run);

// Decode with EXIF orientation applied. HEIC and other formats the browser can't
// read end up in the catch.
async function loadImage(file) {
     try {
             if (window.createImageBitmap) return await createImageBitmap(file, { imageOrientation: "from-image" });
     } catch (e) { /* fall back to <img> below */ }
     const url = URL.createObjectURL(file);
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

// Resize choice: a preset key, a max side ("1920"), or [w, h] for a custom pixel size.
// null when the custom size is out of range.
function resizeChoice() {
     const v = $("resize").value;
     if (v !== "custom") return v;
     const w = Math.round(Number($("cw").value)), h = Math.round(Number($("ch").value));
     return w >= 16 && w <= 4000 && h >= 16 && h <= 4000 ? [w, h] : null;
}
function syncCustom() {
     $("custom").hidden = $("resize").value !== "custom";
}
$("resize").addEventListener("change", syncCustom);

// Size tiles (ID photo page): a friendlier front for the Resize select.
const tiles = document.querySelectorAll(".preset[data-resize]");
function syncTiles() {
     tiles.forEach((t) => t.classList.toggle("on", t.dataset.resize === $("resize").value));
}
tiles.forEach((t) => t.addEventListener("click", () => {
     $("resize").value = t.dataset.resize;
     $("resize").dispatchEvent(new Event("change"));
}));
$("resize").addEventListener("change", syncTiles);
$("resize").addEventListener("change", () => {
     const t = PRESET_TARGET[$("resize").value];
     if (t) { $("target").value = t; $("target").dispatchEvent(new Event("change")); }
});
$("target").addEventListener("change", () => { $("krange").hidden = $("target").value !== "custom"; });
$("krange").hidden = $("target").value !== "custom";

// Pasted form requirements -> exact pixel size, KB range and format (js/specs.js).
function applySpecs() {
     const out = $("specsout");
     const r = SlimSpecs.parse($("specs").value);
     if (!r) { out.hidden = true; return; }
     const found = [];
     if (r.w && r.h) {
             $("resize").value = "custom"; $("cw").value = r.w; $("ch").value = r.h;
             $("resize").dispatchEvent(new Event("change"));
             found.push(`${r.w}×${r.h} px`);
     }
     if (r.minKB || r.maxKB) {
             $("target").value = "custom"; $("krange").hidden = false;
             $("kmin").value = r.minKB || ""; $("kmax").value = r.maxKB || "";
             found.push(r.minKB && r.maxKB ? `${r.minKB}–${r.maxKB} KB` : r.maxKB ? SlimIO.t("under {kb} KB", { kb: r.maxKB }) : SlimIO.t("at least {kb} KB", { kb: r.minKB }));
     }
     if (r.format) { $("format").value = r.format; found.push(r.format === "png" ? "PNG" : "JPG"); }
     out.hidden = false;
     out.className = "specs-out" + (found.length ? "" : " none");
     out.textContent = found.length
             ? "✓ " + SlimIO.t("Set to") + " " + found.join(" · ") + (r.notes.includes("no-dpi") ? " — " + SlimIO.t("cm/mm converted at 200 dpi; check the result") : "")
             : SlimIO.t("Couldn't find sizes in that text — set them below.");
}
let specsTimer = null;
$("specs").addEventListener("input", () => { clearTimeout(specsTimer); specsTimer = setTimeout(applySpecs, 300); });

// ?resize=bank-photo&target=50KB preselects options (links from guide pages)
{
     const q = new URLSearchParams(location.search);
     for (const [param, id] of [["resize", "resize"], ["target", "target"]]) {
             const v = q.get(param), sel = $(id);
             if (v && [...sel.options].some((o) => o.value === v)) { sel.value = v; sel.dispatchEvent(new Event("change")); }
     }
}
syncTiles();
syncCustom();   // the browser may restore "custom" on back/refresh

// Source rectangle for a fixed-size output: the largest box of the right shape, shrunk by
// `crop.z` and centered on (crop.fx, crop.fy) — fractions of the image — or the middle.
function cropRect(w, h, tw, th, crop) {
     const aspect = tw / th;
     let sw = w, sh = h;
     if (w / h > aspect) sw = h * aspect; else sh = w / aspect;
     const z = (crop && crop.z) || 1;
     sw /= z; sh /= z;
     const clamp = (v, lo, hi) => Math.min(Math.max(v, lo), hi);
     const cx = clamp(crop ? crop.fx * w : w / 2, sw / 2, w - sw / 2);
     const cy = clamp(crop ? crop.fy * h : h / 2, sh / 2, h - sh / 2);
     return { sx: cx - sw / 2, sy: cy - sh / 2, sw, sh };
}

function geometry(w, h, resize, crop) {
     const box = Array.isArray(resize) ? resize : PRESETS[resize];
     if (box) {
             const [tw, th] = box;
             return { ...cropRect(w, h, tw, th, crop), dw: tw, dh: th, fixed: true };
     }
     const max = parseInt(resize, 10) || 0;
     const s = max && Math.max(w, h) > max ? max / Math.max(w, h) : 1;
     return { sx: 0, sy: 0, sw: w, sh: h, dw: Math.round(w * s), dh: Math.round(h * s), fixed: false };
}

// True if a JPEG carries an APP1 segment (EXIF/XMP: location, orientation, ...).
function jpegHasApp1(b) {
     for (let i = 2; i + 4 <= b.length && b[i] === 0xff;) {
             const marker = b[i + 1];
             if (marker === 0xe1) return true;
             if (marker === 0xda) return false;   // image data starts; no more metadata
             i += 2 + ((b[i + 2] << 8) | b[i + 3]);
     }
     return false;
}

function draw(img, g, scale, format) {
     const c = document.createElement("canvas");
     c.width = Math.max(1, Math.round(g.dw * scale));
     c.height = Math.max(1, Math.round(g.dh * scale));
     const ctx = c.getContext("2d");
     if (format === "jpeg") { ctx.fillStyle = "#fff"; ctx.fillRect(0, 0, c.width, c.height); }   // JPG has no transparency
     ctx.imageSmoothingQuality = "high";
     ctx.drawImage(img, g.sx, g.sy, g.sw, g.sh, 0, 0, c.width, c.height);
     return c;
}

function encode(canvas, format, quality) {
     return new Promise((resolve, reject) =>
             canvas.toBlob((b) => (b ? resolve(b) : reject(new Error("encode failed"))), "image/" + format, quality));
}

// Best-looking image that fits `target` bytes: search JPEG/WebP quality first,
// then scale down 20% at a time. PNG is lossless, so only scaling helps there.
async function compressOne(file, opts, crop) {
     const img = await loadImage(file);
     try {
             const r = await shrink(img, opts, crop);
             // Never hand back a bigger file than the user gave us when nothing else had to change.
             // A JPEG with EXIF still gets the re-encoded copy, so location data is always removed.
             const unchanged = file.type === "image/" + opts.format && r.w === img.width && r.h === img.height;
             if (unchanged && r.blob.size >= file.size && (!opts.target || file.size <= opts.target)) {
                     const orig = new Uint8Array(await file.arrayBuffer());
                     if (opts.format !== "jpeg" || !jpegHasApp1(orig)) return { blob: file, w: img.width, h: img.height, fits: true, kept: true };
             }
             return r;
     } finally {
             if (img.close) img.close();
     }
}

async function shrink(img, opts, crop) {
     const g = geometry(img.width, img.height, opts.resize, crop);
     const lossy = opts.format !== "png";
     if (!opts.target) {
             const c = draw(img, g, 1, opts.format);
             return { blob: await encode(c, opts.format, lossy ? 0.82 : undefined), w: c.width, h: c.height, fits: true };
     }
     let smallest = null;
     for (let scale = 1, step = 0; step < 10; step++, scale *= 0.8) {
             const c = draw(img, g, scale, opts.format);
             const out = (blob) => ({ blob, w: c.width, h: c.height });
             if (!lossy) {
                     const b = await encode(c, opts.format);
                     if (b.size <= opts.target) return { ...out(b), fits: true };
                     if (!smallest || b.size < smallest.blob.size) smallest = out(b);
             } else {
                     let hi = 0.92, lo = 0.3;
                     const top = await encode(c, opts.format, hi);
                     if (top.size <= opts.target) return { ...out(top), fits: true };
                     let fit = await encode(c, opts.format, lo);
                     if (fit.size <= opts.target) {
                             for (let i = 0; i < 6; i++) {
                                     const mid = (lo + hi) / 2;
                                     const b = await encode(c, opts.format, mid);
                                     if (b.size <= opts.target) { fit = b; lo = mid; } else hi = mid;
                             }
                             return { ...out(fit), fits: true };
                     }
                     if (!smallest || fit.size < smallest.blob.size) smallest = out(fit);
             }
             if (g.fixed) break;   // ID photos and custom sizes must keep their pixel size
     }
     return { ...smallest, fits: false };
}

// ---- crop preview: shown for ID / passport / custom sizes, set on the first photo ----
const cropBox = $("crop");
const cv = $("cropcv");
const zoom = $("zoom");
let preview = null;           // decoded first photo
let crop = { fx: 0.5, fy: 0.5, z: 1 };
let view = null;              // how the photo is laid out on the canvas: { s, ox, oy }

async function loadPreview() {
     if (preview && preview.close) preview.close();
     preview = null;
     crop = { fx: 0.5, fy: 0.5, z: 1 };
     zoom.value = 100;
     try { preview = await loadImage(files[0]); } catch (e) { /* HEIC etc: the run shows the error */ }
     syncCrop();
}

function outputBox() {
     const r = resizeChoice();
     return Array.isArray(r) ? r : PRESETS[r] || null;
}

function cropState() {
     return cropBox.hidden ? null : { ...crop };
}

function syncCrop() {
     const box = outputBox();
     cropBox.hidden = !(preview && box);
     if (cropBox.hidden) return;
     $("crophint").textContent = files.length > 1
             ? SlimIO.t("Drag the frame to set the crop on the first photo. The others are cropped from the center.")
             : $("resize").value === "us-visa"
             ? SlimIO.t("Drag the frame and zoom: head inside the oval, eyes between the two dotted lines.")
             : SlimIO.t("Drag the frame so your face sits inside the guide.");
     drawCrop();
}

function drawCrop() {
     const box = outputBox();
     if (!preview || !box) return;
     const dpr = window.devicePixelRatio || 1;
     const W = cv.clientWidth || 520;
     const H = Math.min(420, Math.round(W * preview.height / preview.width));
     cv.style.height = H + "px";
     cv.width = Math.round(W * dpr);
     cv.height = Math.round(H * dpr);
     const ctx = cv.getContext("2d");
     ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
     const s = Math.min(W / preview.width, H / preview.height);
     view = { s, ox: (W - preview.width * s) / 2, oy: (H - preview.height * s) / 2 };
     ctx.clearRect(0, 0, W, H);
     ctx.drawImage(preview, view.ox, view.oy, preview.width * s, preview.height * s);

     const r = cropRect(preview.width, preview.height, box[0], box[1], crop);
     const x = view.ox + r.sx * s, y = view.oy + r.sy * s, w = r.sw * s, h = r.sh * s;
     // dim everything outside the frame
     ctx.fillStyle = "rgba(8, 10, 14, 0.62)";
     ctx.beginPath();
     ctx.rect(0, 0, W, H);
     ctx.rect(x, y, w, h);
     ctx.fill("evenodd");
     // frame + face guide (head roughly 70% of the photo height, eyes a little above the middle)
     ctx.strokeStyle = "#46e0a0";
     ctx.lineWidth = 2;
     ctx.strokeRect(x + 1, y + 1, w - 2, h - 2);
     ctx.setLineDash([5, 5]);
     ctx.strokeStyle = "rgba(255, 255, 255, 0.75)";
     ctx.lineWidth = 1.5;
     const gd = GUIDES[$("resize").value] || GUIDES.default;
     ctx.beginPath();
     ctx.ellipse(x + w / 2, y + h * gd.cy, w * gd.rx, h * gd.ry, 0, 0, Math.PI * 2);
     ctx.stroke();
     if (gd.eyes) {
             ctx.strokeStyle = "rgba(70, 224, 160, 0.8)";
             ctx.setLineDash([3, 6]);
             for (const f of gd.eyes) {
                     ctx.beginPath();
                     ctx.moveTo(x + w * 0.12, y + h * f);
                     ctx.lineTo(x + w * 0.88, y + h * f);
                     ctx.stroke();
             }
     }
     ctx.setLineDash([]);
}

// Drag anywhere on the photo: the frame follows the pointer.
let drag = null;
cv.addEventListener("pointerdown", (e) => {
     if (!view) return;
     cv.setPointerCapture(e.pointerId);
     cv.classList.add("dragging");
     drag = { x: e.offsetX, y: e.offsetY, fx: crop.fx, fy: crop.fy };
     const r = cropRect(preview.width, preview.height, ...outputBox(), crop);
     const px = (e.offsetX - view.ox) / view.s, py = (e.offsetY - view.oy) / view.s;
     if (px < r.sx || px > r.sx + r.sw || py < r.sy || py > r.sy + r.sh) {   // outside the frame: jump there
             crop.fx = px / preview.width;
             crop.fy = py / preview.height;
             settle();
             drag = { x: e.offsetX, y: e.offsetY, fx: crop.fx, fy: crop.fy };
             drawCrop();
     }
});
cv.addEventListener("pointermove", (e) => {
     if (!drag) return;
     crop.fx = drag.fx + (e.offsetX - drag.x) / view.s / preview.width;
     crop.fy = drag.fy + (e.offsetY - drag.y) / view.s / preview.height;
     settle();
     drawCrop();
});
const endDrag = () => { drag = null; cv.classList.remove("dragging"); };
cv.addEventListener("pointerup", endDrag);
cv.addEventListener("pointercancel", endDrag);

// Keep the stored center where the frame actually is (the frame can't leave the photo).
function settle() {
     const r = cropRect(preview.width, preview.height, ...outputBox(), crop);
     crop.fx = (r.sx + r.sw / 2) / preview.width;
     crop.fy = (r.sy + r.sh / 2) / preview.height;
}

zoom.addEventListener("input", () => { crop.z = zoom.value / 100; settle(); drawCrop(); });
$("cropreset").addEventListener("click", () => { crop = { fx: 0.5, fy: 0.5, z: 1 }; zoom.value = 100; drawCrop(); });
$("resize").addEventListener("change", syncCrop);
$("cw").addEventListener("input", syncCrop);
$("ch").addEventListener("input", syncCrop);
window.addEventListener("resize", () => { if (!cropBox.hidden) drawCrop(); });

async function run() {
     if (!files.length) return;
     SlimIO.clearError();
     const resize = resizeChoice();
     if (!resize) { SlimIO.showError(SlimIO.t("Enter a width and height between 16 and 4000 pixels.")); return; }
     goBtn.disabled = true;
     goBtn.textContent = SlimIO.t("Compressing…");
     prog.show();
     result.style.display = "none";
     urls.forEach((u) => URL.revokeObjectURL(u));
     urls = [];
     const label = $("target").value;
     const custom = label === "custom";
     const opts = custom
             ? { target: Number($("kmax").value) > 0 ? Number($("kmax").value) * 1000 : 0,
                 min: Number($("kmin").value) > 0 ? Number($("kmin").value) * 1024 : 0, resize, format: $("format").value }
             : { target: parseSize(label), min: parseMin(label), resize, format: $("format").value };
     try {
             const check = await SlimIO.consume();
             if (check && !check.ok) { SlimIO.showError(SlimIO.t("Daily limit reached. Come back tomorrow.")); return; }

             const done = [];
             for (let i = 0; i < files.length; i++) {
                     const file = files[i];
                     try {
                             const r = await compressOne(file, opts, i === 0 ? cropState() : null);   // the frame is set on the first photo
                             if (opts.min && opts.format === "jpeg" && r.blob.size < opts.min) {
                                     r.blob = await padJpeg(r.blob, opts.min);
                                     r.padded = true;
                             }
                             done.push({ file, ...r, name: file.name.replace(/\.[^.]+$/, "") + "_slimio." + EXT[opts.format] });
                     } catch (e) {
                             done.push({ file, error: e.message });
                     }
                     prog.set(((i + 1) / files.length) * 100);
             }
             showResult(done, label === "custom" ? ($("kmax").value ? $("kmax").value + "KB" : "") : label);
     } catch (e) {
             SlimIO.showError(SlimIO.t("Compression failed: {msg}", { msg: e.message }));
     } finally {
             goBtn.disabled = false;
             goBtn.textContent = SlimIO.t("Compress images");
             prog.hide();
     }
}

function showResult(done, label) {
     list.replaceChildren();
     let before = 0, after = 0;
     const ok = done.filter((d) => d.blob);
     for (const d of done) {
             const li = document.createElement("li");
             const info = document.createElement("div");
             info.className = "info";
             const name = document.createElement("div");
             name.className = "name";
             name.textContent = d.blob ? d.name : d.file.name;
             const meta = document.createElement("div");
             meta.className = "meta";
             if (d.blob) {
                     before += d.file.size;
                     after += d.blob.size;
                     const url = URL.createObjectURL(d.blob);
                     urls.push(url);
                     const thumb = document.createElement("img");
                     thumb.className = "thumb";
                     thumb.src = url;
                     thumb.alt = "";
                     li.appendChild(thumb);
                     meta.textContent = `${SlimIO.formatSize(d.file.size)} → ${SlimIO.formatSize(d.blob.size)} · ${d.w}×${d.h}`;
                     if (d.kept) meta.append(" · " + SlimIO.t("already optimized, kept as is"));
                     if (d.padded) meta.append(" · " + SlimIO.t("padded to the minimum size; the image is unchanged"));
                     if (label && !d.fits) {
                             const warn = document.createElement("span");
                             warn.className = "warn";
                             warn.textContent = " · " + SlimIO.t("✗ over {size}", { size: label });
                             meta.appendChild(warn);
                     }
                     const a = document.createElement("a");
                     a.href = url;
                     a.download = d.name;
                     a.addEventListener("click", () => SlimIO.trackDownload());
                     a.textContent = SlimIO.t("↓ Download");
                     info.append(name, meta);
                     li.append(info, a);
             } else {
                     const warn = document.createElement("span");
                     warn.className = "warn";
                     warn.textContent = d.error;
                     meta.appendChild(warn);
                     info.append(name, meta);
                     li.appendChild(info);
             }
             list.appendChild(li);
     }
     // never round a real file down to "−100%"
     const pct = before ? Math.min(Math.round((1 - after / before) * 100), after > 0 ? 99 : 100) : 0;
     const change = pct > 0 ? `−${pct}%` : pct < 0 ? `+${-pct}%` : "0%";
     $("total").textContent = ok.length
             ? SlimIO.t("Total: {before} → {after} ({change})", { before: SlimIO.formatSize(before), after: SlimIO.formatSize(after), change })
             : "";
     dlzip.style.display = ok.length > 1 ? "inline-block" : "none";
     dlzip.onclick = async (e) => {
             e.preventDefault();
             const zip = new JSZip();
             const used = new Set();
             for (const d of ok) {
                     let n = d.name, k = 1;
                     while (used.has(n)) n = d.name.replace(/(\.[^.]+)$/, `_${k++}$1`);   // same file names in a batch
                     used.add(n);
                     zip.file(n, d.blob);
             }
             const blob = await zip.generateAsync({ type: "blob" });
             SlimIO.download(new Uint8Array(await blob.arrayBuffer()), "slimio_images.zip", "application/zip");
     };
     result.style.display = "block";
}

SlimIO.refreshStatus();
