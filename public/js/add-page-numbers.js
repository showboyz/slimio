const { PDFDocument, StandardFonts, rgb, degrees } = PDFLib;
const drop = $("drop");
const controls = $("controls");
const goBtn = $("go");
const result = $("result");
const dl = $("dl");
const prog = SlimIO.bindProgress("prog");

let file = null;

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

goBtn.addEventListener("click", addNumbers);

function label(fmt, n, total) {
     if (fmt === "page-n") return `Page ${n}`;
     if (fmt === "n-of") return `${n} / ${total}`;
     if (fmt === "page-n-of") return `Page ${n} of ${total}`;
     return String(n);
}

async function addNumbers() {
     if (!file) return;
     SlimIO.clearError();
     goBtn.disabled = true;
     goBtn.textContent = SlimIO.t("Numbering…");
     prog.show();
     result.style.display = "none";
     try {
             const check = await SlimIO.consume();
             if (check && !check.ok) { SlimIO.showError(SlimIO.t("Daily limit reached. Come back tomorrow.")); return; }

             const doc = await PDFDocument.load(await file.arrayBuffer());
             const font = await doc.embedFont(StandardFonts.Helvetica);
             const [vert, horiz] = $("pos").value.split("-");
             const fmt = $("fmt").value;
             const size = parseInt($("size").value, 10);
             const skip = parseInt($("skip").value, 10);
             const start = parseInt($("start").value, 10);
             const pages = doc.getPages();
             const numbered = Math.max(0, pages.length - skip);
             const lastNumber = start + numbered - 1;

             for (let i = skip; i < pages.length; i++) {
                 const page = pages[i];
                 const text = label(fmt, start + i - skip, lastNumber);
                 const tw = font.widthOfTextAtSize(text, size);
                 const v = SlimIO.page2user(page);
                 const margin = Math.max(18, Math.min(v.width, v.height) * 0.04);
                 const vx = horiz === "left" ? margin : horiz === "right" ? v.width - margin - tw : (v.width - tw) / 2;
                 const vy = vert === "top" ? v.height - margin - size : margin;
                 const p = v.map(vx, vy);
                 page.drawText(text, { x: p.x, y: p.y, size, font, color: rgb(0.2, 0.2, 0.2), rotate: degrees(p.angle) });
                 prog.set(Math.round(((i + 1) / pages.length) * 100));
             }
             const out = await doc.save();
             showResult(pages.length, numbered, out);
     } catch (e) {
             SlimIO.showError(SlimIO.t("Numbering failed: {msg}", { msg: e.message }));
     } finally {
             goBtn.disabled = false;
             goBtn.textContent = SlimIO.t("Add page numbers");
             prog.hide();
     }
}

function showResult(count, numbered, bytes) {
     result.style.display = "block";
     $("after").textContent = SlimIO.pages(count);
     $("numbered").textContent = SlimIO.pages(numbered);
     dl.onclick = () => SlimIO.download(bytes, "slimio_numbered.pdf", "application/pdf");
}

SlimIO.refreshStatus();
