const { PDFDocument } = PDFLib;
const drop = $("drop");
const controls = $("controls");
const pagesInput = $("pages");
const pagesInfo = $("pagesinfo");
const goBtn = $("go");
const result = $("result");
const dl = $("dl");
const prog = SlimIO.bindProgress("prog");

let file = null;
let pageCount = 0;

function parseNumbers(str, max) {
    const out = new Set();
    str.split(",").forEach((part) => {
        const token = part.trim();
        if (!token) return;
        const m = token.match(/^(\d+)\s*-\s*(\d+)$/);
        if (m) {
            let a = parseInt(m[1], 10), b = parseInt(m[2], 10);
            if (a > b) [a, b] = [b, a];
            for (let p = a; p <= b; p++) out.add(p);
        } else {
            const p = parseInt(token, 10);
            if (!Number.isNaN(p)) out.add(p);
        }
    });
    return [...out].filter((p) => p >= 1 && p <= max).sort((a, b) => a - b);
}

function setFile(f) {
     if (!f || f.type !== "application/pdf") { SlimIO.showError(SlimIO.t("Please choose a PDF file.")); return; }
     SlimIO.clearError();
     file = f;
     drop.querySelector(".drop-title").textContent = f.name;
     drop.querySelector(".drop-or").textContent = SlimIO.formatSize(f.size);
     controls.classList.remove("hidden");
     goBtn.disabled = !pagesInput.value.trim();
     SlimIO.refreshStatus();
}

pagesInput.addEventListener("input", () => {
    if (pageCount > 0) {
        const removed = parseNumbers(pagesInput.value, pageCount).length;
        pagesInfo.textContent = SlimIO.t("This PDF has {pages}. You are removing {removed}.", { pages: SlimIO.pages(pageCount), removed });
    }
    goBtn.disabled = !pagesInput.value.trim();
});

drop.addEventListener("click", () => $("pdf").click());
$("pdf").addEventListener("change", () => setFile($("pdf").files[0]));
drop.addEventListener("dragover", (e) => { e.preventDefault(); drop.classList.add("drag"); });
drop.addEventListener("dragleave", () => drop.classList.remove("drag"));
drop.addEventListener("drop", (e) => {
    e.preventDefault();
    drop.classList.remove("drag");
    if (e.dataTransfer.files.length) setFile(e.dataTransfer.files[0]);
})

goBtn.addEventListener("click", remove);

async function remove() {
     if (!file || !pagesInput.value.trim()) return;
     SlimIO.clearError();
     goBtn.disabled = true;
     goBtn.textContent = SlimIO.t("Removing…");
     prog.show();
     result.style.display = "none";
     try {
            const check = await SlimIO.consume();
            if (check && !check.ok) { SlimIO.showError(SlimIO.t("Daily limit reached. Come back tomorrow.")); return; }

            const data = await file.arrayBuffer();
            const src = await PDFDocument.load(data);
            pageCount = src.getPageCount();
            const removed = parseNumbers(pagesInput.value, pageCount);
            if (removed.length === 0) { SlimIO.showError(SlimIO.t("None of those page numbers exist in this PDF.")); return; }
            if (removed.length >= pageCount) { SlimIO.showError(SlimIO.t("You can't remove every page — the result would be empty.")); return; }

            // remove from the back so earlier indices don't shift
            [...removed].reverse().forEach((p) => src.removePage(p - 1));
            const out = await src.save();
            prog.set(100);
            showResult(removed.length, src.getPageCount(), out);
     } catch (e) {
            SlimIO.showError(SlimIO.t("Remove failed: {msg}", { msg: e.message }));
     } finally {
            goBtn.disabled = !pagesInput.value.trim();
            goBtn.textContent = SlimIO.t("Remove pages");
            prog.hide();
     }
}

function showResult(removedCount, left, bytes) {
     result.style.display = "block";
     $("merged").textContent = removedCount;
     $("pages").textContent = left;
     $("after").textContent = SlimIO.formatSize(bytes.length);
     dl.textContent = SlimIO.t("↓ Download PDF");
     dl.onclick = () => SlimIO.download(bytes, "slimio_removed.pdf", "application/pdf");
}

SlimIO.refreshStatus();
