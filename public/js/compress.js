// Same-origin: the backend serves both the page and the /api/* routes.
// For local dev, run from the node server (http://127.0.0.1:3001), not a static host.
const API_BASE = "";
const SERVER_BASE = "";

pdfjsLib.GlobalWorkerOptions.workerSrc =
     "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

const $ = (id) => document.getElementById(id);
const drop = $("drop");
const controls = $("controls");
const mode = $("mode");
const optBrowser = $("opt-browser");
const optServer = $("opt-server");
const gslevel = $("gslevel");
const quality = $("quality");
const scale = $("scale");
const qval = $("qval");
const sval = $("sval");
const goBtn = $("go");
const prog = $("prog");
const result = $("result");
const errEl = $("error");
const limitEl = $("limit");
const dl = $("dl");
const sub = $("sub");
const logEl = $("log");

let file = null;

quality.oninput = () => (qval.textContent = quality.value + "%");
scale.oninput = () => (sval.textContent = (scale.value / 100).toFixed(1) + "x");

mode.onchange = () => {
    const server = mode.value === "server";
    optBrowser.style.display = server ? "none" : "block";
    optServer.style.display = server ? "block" : "none";
    sub.textContent = server
        ? SlimIO.t("Your file is sent to the Ghostscript server to keep text perfectly sharp.")
        : SlimIO.t("Your file runs locally in your browser — nothing is uploaded.");
    refreshStatus();
};

// ---- file selection ----
function setFile(f) {
    if (!f || f.type !== "application/pdf") {
        showError(SlimIO.t("Please choose a PDF file."));
        return;
    }
    file = f;
    drop.querySelector(".drop-title").textContent = f.name;
    drop.querySelector(".drop-or").textContent = formatSize(f.size);
    goBtn.disabled = false;
    controls.classList.remove("hidden");
    refreshStatus();
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

// ---- compression ----
goBtn.addEventListener("click", compress);

async function compress() {
    if (!file) return;
    clearError();
    goBtn.disabled = true;
    goBtn.textContent = SlimIO.t("Compressing…");
    prog.parentElement.style.display = "block";
    result.style.display = "none";

    try {
        if (mode.value === "server") {
            await compressOnServer();
        } else {
            await compressInBrowser();
        }
    } catch (e) {
        console.error(e);
        showError(SlimIO.t("Something went wrong: {msg}", { msg: e.message }));
    } finally {
        goBtn.disabled = false;
        goBtn.textContent = SlimIO.t("Compress PDF");
        prog.parentElement.style.display = "none";
    }
}

async function compressOnServer() {
    prog.style.width = "60%";
    const resp = await fetch(`${SERVER_BASE}/api/compress`, {
        method: "POST",
        headers: { "X-Level": gslevel.value },
        body: await file.arrayBuffer(),
    });
    const j = await resp.json();
    if (resp.status === 429) {
        showError(SlimIO.t("Daily limit reached. {limit} per day. Come back tomorrow.", { limit: j.limit || "?" }));
        refreshStatus();
        return;
    }
    if (!j.ok) {
        showError(SlimIO.t("Server error: {msg}", { msg: j.error || "unknown" }));
        refreshStatus();
        return;
    }
    prog.style.width = "100%";
    const bytes = base64ToBytes(j.pdf);
    showResult(j.inBytes, j.outBytes, bytes);
    updateLimit(j.remaining, j.limit);
}

async function compressInBrowser() {
    const check = await fetch(`${API_BASE}/api/check`).then((r) => r.json());
    if (!check.ok) {
        showError(SlimIO.t("Daily limit reached. {limit} per day. Come back tomorrow.", { limit: check.limit }));
        refreshStatus();
        return;
    }

    const q = parseInt(quality.value, 10) / 100;
    const s = parseInt(scale.value, 10) / 100;
    const data = await file.arrayBuffer();

    const src = await pdfjsLib.getDocument(data).promise;
    const out = await PDFLib.PDFDocument.create();

    for (let i = 1; i <= src.numPages; i++) {
        const page = await src.getPage(i);
        const viewport = page.getViewport({ scale: s * 1.5 });
        const canvas = document.createElement("canvas");
        canvas.width = Math.ceil(viewport.width);
        canvas.height = Math.ceil(viewport.height);
        const ctx = canvas.getContext("2d");

        ctx.fillStyle = "#fff";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        await page.render({ canvasContext: ctx, viewport }).promise;

        const imgBytes = await canvasToJpeg(canvas, q);
        const jpg = await out.embedJpg(imgBytes);
        const pdfPage = out.addPage([jpg.width, jpg.height]);
        pdfPage.drawImage(jpg, { x: 0, y: 0, width: jpg.width, height: jpg.height });

        prog.style.width = Math.round((i / src.numPages) * 100) + "%";
    }

    const bytes = await out.save();
    const consume = await fetch(`${API_BASE}/api/consume`, { method: "POST" }).then((r) => r.json());
    showResult(file.size, bytes.length, bytes);
    updateLimit(consume.remaining, consume.limit);
}

function canvasToJpeg(canvas, quality) {
    return new Promise((resolve, reject) => {
        canvas.toBlob(async (b) => {
            if (!b) return reject(new Error("toBlob failed"));
            try {
                resolve(new Uint8Array(await b.arrayBuffer()));
            } catch (e) { reject(e); }
        }, "image/jpeg", quality);
    });
}

function base64ToBytes(b64) {
    const bin = atob(b64);
    const out = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
}

// ---- UI helpers ----
function showResult(orig, after, bytes) {
    try { window.plausible && window.plausible("Tool Used", { props: { tool: "compress" } }); } catch (e) {}
    result.style.display = "block";
    $("orig").textContent = formatSize(orig);
    $("after").textContent = formatSize(after);
    const pct = orig > 0 ? ((orig - after) / orig) * 100 : 0;
    $("gain").textContent = pct > 0 ? `−${pct.toFixed(1)}%` : SlimIO.t("0% (already optimized)");
    log(`OK original=${formatSize(orig)} after=${formatSize(after)} saved=${pct.toFixed(1)}%`);

    const url = URL.createObjectURL(new Blob([bytes], { type: "application/pdf" }));
    dl.href = url;
    dl.download = "slimio_" + (file ? file.name : "out.pdf");
}

function updateLimit(remaining, limit) {
    limitEl.textContent = SlimIO.t("Compressions left today: {remaining} / {limit}", { remaining, limit });
    if (remaining === 0) goBtn.disabled = true;
}

function showError(msg) {
    errEl.textContent = msg;
    errEl.style.display = "block";
    result.style.display = "none";
    log(msg);
}
function clearError() { errEl.style.display = "none"; }

function log(msg) {
    logEl.style.display = "block";
    logEl.textContent += msg + "\n";
    logEl.scrollTop = logEl.scrollHeight;
}

function refreshStatus() {
    const base = mode.value === "server" ? SERVER_BASE : API_BASE;
    fetch(`${base}/api/check`)
        .then((r) => r.json())
        .then((c) => updateLimit(c.remaining, c.limit))
        .catch(() => { limitEl.textContent = SlimIO.t("Limit service currently unavailable."); });
}

function formatSize(n) {
    if (n < 1024) return `${n} B`;
    if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
    return `${(n / 1024 / 1024).toFixed(2)} MB`;
}

window.addEventListener("error", (e) => log("JS ERROR: " + e.message));
window.addEventListener("unhandledrejection", (e) => log("REJECTION: " + (e.reason?.message || e.reason)));

 refreshStatus();
