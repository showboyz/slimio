pdfjsLib.GlobalWorkerOptions.workerSrc =
        "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

const drop = $("drop");
const controls = $("controls");
const quality = $("quality");
const scale = $("scale");
const qval = $("qval");
const sval = $("sval");
const outtype = $("outtype");
const goBtn = $("go");
const result = $("result");
const dl = $("dl");
const prog = SlimIO.bindProgress("prog");

let file = null;

quality.oninput = () => (qval.textContent = quality.value + "%");
scale.oninput = () => (sval.textContent = (scale.value / 100).toFixed(1) + "x");

async function setFile(f) {
    if (!f || f.type !== "application/pdf") { SlimIO.showError(SlimIO.t("Please choose a PDF file.")); return; }
    SlimIO.clearError();
    file = f;
    drop.querySelector(".drop-title").textContent = f.name;
    drop.querySelector(".drop-or").textContent = SlimIO.formatSize(f.size);
    controls.classList.remove("hidden");
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

goBtn.addEventListener("click", convert);

async function convert() {
    if (!file) return;
    SlimIO.clearError();
    goBtn.disabled = true;
    goBtn.textContent = SlimIO.t("Converting…");
    prog.show();
    result.style.display = "none";
    try {
        const check = await SlimIO.consume();
        if (check && !check.ok) { SlimIO.showError(SlimIO.t("Daily limit reached. Come back tomorrow.")); return; }

        const mime = outtype.value;
        const q = parseInt(quality.value, 10) / 100;
        const s = parseInt(scale.value, 10) / 100;
        const ext = mime === "image/png" ? "png" : "jpg";
        const data = await file.arrayBuffer();

        const src = await pdfjsLib.getDocument(data).promise;
        const zip = new JSZip();
        const base = (file.name || "document").replace(/\.pdf$/i, "");

        for (let i = 1; i <= src.numPages; i++) {
            const page = await src.getPage(i);
            const viewport = page.getViewport({ scale: s });
            const canvas = document.createElement("canvas");
            canvas.width = Math.ceil(viewport.width);
            canvas.height = Math.ceil(viewport.height);
            const ctx = canvas.getContext("2d");
            ctx.fillStyle = "#fff";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            await page.render({ canvasContext: ctx, viewport }).promise;

            const blob = await new Promise((resolve, reject) =>
                canvas.toBlob((b) => b ? resolve(b) : reject(new Error("toBlob failed")), mime, q));
            const bytes = await blob.arrayBuffer();
            zip.file(`${base}_${String(i).padStart(3, "0")}.${ext}`, new Uint8Array(bytes));
            prog.set(Math.round((i / src.numPages) * 100));
        }

        const out = await zip.generateAsync({ type: "uint8array" });
        showResult(src.numPages, mime, out);
     } catch (e) {
        SlimIO.showError(SlimIO.t("Conversion failed: {msg}", { msg: e.message }));
     } finally {
        goBtn.disabled = false;
        goBtn.textContent = SlimIO.t("Convert to JPG");
        prog.hide();
     }
}

function showResult(count, mime, bytes) {
    result.style.display = "block";
     $("after").textContent = SlimIO.pages(count);
     $("outtype-label").textContent = mime === "image/png" ? "PNG (PNG)" : "JPG (JPG)";
    dl.textContent = SlimIO.t("↓ Download ZIP");
    dl.onclick = () => SlimIO.download(bytes, "slimio_images.zip", "application/zip");
}

SlimIO.refreshStatus();
