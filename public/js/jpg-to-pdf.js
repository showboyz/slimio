const { PDFDocument } = PDFLib;
const drop = $("drop");
const controls = $("controls");
const filelist = $("filelist");
const goBtn = $("go");
const result = $("result");
const dl = $("dl");
const prog = SlimIO.bindProgress("prog");

let items = [];

function render() {
    filelist.innerHTML = "";
    items.forEach((it, i) => {
        const li = document.createElement("li");
        li.innerHTML =
              `<span class="fname">${i + 1}. ${escapeHtml(it.name)} <span class="fsize">${SlimIO.formatSize(it.size)}</span></span>`;
        const actions = document.createElement("span");
        actions.style.display = "flex";
        actions.style.gap = "6px";
        ["up", "down", "rm"].forEach((a) => {
            const b = document.createElement("button");
            b.className = "fbtn";
            b.title = { up: SlimIO.t("Move up"), down: SlimIO.t("Move down"), rm: SlimIO.t("Remove") }[a];
            b.textContent = { up: "▲", down: "▼", rm: "✕" }[a];
            b.addEventListener("click", () => onItemAction(a, i));
            actions.appendChild(b);
         });
        li.appendChild(actions);
        filelist.appendChild(li);
     });
    goBtn.disabled = items.length === 0;
    controls.classList.toggle("hidden", items.length === 0);
    SlimIO.refreshStatus();
}

function onItemAction(action, i) {
    if (action === "up" && i > 0) { [items[i - 1], items[i]] = [items[i], items[i - 1]]; render(); }
    else if (action === "down" && i < items.length - 1) { [items[i + 1], items[i]] = [items[i], items[i + 1]]; render(); }
    else if (action === "rm") { items.splice(i, 1); render(); }
}

