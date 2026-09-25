pdfjsLib.GlobalWorkerOptions.workerSrc =
        "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
const drop = $("drop");
const controls = $("controls");
const goBtn = $("go");
const result = $("result");
const dl = $("dl");
const statusEl = $("status");
const prog = SlimIO.bindProgress("prog");

let file = null;

function setFile(f) {
     if (!f || f.type !== "application/pdf") { SlimIO.showError(SlimIO.t("Please choose a PDF file.")); return; }
     SlimIO.clearError();
     file = f;
     drop.querySelector(".drop-title").textContent = f.name;
     drop.querySelector(".drop-or").textContent = SlimIO.formatSize(f.size);
     controls.classList.remove("hidden");
     result.style.display = "none";
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

goBtn.addEventListener("click", compress);

async function compress() {
     if (!file) return;
     const label = $("target").value;
     const target = SlimTarget.parseSize(label);
     SlimIO.clearError();
     goBtn.disabled = true;
     goBtn.textContent = SlimIO.t("Compressing…");
     prog.show();
     prog.set(5);
     result.style.display = "none";
     try {
             const r = await SlimTarget.run(file, target, (p) => prog.set(5 + p * 95), (msg) => (statusEl.textContent = msg));
             if (r.limited) { SlimIO.showError(SlimIO.t("Daily limit reached. Come back tomorrow.")); return; }
             showResult(r, label);
     } catch (e) {
             SlimIO.showError(SlimIO.t("Compression failed: {msg}", { msg: e.message }));
     } finally {
             goBtn.disabled = false;
             goBtn.textContent = SlimIO.t("Compress PDF");
             statusEl.textContent = "";
             prog.hide();
     }
}

function showResult(r, label) {
     result.style.display = "block";
     $("orig").textContent = SlimIO.formatSize(file.size);
     $("after").textContent = SlimIO.formatSize(r.bytes.length);
     $("fit").textContent = r.fits ? SlimIO.t("✓ under {size}", { size: label }) : SlimIO.t("✗ over {size}", { size: label });
     const note = $("note");
     note.className = "note" + (r.fits ? "" : " warn");
     if (r.method === "original") note.textContent = SlimIO.t("Your PDF is already under {size} — no compression needed.", { size: label });
     else if (!r.fits) note.textContent = SlimIO.t("This is the smallest we could make it. To get under {size}, remove pages you don't need or split the file into parts.", { size: label });
     else if (r.method === "server") note.textContent = SlimIO.t("Text kept sharp and selectable.");
     else {
             const dpi = Math.round(r.scale * 72);
             note.textContent = SlimIO.t("To reach {size}, pages were converted to images at about {dpi} dpi. The text is no longer selectable.", { size: label, dpi }) +
                     (dpi < 50 ? SlimIO.t(" Small print may be hard to read — removing pages you don't need will give a sharper result.") : "");
             if (dpi < 50) note.className = "note warn";
     }
     const base = file.name.replace(/\.pdf$/i, "");
     dl.onclick = () => SlimIO.download(r.bytes, `${base}_${label.toLowerCase()}.pdf`, "application/pdf");
}

SlimIO.refreshStatus();
