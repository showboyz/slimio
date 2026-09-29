const drop = $("drop");
const controls = $("controls");
const goBtn = $("go");
const result = $("result");
const list = $("list");
const dlzip = $("dlzip");
const prog = SlimIO.bindProgress("prog");

// ID photo presets: crop to this shape from the center, then scale to these pixels
const PRESETS = { "id-3x4": [354, 472], passport: [413, 531] };
const EXT = { jpeg: "jpg", webp: "webp", png: "png" };

// "200KB" -> bytes. Decimal (1KB = 1000 bytes) so the file passes whichever
// definition an upload form checks against.
function parseSize(s) {
     const m = String(s).match(/^(\d+(?:\.\d+)?)\s*(kb|mb)$/i);
     return m ? Math.round(parseFloat(m[1]) * (m[2].toLowerCase() === "mb" ? 1e6 : 1e3)) : 0;
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

function geometry(w, h, resize) {
     if (PRESETS[resize]) {
             const [tw, th] = PRESETS[resize];
             const aspect = tw / th;
             let sw = w, sh = h;
             if (w / h > aspect) sw = h * aspect; else sh = w / aspect;
             return { sx: (w - sw) / 2, sy: (h - sh) / 2, sw, sh, dw: tw, dh: th, fixed: true };
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
async function compressOne(file, opts) {
     const img = await loadImage(file);
     try {
             const r = await shrink(img, opts);
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

async function shrink(img, opts) {
     const g = geometry(img.width, img.height, opts.resize);
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
             if (g.fixed) break;   // ID photos must keep their pixel size
     }
     return { ...smallest, fits: false };
}

async function run() {
     if (!files.length) return;
     SlimIO.clearError();
     goBtn.disabled = true;
     goBtn.textContent = SlimIO.t("Compressing…");
     prog.show();
     result.style.display = "none";
     urls.forEach((u) => URL.revokeObjectURL(u));
     urls = [];
     const label = $("target").value;
     const opts = { target: parseSize(label), resize: $("resize").value, format: $("format").value };
     try {
             const check = await SlimIO.consume();
             if (check && !check.ok) { SlimIO.showError(SlimIO.t("Daily limit reached. Come back tomorrow.")); return; }

             const done = [];
             for (let i = 0; i < files.length; i++) {
                     const file = files[i];
                     try {
                             const r = await compressOne(file, opts);
                             done.push({ file, ...r, name: file.name.replace(/\.[^.]+$/, "") + "_slimio." + EXT[opts.format] });
                     } catch (e) {
                             done.push({ file, error: e.message });
                     }
                     prog.set(((i + 1) / files.length) * 100);
             }
             showResult(done, label);
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
     const pct = before ? Math.round((1 - after / before) * 100) : 0;
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
