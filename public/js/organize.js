pdfjsLib.GlobalWorkerOptions.workerSrc =
        "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
const { PDFDocument, degrees } = PDFLib;
const drop = $("drop");
const controls = $("controls");
const grid = $("pages");
const goBtn = $("go");
const result = $("result");
const dl = $("dl");
const prog = SlimIO.bindProgress("prog");

let file = null;
let bytes = null;       // original PDF bytes
let viewer = null;      // pdf.js document, for thumbnails
let items = [];         // [{ src: original page index, rot: extra rotation, el }]
let dragFrom = -1;

async function setFile(f) {
     if (!f || f.type !== "application/pdf") { SlimIO.showError(SlimIO.t("Please choose a PDF file.")); return; }
     SlimIO.clearError();
     file = f;
     drop.querySelector(".drop-title").textContent = f.name;
     drop.querySelector(".drop-or").textContent = SlimIO.formatSize(f.size);
     result.style.display = "none";
     grid.innerHTML = "";
     goBtn.disabled = true;
     controls.classList.remove("hidden");
     try {
             bytes = new Uint8Array(await f.arrayBuffer());
             viewer = await pdfjsLib.getDocument({ data: bytes.slice() }).promise;
             items = [];
             for (let i = 0; i < viewer.numPages; i++) items.push(makeItem(i));
             render();
             goBtn.disabled = false;
             for (const it of items) await drawThumb(it);
     } catch (e) {
             SlimIO.showError(SlimIO.t("Could not open this PDF: {msg}", { msg: e.message }));
     }
     SlimIO.refreshStatus();
}

function makeItem(src) {
     const it = { src, rot: 0 };
     const el = document.createElement("div");
     el.className = "pg";
     el.draggable = true;
     el.innerHTML = `<div class="thumb"><canvas></canvas></div><div class="num"></div>
          <div class="acts">
            <button data-a="left" title="${SlimIO.t("Move left")}">←</button>
            <button data-a="rot" title="${SlimIO.t("Rotate this page")}">↻</button>
            <button data-a="del" class="del" title="${SlimIO.t("Remove this page")}">✕</button>
            <button data-a="right" title="${SlimIO.t("Move right")}">→</button>
          </div>`;
     el.addEventListener("click", (e) => {
             const a = e.target.dataset && e.target.dataset.a;
             if (!a) return;
             const i = items.indexOf(it);
             if (a === "left" && i > 0) move(i, i - 1);
             else if (a === "right" && i < items.length - 1) move(i, i + 1);
             else if (a === "rot") { it.rot = (it.rot + 90) % 360; drawThumb(it); }
             else if (a === "del") { items.splice(i, 1); render(); }
     });
     el.addEventListener("dragstart", (e) => {
             dragFrom = items.indexOf(it);
             el.classList.add("dragging");
             e.dataTransfer.effectAllowed = "move";
             e.dataTransfer.setData("text/plain", "");
     });
     el.addEventListener("dragend", () => { el.classList.remove("dragging"); dragFrom = -1; });
     el.addEventListener("dragover", (e) => { if (dragFrom < 0) return; e.preventDefault(); el.classList.add("over"); });
     el.addEventListener("dragleave", () => el.classList.remove("over"));
     el.addEventListener("drop", (e) => {
             e.preventDefault();
             e.stopPropagation();
             el.classList.remove("over");
             if (dragFrom >= 0) move(dragFrom, items.indexOf(it));
     });
     it.el = el;
     return it;
}

function move(from, to) {
     if (from === to) return;
     const [it] = items.splice(from, 1);
     items.splice(to, 0, it);
     render();
}

function render() {
     grid.replaceChildren(...items.map((it) => it.el));
     items.forEach((it, i) => {
             it.el.querySelector(".num").textContent = `Page ${it.src + 1}`;
             it.el.querySelector('[data-a="left"]').disabled = i === 0;
             it.el.querySelector('[data-a="right"]').disabled = i === items.length - 1;
             it.el.querySelector('[data-a="del"]').disabled = items.length === 1;
     });
     $("pagecount").textContent = SlimIO.pages(items.length);
}

async function drawThumb(it) {
     const page = await viewer.getPage(it.src + 1);
     const base = page.getViewport({ scale: 1, rotation: (page.rotate + it.rot) % 360 });
     const scale = Math.min(220 / base.width, 260 / base.height);
     const vp = page.getViewport({ scale, rotation: (page.rotate + it.rot) % 360 });
     const canvas = document.createElement("canvas");
     canvas.width = Math.ceil(vp.width);
     canvas.height = Math.ceil(vp.height);
     await page.render({ canvasContext: canvas.getContext("2d"), viewport: vp }).promise;
     it.el.querySelector("canvas").replaceWith(canvas);
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

goBtn.addEventListener("click", save);

async function save() {
     if (!bytes || !items.length) return;
     SlimIO.clearError();
     goBtn.disabled = true;
     goBtn.textContent = SlimIO.t("Saving…");
     prog.show();
     result.style.display = "none";
     try {
             const check = await SlimIO.consume();
             if (check && !check.ok) { SlimIO.showError(SlimIO.t("Daily limit reached. Come back tomorrow.")); return; }

             const src = await PDFDocument.load(bytes);
             const out = await PDFDocument.create();
             const copied = await out.copyPages(src, items.map((it) => it.src));
             copied.forEach((page, i) => {
                 const rot = items[i].rot;
                 if (rot) page.setRotation(degrees((page.getRotation().angle + rot) % 360));
                 out.addPage(page);
                 prog.set(Math.round(((i + 1) / copied.length) * 100));
             });
             const saved = await out.save();
             showResult(copied.length, saved);
     } catch (e) {
             SlimIO.showError(SlimIO.t("Save failed: {msg}", { msg: e.message }));
     } finally {
             goBtn.disabled = false;
             goBtn.textContent = SlimIO.t("Save PDF");
             prog.hide();
     }
}

function showResult(count, out) {
     result.style.display = "block";
     $("after").textContent = SlimIO.pages(count);
     $("size").textContent = SlimIO.formatSize(out.length);
     dl.onclick = () => SlimIO.download(out, "slimio_organized.pdf", "application/pdf");
}

SlimIO.refreshStatus();