function escapeHtml(s) {
    return String(s).replace(/[&<>"]/g, (c) =>
        ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

async function addFiles(list) {
    SlimIO.clearError();
    for (const f of list) {
        if (!f.type.startsWith("image/")) { SlimIO.showError(SlimIO.t("Please choose image files (JPG, PNG, WebP…).")); return; }
        items.push({ name: f.name, size: f.size, file: f });
        render();
     }
    SlimIO.refreshStatus();
}

drop.addEventListener("click", () => $("images").click());
$("images").addEventListener("change", (e) => addFiles(e.target.files));
drop.addEventListener("dragover", (e) => { e.preventDefault(); drop.classList.add("drag"); });
drop.addEventListener("dragleave", () => drop.classList.remove("drag"));
drop.addEventListener("drop", (e) => {
    e.preventDefault();
    drop.classList.remove("drag");
    if (e.dataTransfer.files.length) addFiles(e.dataTransfer.files);
});

goBtn.addEventListener("click", convert);

// PDF size limit: "200KB", "2MB", or "custom" with the KB box. 0 = no limit.
// Decimal (1KB = 1000 bytes), so the file passes whichever way a form counts.
function limitBytes() {
    const v = $("target").value;
    if (v === "custom") { const kb = Number($("kmax").value); return kb >= 10 ? Math.round(kb * 1000) : 0; }
    const m = v.match(/^(\d+(?:\.\d+)?)(KB|MB)$/i);
    return m ? Math.round(parseFloat(m[1]) * (m[2].toUpperCase() === "MB" ? 1e6 : 1e3)) : 0;
}
function limitLabel() {
    return $("target").value === "custom" ? Math.round(Number($("kmax").value)) + "KB" : $("target").value;
}
$("target").addEventListener("change", () => { $("krange").hidden = $("target").value !== "custom"; });
// ?target=200KB from guides and links; a size that isn't in the menu goes in the KB box
(() => {
    const t = (new URLSearchParams(location.search).get("target") || "").toUpperCase();
    const m = t.match(/^(\d+(?:\.\d+)?)(KB|MB)$/);
    if (!m) return;
    if ([...$("target").options].some((o) => o.value === t)) $("target").value = t;
    else { $("target").value = "custom"; $("kmax").value = Math.round(parseFloat(m[1]) * (m[2] === "MB" ? 1000 : 1)); }
})();
$("krange").hidden = $("target").value !== "custom";

async function convert() {
    if (items.length === 0) return;
    SlimIO.clearError();
    const limit = limitBytes();
    if ($("target").value === "custom" && !limit) { SlimIO.showError(SlimIO.t("Enter a size of at least 10KB.")); return; }
    goBtn.disabled = true;
    goBtn.textContent = SlimIO.t("Converting…");
    prog.show();
    result.style.display = "none";
    try {
        const check = await SlimIO.consume();
        if (check && !check.ok) { SlimIO.showError(SlimIO.t("Daily limit reached. Come back tomorrow.")); return; }

        let r = null;
        // Photos as they are when they already fit: no quality lost
        if (!limit || items.reduce((n, it) => n + it.size, 0) <= limit) {
            const out = await PDFDocument.create();
            for (let i = 0; i < items.length; i++) {
                const it = items[i];
                const img = await loadImage(out, it.file);
                if (!img) { SlimIO.showError(SlimIO.t('Could not read "{name}".', { name: it.name })); return; }
                const page = out.addPage([img.width, img.height]);
                page.drawImage(img, { x: 0, y: 0, width: img.width, height: img.height });
                prog.set(Math.round(((i + 1) / items.length) * (limit ? 30 : 100)));
             }
            const bytes = await out.save();
            if (!limit || bytes.length <= limit) r = { bytes, fits: true, kept: true };
        }
        if (!r) r = await fitToLimit(limit);
        if (!r) return;
        SlimIO.event("jpg-to-pdf-result", { target: limit ? limitLabel() : "none", fits: r.fits, kept: !!r.kept,
                images: items.length, outKB: Math.round(r.bytes.length / 1024) });
        showResult(items.length, r, limit);
     } catch (e) {
        SlimIO.showError(SlimIO.t("Conversion failed: {msg}", { msg: e.message }));
     } finally {
        goBtn.disabled = false;
        goBtn.textContent = SlimIO.t("Convert to PDF");
        prog.hide();
     }
}

// Under a limit ("one PDF under 200KB" on upload forms): every photo is saved again as JPEG,
// lowering the quality first and then the pixel size, until the whole PDF fits. Pages keep
// their size, so only the sharpness changes. Quality goes down to 0.3 before pixels go:
// for photographed documents, pixels are what keep small print readable.
async function fitToLimit(limit) {
    const pics = [];
    try {
        for (const it of items) {
            const img = await decode(it.file);
            if (!img) { SlimIO.showError(SlimIO.t('Could not read "{name}".', { name: it.name })); return null; }
            pics.push(img);
        }
        const full = Math.max(...pics.map((p) => Math.max(p.width, p.height)));
        let side = Math.min(2000, full), smallest = null, step = 0;
        const tick = () => prog.set(Math.min(98, 30 + ++step * 4));
        for (let round = 0; round < 12; round++, side = Math.round(side * 0.8)) {
            const canvases = pics.map((p) => draw(p, side));
            const lo = await build(pics, canvases, 0.3); tick();
            if (lo.length > limit) {
                if (!smallest || lo.length < smallest.bytes.length) smallest = { bytes: lo, fits: false, side };
                if (side < 300) break;
                continue;
            }
            let best = lo, a = 0.3, b = 0.9;
            const top = await build(pics, canvases, b); tick();
            // small print (about 8pt on A4) blurred below ~1000 px on the long side in our tests
            const blurry = side < 1000 && side < full;
            if (top.length <= limit) return { bytes: top, fits: true, side, blurry };
            for (let i = 0; i < 5; i++) {
                const mid = (a + b) / 2, m = await build(pics, canvases, mid); tick();
                if (m.length <= limit) { best = m; a = mid; } else b = mid;
            }
            return { bytes: best, fits: true, side, blurry };
        }
        return smallest;
    } finally {
        pics.forEach((p) => p.close && p.close());
    }
}

// Decoded with the EXIF rotation applied, so phone photos stand the right way up
async function decode(file) {
    try { if (window.createImageBitmap) return await createImageBitmap(file, { imageOrientation: "from-image" }); } catch (e) { /* <img> below */ }
    const url = URL.createObjectURL(file);
    try { const img = new Image(); img.src = url; await img.decode(); return img; } catch (e) { return null; } finally { URL.revokeObjectURL(url); }
}

function draw(img, side) {
    const s = Math.min(1, side / Math.max(img.width, img.height));
    const c = document.createElement("canvas");
    c.width = Math.max(1, Math.round(img.width * s));
    c.height = Math.max(1, Math.round(img.height * s));
    const x = c.getContext("2d");
    x.fillStyle = "#fff"; x.fillRect(0, 0, c.width, c.height);   // JPG has no transparency
    x.imageSmoothingQuality = "high";
    x.drawImage(img, 0, 0, c.width, c.height);
    return c;
}

async function build(pics, canvases, quality) {
    const out = await PDFDocument.create();
    for (let i = 0; i < pics.length; i++) {
        const img = await out.embedJpg(await canvasToJpeg(canvases[i], quality));
        // the page keeps the photo's own size; the smaller picture is drawn over all of it
        out.addPage([pics[i].width, pics[i].height]).drawImage(img, { x: 0, y: 0, width: pics[i].width, height: pics[i].height });
    }
    return out.save();
}

// EXIF orientation of a JPEG (1 = upright). pdf-lib puts the pixels in as stored, so a
// sideways-stored phone photo has to be turned before it goes in.
function jpegOrientation(u) {
    if (u[0] !== 0xff || u[1] !== 0xd8) return 1;
    let p = 2;
    while (p + 4 < u.length && u[p] === 0xff) {
        const mk = u[p + 1], len = (u[p + 2] << 8) | u[p + 3];
        if (mk === 0xe1 && u[p + 4] === 0x45 && u[p + 5] === 0x78 && u[p + 6] === 0x69 && u[p + 7] === 0x66) {
            const t = p + 10, le = u[t] === 0x49;
            const r16 = (o) => (le ? u[t + o] | (u[t + o + 1] << 8) : (u[t + o] << 8) | u[t + o + 1]);
            const r32 = (o) => (le ? (r16(o) | (r16(o + 2) << 16)) : ((r16(o) << 16) | r16(o + 2))) >>> 0;
            const ifd = r32(4), n = r16(ifd);
            for (let i = 0; i < n; i++) if (r16(ifd + 2 + i * 12) === 0x0112) return r16(ifd + 2 + i * 12 + 8) || 1;
            return 1;
        }
        if (mk === 0xda) break;
        p += 2 + len;
    }
    return 1;
}

async function loadImage(out, file) {
    const u = new Uint8Array(await file.arrayBuffer());
    try {
        if (file.type === "image/png") return await out.embedPng(u);
        if (/^image\/jpe?g$/.test(file.type) && jpegOrientation(u) === 1) return await out.embedJpg(u);
     } catch (e) { /* not what the type says: redrawn below */ }
    // WebP, GIF, rotated JPEGs and anything else the browser opens: redrawn as a high-quality JPG
    const img = await decode(file);
    if (!img) return null;
    try { return await out.embedJpg(await canvasToJpeg(draw(img, Math.max(img.width, img.height)), 0.92)); }
    finally { if (img.close) img.close(); }
}

function canvasToJpeg(canvas, quality) {
    return new Promise((resolve, reject) => {
        canvas.toBlob(async (b) => {
            if (!b) return reject(new Error("toBlob failed"));
            try { resolve(new Uint8Array(await b.arrayBuffer())); } catch (e) { reject(e); }
        }, "image/jpeg", quality);
     });
}

function showResult(count, r, limit) {
    const bytes = r.bytes, label = limitLabel();
    result.style.display = "block";
     $("merged").textContent = SlimIO.t(count === 1 ? "{n} image" : "{n} images", { n: count });
     $("after").textContent = SlimIO.formatSize(bytes.length);
    $("fitrow").hidden = !limit;
    $("fit").textContent = r.fits ? SlimIO.t("✓ under {size}", { size: label }) : SlimIO.t("✗ over {size}", { size: label });
    const note = $("note");
    note.hidden = !limit;
    note.className = "note" + (r.fits ? "" : " warn");
    if (!limit) note.textContent = "";
    else if (r.kept) note.textContent = SlimIO.t("Already under {size} — the photos are in at full quality.", { size: label });
    else if (r.fits) {
        note.textContent = SlimIO.t("To fit {size}, the photos were saved again at up to {px} px on the long side.", { size: label, px: r.side }) +
            (r.blurry ? SlimIO.t(" Small print may be hard to read — fewer photos or a higher limit will give a sharper result.") : "");
        if (r.blurry) note.className = "note warn";
    }
    else note.textContent = SlimIO.t("This is the smallest we could make it. To get under {size}, use fewer photos or crop away what isn't needed.", { size: label });
    dl.textContent = SlimIO.t("↓ Download PDF");
    dl.onclick = () => SlimIO.download(bytes, "slimio.pdf", "application/pdf");
    SlimIO.reveal(result);
}

SlimIO.refreshStatus();
