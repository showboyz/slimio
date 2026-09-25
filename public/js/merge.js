const drop = $("drop");
const controls = $("controls");
const filelist = $("filelist");
const goBtn = $("go");
const result = $("result");
const errEl = $("error");
const dl = $("dl");
const prog = SlimIO.bindProgress("prog");

let items = []; // { file, name, size, doc }

function renderList() {
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
}

function onItemAction(action, idx) {
    if (action === "up" && idx > 0) { [items[idx - 1], items[idx]] = [items[idx], items[idx - 1]]; render(); }
    else if (action === "down" && idx < items.length - 1) { [items[idx + 1], items[idx]] = [items[idx], items[idx + 1]]; render(); }
    else if (action === "rm") { items.splice(idx, 1); render(); }
    else return;
}

async function addFiles(list) {
    SlimIO.clearError();
    for (const f of list) {
        if (f.type !== "application/pdf") { SlimIO.showError(SlimIO.t("Please choose PDF files.")); return; }
        try {
            const bytes = await f.arrayBuffer();
            const doc = await PDFLib.PDFDocument.load(bytes);
            items.push({ file: f, name: f.name, size: f.size, doc });
        } catch (e) {
            SlimIO.showError(SlimIO.t('Could not read "{name}": {msg}', { name: f.name, msg: e.message }));
            return;
        }
    }
    render();
}

function render() {
    renderList();
        goBtn.disabled = items.length < 2;
    controls.classList.toggle("hidden", items.length === 0);
    SlimIO.refreshStatus();
}

function escapeHtml(s) {
    return String(s).replace(/[&<>"]/g, (c) =>
        ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

drop.addEventListener("click", () => $("pdfs").click());
$("pdfs").addEventListener("change", (e) => addFiles(e.target.files));
drop.addEventListener("dragover", (e) => { e.preventDefault(); drop.classList.add("drag"); });
drop.addEventListener("dragleave", () => drop.classList.remove("drag"));
drop.addEventListener("drop", (e) => {
    e.preventDefault();
    drop.classList.remove("drag");
    if (e.dataTransfer.files.length) addFiles(e.dataTransfer.files);
});

goBtn.addEventListener("click", merge);

async function merge() {
        if (items.length < 2) return;
    SlimIO.clearError();
    goBtn.disabled = true;
    goBtn.textContent = SlimIO.t("Merging…");
    prog.show();
    result.style.display = "none";
    try {
            const out = await PDFLib.PDFDocument.create();
        for (const it of items) {
            const copied = await out.copyPages(it.doc, it.doc.getPageIndices());
            copied.forEach((p) => out.addPage(p));
            prog.set(Math.round(((items.indexOf(it) + 1) / items.length) * 100));
        }
            const bytes = await out.save();
        const con = await SlimIO.consume();
        if (con && !con.ok) {
            SlimIO.showError(SlimIO.t("Daily limit reached. Come back tomorrow."));
            return;
        }
            showResult(items.length, out.getPageCount(), bytes);
    } catch (e) {
        SlimIO.showError(SlimIO.t("Merge failed: {msg}", { msg: e.message }));
    } finally {
        goBtn.disabled = false;
        goBtn.textContent = SlimIO.t("Merge PDFs");
        prog.hide();
    }
}

function showResult(fileCount, pageCount, bytes) {
    result.style.display = "block";
    $("merged").textContent = fileCount;
    $("pages").textContent = pageCount;
    $("after").textContent = SlimIO.formatSize(bytes.length);
    dl.onclick = () => SlimIO.download(bytes, "slimio_merged.pdf", "application/pdf");
}

SlimIO.refreshStatus();
