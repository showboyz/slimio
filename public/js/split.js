const { PDFDocument } = PDFLib;
const drop = $("drop");
const controls = $("controls");
const mode = $("mode");
const optRange = $("opt-range");
const optPages = $("opt-pagesinfo");
const rangeSel = $("range");
const pagesInfo = $("pagesinfo");
const goBtn = $("go");
const result = $("result");
const dl = $("dl");
const prog = SlimIO.bindProgress("prog");

let file = null;
let doc = null;
let pageCount = 0;

mode.onchange = () => {
    const range = mode.value === "range";
    optRange.style.display = range ? "block" : "none";
    fillRangeOptions();
};

function fillRangeOptions() {
    rangeSel.innerHTML = "";
    for (let i = 1; i <= Math.max(pageCount, 1); i++) {
        const o = document.createElement("option");
        o.value = String(i - 1);
        o.textContent = i;
        rangeSel.appendChild(o);
    }
    rangeSel.value = String(Math.max(pageCount - 1, 0));
}

async function setFile(f) {
    if (!f || f.type !== "application/pdf") { SlimIO.showError(SlimIO.t("Please choose a PDF file.")); return; }
    SlimIO.clearError();
    file = f;
    drop.querySelector(".drop-title").textContent = f.name;
    drop.querySelector(".drop-or").textContent = SlimIO.formatSize(f.size);
    try {
        doc = await PDFDocument.load(await f.arrayBuffer());
        pageCount = doc.getPageCount();
    } catch (e) { SlimIO.showError(SlimIO.t("Could not read file: {msg}", { msg: e.message })); return; }
    controls.classList.remove("hidden");
    optPages.style.display = "block";
    pagesInfo.textContent = SlimIO.t("{pages} in this PDF.", { pages: SlimIO.pages(pageCount) });
    optRange.style.display = mode.value === "range" ? "block" : "none";
    fillRangeOptions();
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

goBtn.addEventListener("click", split);

function parseRanges(str, max) {
    const out = [];
    str.split(",").forEach((part) => {
        const token = part.trim();
        if (!token) return;
        const m = token.match(/^(\d+)\s*-\s*(\d+)$/);
        if (m) {
            let a = parseInt(m[1], 10), b = parseInt(m[2], 10);
            if (a > b) [a, b] = [b, a];
            for (let p = a; p <= b; p++) out.push(p - 1);
        } else {
            const p = parseInt(token, 10);
            if (!Number.isNaN(p)) out.push(p - 1);
        }
    });
    return out.filter((p) => p >= 0 && p < max);
}

async function split() {
    if (!doc) return;
    SlimIO.clearError();
    goBtn.disabled = true;
    goBtn.textContent = SlimIO.t("Splitting…");
    prog.show();
    result.style.display = "none";
    try {
        if (mode.value === "each") {
            await splitEach();
        } else {
            await extractRange();
        }
        SlimIO.consume();
    } catch (e) {
        SlimIO.showError(SlimIO.t("Split failed: {msg}", { msg: e.message }));
    } finally {
        goBtn.disabled = false;
        goBtn.textContent = SlimIO.t("Split PDF");
        prog.hide();
    }
}

let pendingDownload = null;
let pendingName = "slimio_split.zip";

async function splitEach() {
    const zip = new JSZip();
    const base = (file.name || "document").replace(/\.pdf$/i, "");
    for (let i = 0; i < pageCount; i++) {
        const out = await PDFDocument.create();
        const copied = await out.copyPages(doc, [i]);
        out.addPage(copied[0]);
        const bytes = await out.save();
        zip.file(`${base}_page_${i + 1}.pdf`, bytes);
        prog.set(Math.round(((i + 1) / pageCount) * 100));
    }
    const blob = await zip.generateAsync({ type: "uint8array" });
    const count = pageCount;
    pendingName = `${base}.zip`;
    showResult(SlimIO.pages(count), blob, "application/zip");
}

async function extractRange() {
    const raw = String(rangeSel.value).trim();
    const pages = parseRanges(raw, pageCount);
    if (pages.length === 0) { SlimIO.showError(SlimIO.t("No valid pages in that range.")); return; }
    const out = await PDFDocument.create();
    const copied = await out.copyPages(doc, pages);
    copied.forEach((p) => out.addPage(p));
    const bytes = await out.save();
    const name = (file.name || "document").replace(/\.pdf$/i, "") + "_extracted.pdf";
    showResult(SlimIO.pages(pages.length), bytes, "application/pdf", name);
}

function showResult(pagesTxt, data, type, name) {
    result.style.display = "block";
    $("after").textContent = pagesTxt;
    pendingDownload = data;
    pendingType = type;
    pendingName = name || pendingName;
    dl.textContent = "↓ Download " + (type === "application/zip" ? "ZIP" : "PDF");
    dl.onclick = () => SlimIO.download(data, pendingName, type);
}
let pendingType = "application/pdf";

SlimIO.refreshStatus();
