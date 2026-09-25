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

async function convert() {
    if (items.length === 0) return;
    SlimIO.clearError();
    goBtn.disabled = true;
    goBtn.textContent = SlimIO.t("Converting…");
    prog.show();
    result.style.display = "none";
    try {
        const check = await SlimIO.consume();
        if (check && !check.ok) { SlimIO.showError(SlimIO.t("Daily limit reached. Come back tomorrow.")); return; }

        const out = await PDFDocument.create();
        for (let i = 0; i < items.length; i++) {
            const it = items[i];
            const bytes = await it.file.arrayBuffer();
            let font = await loadImage(out, bytes, it.file.type);
            if (!font) { SlimIO.showError(SlimIO.t('Could not read "{name}".', { name: it.name })); return; }
            const page = out.addPage([font.width, font.height]);
            page.drawImage(font, { x: 0, y: 0, width: font.width, height: font.height });
            prog.set(Math.round(((i + 1) / items.length) * 100));
         }
        const pdfBytes = await out.save();
        showResult(items.length, pdfBytes);
     } catch (e) {
        SlimIO.showError(SlimIO.t("Conversion failed: {msg}", { msg: e.message }));
     } finally {
        goBtn.disabled = false;
        goBtn.textContent = SlimIO.t("Convert to PDF");
        prog.hide();
     }
}

async function loadImage(out, bytes, mime) {
    const u = new Uint8Array(bytes);
    try {
        if (mime === "image/png") return await out.embedPng(u);
        if (mime === "image/webp") {
            const blob = new Blob([u], { type: "image/webp" });
            const url = URL.createObjectURL(blob);
            const img = await loadCanvas(url);
            URL.revokeObjectURL(url);
            const jpeg = await canvasToJpeg(img, 0.92);
            return await out.embedJpg(jpeg);
        }
        return await out.embedJpg(u);
     } catch (e) {
        try {
            const url = URL.createObjectURL(new Blob([u]));
            const img = await loadCanvas(url);
            URL.revokeObjectURL(url);
            const jpeg = await canvasToJpeg(img, 0.92);
            return await out.embedJpg(jpeg);
        } catch (e2) { return null; }
     }
}

function loadCanvas(url) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = () => reject(new Error("image load failed"));
        img.src = url;
     });
}

function canvasToJpeg(canvas, quality) {
    return new Promise((resolve, reject) => {
        canvas.toBlob(async (b) => {
            if (!b) return reject(new Error("toBlob failed"));
            try { resolve(new Uint8Array(await b.arrayBuffer())); } catch (e) { reject(e); }
        }, "image/jpeg", quality);
     });
}

function showResult(count, bytes) {
    result.style.display = "block";
     $("merged").textContent = SlimIO.t(count === 1 ? "{n} image" : "{n} images", { n: count });
     $("after").textContent = SlimIO.formatSize(bytes.length);
    dl.textContent = SlimIO.t("↓ Download PDF");
    dl.onclick = () => SlimIO.download(bytes, "slimio.pdf", "application/pdf");
}

SlimIO.refreshStatus();
