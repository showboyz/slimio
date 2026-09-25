const { PDFDocument, degrees } = PDFLib;
const drop = $("drop");
const controls = $("controls");
const angle = $("angle");
const pagesInfo = $("pagesinfo");
const pageCountEl = $("pagecount");
const goBtn = $("go");
const result = $("result");
const dl = $("dl");
const prog = SlimIO.bindProgress("prog");

let file = null;
let pageCount = 0;

function setFile(f) {
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

goBtn.addEventListener("click", rotate);

async function rotate() {
     if (!file) return;
     SlimIO.clearError();
     goBtn.disabled = true;
     goBtn.textContent = SlimIO.t("Rotating…");
     prog.show();
     result.style.display = "none";
     try {
             const check = await SlimIO.consume();
             if (check && !check.ok) { SlimIO.showError(SlimIO.t("Daily limit reached. Come back tomorrow.")); return; }

             const data = await file.arrayBuffer();
             const doc = await PDFDocument.load(data);
             pageCount = doc.getPageCount();
             const deg = parseInt(angle.value, 10);

             for (let i = 0; i < pageCount; i++) {
                 const page = doc.getPage(i);
                 let current = page.getRotation();
                 page.setRotation(degrees((current.angle + deg) % 360));
                 prog.set(Math.round(((i + 1) / pageCount) * 100));
             }
             const out = await doc.save();
             showResult(pageCount, deg, out);
     } catch (e) {
             SlimIO.showError(SlimIO.t("Rotate failed: {msg}", { msg: e.message }));
     } finally {
             goBtn.disabled = false;
             goBtn.textContent = SlimIO.t("Rotate PDF");
             prog.hide();
     }
}

function showResult(count, deg, bytes) {
     result.style.display = "block";
      $("after").textContent = SlimIO.pages(count);
      $("rotated").textContent = deg === 0 ? SlimIO.t("No rotation") : SlimIO.t("{deg}° clockwise", { deg });
      dl.textContent = SlimIO.t("↓ Download PDF");
      dl.onclick = () => SlimIO.download(bytes, "slimio_rotated.pdf", "application/pdf");
}

SlimIO.refreshStatus();
