// Unlock PDF: takes off a PDF's open password (the visitor types the one they already know) and its
// print / copy / edit restrictions. qpdf, compiled to WebAssembly (public/vendor), rewrites the same
// file without encryption: pages, text, fonts and images are copied as they are, nothing is redrawn,
// and neither the file nor the password leaves the browser. It never guesses passwords.
const drop = $("drop");
const controls = $("controls");
const statusEl = $("status");
const pwField = $("pwfield");
const pw = $("pw");
const goBtn = $("go");
const result = $("result");
const dl = $("dl");
const prog = SlimIO.bindProgress("prog");

const QPDF = "/vendor/qpdf-wasm-0.3.0/";
let file = null;
let bytes = null;
let state = null;   // "password" (needs one to open) | "restricted" (opens, but locked) | "plain" | null
let locks = [];     // what the restrictions forbid: "print", "copy", "edit"

let loading = null;
function loadQpdf() {
     return loading || (loading = new Promise((ok, no) => {
         const s = document.createElement("script");
         s.src = QPDF + "qpdf.js?v=0.3.0";
         s.onload = () => ok(window.Module);
         s.onerror = () => { loading = null; s.remove(); no(new Error(SlimIO.t("The unlock tool didn't load. Check the connection and try again."))); };
         document.head.append(s);
     }));
}

// qpdf is a command-line program: one fresh instance per run (main() runs once), and its messages
// are caught from the console, which the build binds when an instance is made.
async function qpdf(args) {
     const factory = await loadQpdf();
     const out = [], err = [], keep = [console.log, console.error];
     console.log = (s) => out.push(String(s));
     console.error = (s) => err.push(String(s));
     let q;
     try { q = await factory({ locateFile: () => QPDF + "qpdf.wasm?v=0.3.0" }); }
     finally { [console.log, console.error] = keep; }
     q.FS.writeFile("/in.pdf", bytes);
     let code;
     try { code = q.callMain(args); }
     catch (e) { code = typeof e.status === "number" ? e.status : 2; err.push(String(e.message || e)); }
     let pdf = null;
     try { pdf = q.FS.readFile("/out.pdf"); } catch (e) { /* no output */ }
     return { code, out: out.join("\n"), err: err.join("\n").replace(/this\.program: \/in\.pdf: /g, ""), pdf };
}
const badPassword = (r) => /invalid password/i.test(r.err);
const pwArgs = (p) => (p ? ["--password=" + p] : []);

function setFile(f) {
     if (!SlimIO.isPdf(f)) { SlimIO.notPdf(f); return; }
     SlimIO.clearError();
     file = f;
     bytes = null;
     state = null;
     drop.querySelector(".drop-title").textContent = f.name;
     drop.querySelector(".drop-or").textContent = SlimIO.formatSize(f.size);
     result.style.display = "none";
     controls.classList.remove("hidden");
     pwField.hidden = true;
     pw.value = "";
     goBtn.disabled = true;
     say(SlimIO.t("Checking the PDF…"));
     check(f);
}

function say(msg) { statusEl.textContent = msg; }

// What kind of lock is on it? Nothing is used up and nothing is written yet.
async function check(f) {
     try {
         const data = new Uint8Array(await f.arrayBuffer());
         if (file !== f) return;
         bytes = data;
         const r = await qpdf(["--requires-password", "/in.pdf"]);
         if (file !== f) return;
         if (r.code === 3) state = "restricted";                    // encrypted, opens without a password
         else if (r.code === 0 || badPassword(r)) state = "password";
         else if (r.code === 2 && !r.err) state = "plain";          // not encrypted at all
         else throw new Error(r.err || "qpdf " + r.code);
         locks = state === "restricted" ? await lockList("") : [];
         if (file !== f) return;
         SlimIO.event("pdf-lock", { kind: state });
         if (state === "password") {
             say(SlimIO.t("This PDF needs a password to open. Type it below — the one you use to open the file."));
             pwField.hidden = false;
             goBtn.disabled = false;
             pw.focus();
         } else if (state === "restricted") {
             say(locks.length ? SlimIO.t("This PDF opens without a password, but it's locked against {what}. Unlock it to take the lock off.", { what: lockWords(locks) })
                 : SlimIO.t("This PDF opens without a password but is encrypted. Unlock it to save a plain copy."));
             goBtn.disabled = false;
         } else {
             say(SlimIO.t("This PDF has no password and no lock. You can use it as it is."));
         }
         SlimIO.refreshStatus();
     } catch (e) {
         if (file !== f) return;
         say("");
         SlimIO.showError(SlimIO.t("This file couldn't be read as a PDF: {msg}", { msg: e.message }));
     }
}

