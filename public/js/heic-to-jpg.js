// HEIC to JPG: iPhone photos (and anything else the browser opens) saved again as JPG, in the
// browser. HEIC is opened by the decoder in lib.js (SlimIO.openImage), fetched on first use.
const drop = $("drop");
const goBtn = $("go");
const controls = $("controls");
const result = $("result");
const list = $("list");
const dlzip = $("dlzip");
const prog = SlimIO.bindProgress();

let files = [];
let urls = [];

function setFiles(fileList) {
    const picked = [...fileList].filter(SlimIO.isImage);
    if (!picked.length) { SlimIO.showError(SlimIO.t("Please choose HEIC photos or other image files.")); return; }
    SlimIO.clearError();
    files = picked;
    drop.querySelector(".drop-title").textContent = files.length === 1 ? files[0].name : SlimIO.t("{n} images", { n: files.length });
    drop.querySelector(".drop-or").textContent = SlimIO.formatSize(files.reduce((s, f) => s + f.size, 0));
    controls.classList.remove("hidden");
    result.style.display = "none";
    goBtn.disabled = false;
    SlimIO.refreshStatus();
}

SlimIO.acceptHeic($("images"));   // computers: let the file dialog show HEIC files too (lib.js)
drop.addEventListener("click", () => $("images").click());
$("images").addEventListener("change", (e) => { setFiles(e.target.files); e.target.value = ""; });
drop.addEventListener("dragover", (e) => { e.preventDefault(); drop.classList.add("drag"); });
drop.addEventListener("dragleave", () => drop.classList.remove("drag"));
drop.addEventListener("drop", (e) => {
    e.preventDefault();
    drop.classList.remove("drag");
    if (e.dataTransfer.files.length) setFiles(e.dataTransfer.files);
});
goBtn.addEventListener("click", run);

// "1MB", "500KB" → bytes, decimal (1KB = 1000 bytes) so the file passes however a form counts. 0 = no limit.
function limitBytes() {
    const m = $("target").value.match(/^(\d+)(KB|MB)$/);
    return m ? Number(m[1]) * (m[2] === "MB" ? 1e6 : 1e3) : 0;
}

function encode(canvas, quality) {
    return new Promise((resolve, reject) =>
        canvas.toBlob((b) => (b ? resolve(b) : reject(new Error("encode failed"))), "image/jpeg", quality));
}

function draw(img, scale) {
    const c = document.createElement("canvas");
    c.width = Math.max(1, Math.round(img.width * scale));
    c.height = Math.max(1, Math.round(img.height * scale));
    const x = c.getContext("2d");
    x.fillStyle = "#fff";   // JPG has no transparency
    x.fillRect(0, 0, c.width, c.height);
    x.imageSmoothingQuality = "high";
    x.drawImage(img, 0, 0, c.width, c.height);
    return c;
}

// The chosen quality and size; with a limit, the best quality that fits (searched between 50% and
// the chosen quality), and only when even 50% is too big, a smaller picture.
async function toJpeg(img, side, quality, limit) {
    let scale = side ? Math.min(1, side / Math.max(img.width, img.height)) : 1;
    let best = null;
    for (let round = 0; round < 6; round++) {
        const c = draw(img, scale);
        const out = (blob) => ({ blob, w: c.width, h: c.height });
        try {
            let r = out(await encode(c, quality));
            if (!limit || r.blob.size <= limit) return { ...r, fits: true };
            let lo = 0.5, hi = quality, fit = null;
            const low = out(await encode(c, lo));
            if (low.blob.size <= limit) {
                fit = low;
                for (let i = 0; i < 5; i++) {
                    const q = (lo + hi) / 2;
                    r = out(await encode(c, q));
                    if (r.blob.size <= limit) { fit = r; lo = q; } else hi = q;
                }
                return { ...fit, fits: true };
            }
            if (!best || low.blob.size < best.blob.size) best = low;
            scale *= Math.max(0.5, Math.min(0.9, Math.sqrt(limit / low.blob.size) * 0.95));
        } finally {
            c.width = 0; c.height = 0;   // iOS counts canvas memory until it's emptied
        }
    }
    return { ...best, fits: false };
}

async function run() {
    if (!files.length) return;
    SlimIO.clearError();
    const check = await SlimIO.consume();
    if (check && !check.ok) { SlimIO.showError(SlimIO.t("Daily limit reached. Come back tomorrow.")); return; }
    goBtn.disabled = true;
    goBtn.textContent = SlimIO.t("Converting…");
    prog.show();
    result.style.display = "none";
    urls.forEach((u) => URL.revokeObjectURL(u));
    urls = [];
    const side = Number($("resize").value), quality = Number($("quality").value), limit = limitBytes();
    const done = [];
    try {
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            try {
                const img = await SlimIO.openImage(file, goBtn);
                if (!img) throw new Error(SlimIO.t("This image can't be opened in this browser. Save it as JPG and try again."));
                try {
                    const r = await toJpeg(img, side, quality, limit);
                    done.push({ file, ...r, name: file.name.replace(/\.[^.]+$/, "") + ".jpg" });
                } finally {
                    if (img.close) img.close();
                }
            } catch (e) {
                done.push({ file, error: e.message });
                SlimIO.reportError("shown", e.message);
            }
            prog.set(((i + 1) / files.length) * 100);
        }
        showResult(done, limit ? $("target").value : "");
    } finally {
        goBtn.disabled = false;
        goBtn.textContent = SlimIO.t("Convert to JPG");
        prog.hide();
    }
}

function showResult(done, label) {
    list.replaceChildren();
    let after = 0;
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
            after += d.blob.size;
            const url = URL.createObjectURL(d.blob);
            urls.push(url);
            const thumb = document.createElement("img");
            thumb.className = "thumb";
            thumb.src = url;
            thumb.alt = "";
            li.appendChild(thumb);
            meta.textContent = `${SlimIO.formatSize(d.file.size)} → ${SlimIO.formatSize(d.blob.size)} · ${d.w}×${d.h}`;
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
            if (done.length === 1) { li.classList.add("one"); a.className = "dl"; }   // one photo: a full-width button
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
    $("total").textContent = ok.length ? SlimIO.t(ok.length === 1 ? "{n} JPG file · {size}" : "{n} JPG files · {size}", { n: ok.length, size: SlimIO.formatSize(after) }) : "";
    dlzip.style.display = ok.length > 1 ? "inline-block" : "none";
    dlzip.onclick = async (e) => {
        e.preventDefault();
        const zip = new JSZip();
        const used = new Set();
        for (const d of ok) {
            let n = d.name, k = 1;
            while (used.has(n)) n = d.name.replace(/(\.[^.]+)$/, `_${k++}$1`);   // IMG_0001.HEIC and IMG_0001.heic
            used.add(n);
            zip.file(n, d.blob);
        }
        const blob = await zip.generateAsync({ type: "blob" });
        SlimIO.download(new Uint8Array(await blob.arrayBuffer()), "slimio_jpg.zip", "application/zip");
    };
    result.style.display = "block";
    SlimIO.reveal(result);
}

SlimIO.refreshStatus();
