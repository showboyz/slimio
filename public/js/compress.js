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
dl.addEventListener("click", () => SlimIO.trackDownload());

quality.oninput = () => (qval.textContent = quality.value + "%");
scale.oninput = () => (sval.textContent = (scale.value / 100).toFixed(1) + "x");

// Server (Ghostscript) is the default: text stays real text. Over SERVER_MAX we can't
// upload (our limit is 50MB; Cloudflare rejects bodies over 100MB with an HTML page),
// so those files go to the in-browser mode automatically.
const SERVER_MAX = 50 * 1024 * 1024;
function syncMode() {
    const server = mode.value === "server";
    optBrowser.style.display = server ? "none" : "block";
    optServer.style.display = server ? "block" : "none";
    sub.textContent = server
        ? SlimIO.t("Text stays sharp and selectable. Files are deleted right after compressing.")
        : SlimIO.t("Your file runs locally in your browser — nothing is uploaded.");
    $("modehint").textContent = server
        ? SlimIO.t("Best for most PDFs. Files up to 50MB; larger files are compressed in your browser.")
        : SlimIO.t("Pages are redrawn as images, so text can't be selected afterwards.");
}
mode.onchange = () => { syncMode(); refreshStatus(); };
syncMode();   // the browser may restore the other option on back/refresh
function useBrowserMode(reason) {
    mode.value = "browser";
    syncMode();
    $("modehint").textContent = reason;
}

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
    if (f.size > SERVER_MAX && mode.value === "server")
        useBrowserMode(SlimIO.t("This file is over 50MB, so it will be compressed in your browser (pages become images)."));
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
        if (mode.value === "server" && file.size > SERVER_MAX) {
            useBrowserMode(SlimIO.t("This file is over 50MB, so it will be compressed in your browser (pages become images)."));
            await compressInBrowser();
        } else if (mode.value === "server") {
            const done = await compressOnServer();
            if (done === "fallback") {
                useBrowserMode(SlimIO.t("The server couldn't take this file right now, so it was compressed in your browser instead."));
                await compressInBrowser();
            }
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
    let resp;
    try {
        resp = await fetch(`${SERVER_BASE}/api/compress`, {
            method: "POST",
            headers: SlimIO.apiHeaders({ "X-Level": gslevel.value }),
            body: await file.arrayBuffer(),
        });
    } catch (e) {
        return "fallback";   // connection dropped (e.g. upload refused mid-way)
    }
    // Anything that isn't our JSON (proxy error page, 413/502/503/504) -> compress in the browser.
    let j;
    try { j = await resp.json(); } catch (e) { return "fallback"; }
    if (resp.status === 413 || resp.status === 503 || resp.status >= 500 && !j.ok) return "fallback";
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
    const check = await fetch(`${API_BASE}/api/check`, { headers: SlimIO.apiHeaders() }).then((r) => r.json());
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
    const consume = await fetch(`${API_BASE}/api/consume`, { method: "POST", headers: SlimIO.apiHeaders() }).then((r) => r.json());
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
    SlimIO.track(SlimIO.lang === "ko" ? "ko/compress" : "compress");
    // Never hand back a bigger file: if compression didn't help, the original is the best result.
    const keep = after >= orig && file;
    if (keep) after = orig;
    result.style.display = "block";
    $("orig").textContent = formatSize(orig);
    $("after").textContent = formatSize(after);
    const pct = orig > 0 ? ((orig - after) / orig) * 100 : 0;
    $("gain").textContent = pct > 0 ? `−${pct.toFixed(1)}%` : SlimIO.t("0% (already optimized)");
    log(`OK original=${formatSize(orig)} after=${formatSize(after)} saved=${pct.toFixed(1)}%`);

    const url = URL.createObjectURL(keep ? file : new Blob([bytes], { type: "application/pdf" }));
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
    if (SlimIO.debug) logEl.style.display = "block";
    logEl.textContent += msg + "\n";
    logEl.scrollTop = logEl.scrollHeight;
}

function refreshStatus() {
    const base = mode.value === "server" ? SERVER_BASE : API_BASE;
    fetch(`${base}/api/check`, { headers: SlimIO.apiHeaders() })
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