// "print low resolution: not allowed" etc. from qpdf --show-encryption
async function lockList(password) {
     const r = await qpdf(["--show-encryption", ...pwArgs(password), "/in.pdf"]);
     const no = (re) => r.out.split("\n").some((l) => re.test(l) && /not allowed/.test(l));
     return [no(/^print/) && "print", no(/^extract for any purpose/) && "copy", no(/^modify/) && "edit"].filter(Boolean);
}
function lockWords(list) {
     const w = { print: SlimIO.t("printing"), copy: SlimIO.t("copying text"), edit: SlimIO.t("editing") };
     return list.map((k) => w[k]).join(", ");
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
$("showpw").addEventListener("change", () => { pw.type = $("showpw").checked ? "text" : "password"; });
pw.addEventListener("input", () => SlimIO.clearError());
pw.addEventListener("keydown", (e) => { if (e.key === "Enter" && !goBtn.disabled) { e.preventDefault(); unlock(); } });
goBtn.addEventListener("click", unlock);

async function unlock() {
     if (!bytes || !state || state === "plain") return;
     const password = state === "password" ? pw.value : "";
     SlimIO.clearError();
     if (state === "password" && !password) {
         SlimIO.showError(SlimIO.t("Type the PDF's password first."));
         pw.focus();
         return;
     }
     goBtn.disabled = true;
     goBtn.textContent = SlimIO.t("Unlocking…");
     prog.show();
     result.style.display = "none";
     try {
         // A wrong password costs nothing: it's checked before a turn is used.
         if (state === "password") {
             const t = await qpdf(["--requires-password", ...pwArgs(password), "/in.pdf"]);
             if (t.code !== 3) {
                 if (!badPassword(t)) throw new Error(t.err || "qpdf " + t.code);
                 SlimIO.showError(SlimIO.t("That password doesn't open this PDF. Check it and try again — capital letters and spaces count."));
                 pw.select();
                 return;
             }
             locks = await lockList(password);
         }
         prog.set(30);
         const c = await SlimIO.consume();
         if (c && !c.ok) { SlimIO.showError(SlimIO.t("Daily limit reached. Come back tomorrow.")); return; }
         const r = await qpdf([...pwArgs(password), "--decrypt", "/in.pdf", "/out.pdf"]);
         if (!r.pdf || (r.code !== 0 && r.code !== 3)) throw new Error(r.err || "qpdf " + r.code);   // 3 = warnings only
         prog.set(100);
         showResult(r.pdf, password);
     } catch (e) {
         SlimIO.showError(SlimIO.t("Unlock failed: {msg}", { msg: e.message }));
     } finally {
         goBtn.disabled = false;
         goBtn.textContent = SlimIO.t("Unlock PDF");
         prog.hide();
     }
}

// Digitally signed PDFs (e-certificates that show "valid" in Acrobat) carry a /ByteRange in plain text.
function signed(b) {
     const s = new TextDecoder("latin1").decode(b);
     return /\/ByteRange\s*\[/.test(s);
}

function showResult(out, password) {
     result.style.display = "block";
     $("pwrow").textContent = password ? SlimIO.t("Removed") : SlimIO.t("None");
     $("lockrow").textContent = locks.length ? SlimIO.t("Removed ({what})", { what: lockWords(locks) }) : SlimIO.t("None");
     $("after").textContent = SlimIO.formatSize(out.length);
     $("signote").hidden = !(signed(bytes) || signed(out));
     const name = file.name.replace(/\.pdf$/i, "") + "_unlocked.pdf";
     dl.textContent = SlimIO.t("↓ Download unlocked PDF");
     dl.onclick = () => SlimIO.download(out, name, "application/pdf");
     SlimIO.reveal(result);
}

SlimIO.refreshStatus();
