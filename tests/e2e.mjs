// End-to-end check of the whole site, meant to be run before every deploy:
//   * every tool page (English and Korean) is run in Chrome on generated sample files, and the
//     result is checked: a valid PDF with the right page count and its text still extractable,
//     ZIPs with the right number of files, images with the right pixels and KB range;
//   * every page in the sitemap is opened at phone width and checked for script errors, failed
//     requests, horizontal scrolling and broken internal links.
// It starts its own server on port 3099 with the daily limit lifted, so it never touches the
// live site. Needs Google Chrome; Ghostscript (gs) adds the page-count and text checks.
//
//   npm test                  everything
//   npm test -- merge sign    only tests whose name contains "merge" or "sign"
//   npm test -- --pages       only the sitemap page checks
//   npm test -- --mobile      run the tools at phone size (390×844, touch) instead of desktop
//   npm test -- --live        after a deploy: the server-compression tests and the page checks
//                             against https://pdfslimio.com (uses 5 of the day's operations;
//                             analytics are blocked, so nothing is counted as a visit)
import { chromium } from "playwright-core";
import { spawn, spawnSync } from "child_process";
import fs from "fs";
import os from "os";
import path from "path";
import { fileURLToPath } from "url";

const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const PORT = 3099;
const args0 = process.argv.slice(2);
const LIVE = args0.includes("--live");
const BASE = LIVE ? "https://pdfslimio.com" : `http://localhost:${PORT}`;
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), "slimio-e2e-"));
const args = args0;
const onlyPages = args.includes("--pages");
const MOBILE = args.includes("--mobile");
const filters = args.filter((a) => !a.startsWith("--"));
const HAS_GS = spawnSync("gs", ["--version"]).status === 0;

// ------------------------------------------------------------------ helpers

const KB = (s) => Math.round(s / 100) / 10 + "KB";

function pdfCheck(bytes, { pages, text, rotate } = {}) {
  if (String.fromCharCode(...bytes.subarray(0, 5)) !== "%PDF-") return "not a PDF";
  if (!HAS_GS) return null;
  const f = path.join(TMP, "check.pdf");
  fs.writeFileSync(f, bytes);
  const n = spawnSync("gs", ["-q", "-dNODISPLAY", "-dNOSAFER", "-c", `(${f}) (r) file runpdfbegin pdfpagecount = quit`]);
  const count = parseInt(String(n.stdout).trim(), 10);
  if (!(count > 0)) return "Ghostscript can't read it: " + String(n.stderr).slice(0, 120);
  if (pages && count !== pages) return `${count} pages, expected ${pages}`;
  if (rotate !== undefined) {
    const r = spawnSync("gs", ["-q", "-dNODISPLAY", "-dNOSAFER", "-c", `(${f}) (r) file runpdfbegin 1 pdfgetpage /Rotate knownoget { = } { 0 = } ifelse quit`]);
    if (parseInt(String(r.stdout), 10) !== rotate) return `page 1 is rotated ${String(r.stdout).trim()}°, expected ${rotate}°`;
  }
  if (text) {
    const t = spawnSync("gs", ["-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=txtwrite", "-sOutputFile=-", f]);
    const got = String(t.stdout).replace(/\s+/g, "");
    for (const w of text) if (!got.includes(w.replace(/\s+/g, ""))) return `text "${w}" not found after processing`;
  }
  return null;
}

// page 1 drawn small, to tell whether something was added to it
function render(bytes) {
  const f = path.join(TMP, "render.pdf");
  fs.writeFileSync(f, bytes);
  return String(spawnSync("gs", ["-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pnggray", "-r40", "-dFirstPage=1", "-dLastPage=1", "-sOutputFile=-", f]).stdout.toString("base64"));
}

// page 1 as raw grey pixels (0 = black)
function grayPage(bytes, res) {
  const f = path.join(TMP, "gray.pdf");
  fs.writeFileSync(f, bytes);
  const out = spawnSync("gs", ["-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pgmraw", `-r${res}`, "-dFirstPage=1", "-dLastPage=1", "-sOutputFile=-", f]).stdout;
  const m = out.toString("latin1", 0, 200).match(/^P5\s+(?:#[^\n]*\n\s*)*(\d+)\s+(\d+)\s+255\s/);   // Ghostscript adds a comment line
  return { w: +m[1], h: +m[2], px: out.subarray(m[0].length) };
}

function zipCount(bytes) {
  if (bytes[0] !== 0x50 || bytes[1] !== 0x4b) return -1;
  let n = 0;
  for (let i = 0; i < bytes.length - 3; i++) if (bytes[i] === 0x50 && bytes[i + 1] === 0x4b && bytes[i + 2] === 1 && bytes[i + 3] === 2) n++;
  return n;
}

function imageSize(b) {
  if (b[0] === 0x89 && b[1] === 0x50) return { type: "png", w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
  if (b[0] === 0xff && b[1] === 0xd8) {
    for (let i = 2; i < b.length - 9;) {
      if (b[i] !== 0xff) { i++; continue; }
      const m = b[i + 1], len = b.readUInt16BE(i + 2);
      if (m >= 0xc0 && m <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(m)) return { type: "jpeg", w: b.readUInt16BE(i + 7), h: b.readUInt16BE(i + 5) };
      i += 2 + len;
    }
  }
  if (b.toString("ascii", 0, 4) === "RIFF" && b.toString("ascii", 8, 12) === "WEBP") {
    const c = b.toString("ascii", 12, 16);
    if (c === "VP8X") return { type: "webp", w: 1 + b.readUIntLE(24, 3), h: 1 + b.readUIntLE(27, 3) };
    if (c === "VP8L") { const v = b.readUInt32LE(21); return { type: "webp", w: 1 + (v & 0x3fff), h: 1 + ((v >> 14) & 0x3fff) }; }
    if (c === "VP8 ") return { type: "webp", w: b.readUInt16LE(26) & 0x3fff, h: b.readUInt16LE(28) & 0x3fff };
  }
  return null;
}

// "50KB" / "20-50KB" / "10-20" (signature menu, KB) / "1MB" -> byte limits. Like the tools, the
// minimum counts 1KB as 1,024 bytes and the maximum as 1,000, so a file passes either reading.
function kbRange(s) {
  const m = String(s).match(/^(?:(\d+)-)?(\d+)(KB|MB)?$/i);
  if (!m) return null;
  const unit = (m[3] || "KB").toUpperCase() === "MB" ? 1e6 : 1e3;
  return { min: m[1] ? +m[1] * 1024 : 0, max: +m[2] * unit };
}

function objectLiteral(file, name) {
  const src = fs.readFileSync(path.join(ROOT, "public", file), "utf8");
  const m = src.match(new RegExp(`const ${name} = (\\{[\\s\\S]*?\\n?\\});`));
  return new Function("return " + m[1])();
}

// ------------------------------------------------------------------ sample files

async function makeFixtures(browser) {
  const p = await browser.newPage();
  // a photo-like JPEG: smooth shapes plus sensor-style noise, so it compresses like a real photo
  const jpeg = async (w, h, q) => Buffer.from(await p.evaluate(async ([w, h, q]) => {
    const c = new OffscreenCanvas(w, h), x = c.getContext("2d");
    const g = x.createLinearGradient(0, 0, w, h); g.addColorStop(0, "#d9cbb5"); g.addColorStop(1, "#6d5a48");
    x.fillStyle = g; x.fillRect(0, 0, w, h);
    x.fillStyle = "#e8c4a8"; x.beginPath(); x.ellipse(w / 2, h * 0.4, w * 0.22, h * 0.24, 0, 0, 7); x.fill();
    x.fillStyle = "#2b2b2b"; x.font = `${Math.round(w / 18)}px serif`;
    for (let i = 0; i < 6; i++) x.fillText("SlimIO sample text line " + i, w * 0.08, h * (0.72 + i * 0.045));
    const d = x.getImageData(0, 0, w, h), a = d.data;
    for (let i = 0; i < a.length; i += 4) { const n = (Math.random() - 0.5) * 34; a[i] += n; a[i + 1] += n; a[i + 2] += n; }
    x.putImageData(d, 0, 0);
    const b = await c.convertToBlob({ type: "image/jpeg", quality: q });
    return Array.from(new Uint8Array(await b.arrayBuffer()));
  }, [w, h, q]));
  const photo = await jpeg(3024, 4032, 0.9);
  fs.writeFileSync(path.join(TMP, "photo.jpg"), photo);
  const photo2 = await jpeg(1600, 1200, 0.85);
  fs.writeFileSync(path.join(TMP, "photo2.jpg"), photo2);
  // the same landscape pixels with an EXIF tag saying "turn 90° clockwise", as phones store portrait shots
  const tiff = Buffer.from([0x4d, 0x4d, 0, 0x2a, 0, 0, 0, 8, 0, 1, 0x01, 0x12, 0, 3, 0, 0, 0, 1, 0, 6, 0, 0, 0, 0, 0, 0]);
  const exif = Buffer.concat([Buffer.from("Exif\0\0", "binary"), tiff]);
  fs.writeFileSync(path.join(TMP, "sideways.jpg"), Buffer.concat([photo2.subarray(0, 2),
    Buffer.from([0xff, 0xe1, (exif.length + 2) >> 8, (exif.length + 2) & 255]), exif, photo2.subarray(2)]));
  // a faded till receipt, small on a dark table: "Make faded text clearer" used to turn its print white
  fs.writeFileSync(path.join(TMP, "faded.jpg"), Buffer.from(await p.evaluate(async () => {
    const c = new OffscreenCanvas(3024, 4032), x = c.getContext("2d");
    x.fillStyle = "#6d5440"; x.fillRect(0, 0, 3024, 4032);
    x.fillStyle = "#eeebe4"; x.fillRect(1062, 666, 900, 2700);
    x.fillStyle = "#b5b0a6"; x.font = "56px monospace";
    for (let i = 0; i < 24; i++) x.fillText(`ITEM ${i + 1}   1,234`, 1120, 900 + i * 100);
    const d = x.getImageData(0, 0, 3024, 4032), a = d.data;
    for (let i = 0; i < a.length; i += 4) { const n = (Math.random() - 0.5) * 18; a[i] += n; a[i + 1] += n; a[i + 2] += n; }
    x.putImageData(d, 0, 0);
    const b = await c.convertToBlob({ type: "image/jpeg", quality: 0.88 });
    return Array.from(new Uint8Array(await b.arrayBuffer()));
  })));
  // a receipt lying 6° crooked on a dark table, the way phone photos of receipts usually look
  fs.writeFileSync(path.join(TMP, "tilted.jpg"), Buffer.from(await p.evaluate(async () => {
    const c = new OffscreenCanvas(3024, 4032), x = c.getContext("2d");
    x.fillStyle = "#4a3b2e"; x.fillRect(0, 0, 3024, 4032);
    x.translate(1512, 2016); x.rotate(6 * Math.PI / 180);
    x.fillStyle = "#f2efe8"; x.fillRect(-500, -1500, 1000, 3000);
    x.fillStyle = "#858585"; x.font = "60px monospace";   // grey print, so only the table counts as dark below
    for (let i = 0; i < 26; i++) x.fillText(`ITEM ${i + 1}   1,234`, -430, -1350 + i * 110);
    x.setTransform(1, 0, 0, 1, 0, 0);
    const d = x.getImageData(0, 0, 3024, 4032), a = d.data;
    for (let i = 0; i < a.length; i += 4) { const n = (Math.random() - 0.5) * 18; a[i] += n; a[i + 1] += n; a[i + 2] += n; }
    x.putImageData(d, 0, 0);
    const b = await c.convertToBlob({ type: "image/jpeg", quality: 0.88 });
    return Array.from(new Uint8Array(await b.arrayBuffer()));
  })));
  // an iPhone-style HEIC photo (Chrome can't open these itself); only where macOS sips can make one
  spawnSync("sips", ["-s", "format", "heic", path.join(TMP, "photo2.jpg"), "--out", path.join(TMP, "photo.heic")], { stdio: "ignore" });
  fs.writeFileSync(path.join(TMP, "notes.txt"), "not a picture");
  fs.writeFileSync(path.join(TMP, "photo.pdf"), jpegPdf([photo, await jpeg(2480, 3508, 0.9)]));
  // three different phone-size photos: well over 10MB, but 10MB has room for much more than 150 dpi
  fs.writeFileSync(path.join(TMP, "photos3.pdf"), jpegPdf([photo, await jpeg(3024, 4032, 0.9), await jpeg(3024, 4032, 0.9)]));
  const sig = Buffer.from(await p.evaluate(async () => {
    const c = new OffscreenCanvas(1400, 520), x = c.getContext("2d");
    x.fillStyle = "#f4f2ec"; x.fillRect(0, 0, 1400, 520);
    x.fillStyle = "#151515"; x.font = "italic 190px 'Snell Roundhand', 'Apple Chancery', cursive";
    x.fillText("J. Rivera", 120, 330);
    const b = await c.convertToBlob({ type: "image/png" });
    return Array.from(new Uint8Array(await b.arrayBuffer()));
  }));
  fs.writeFileSync(path.join(TMP, "sig.png"), sig);
  // a 3-page text PDF with English and Korean, printed by Chrome like "Save as PDF"
  const para = "New sign-ups grew steadily this quarter. 이번 분기에는 신규 가입자가 꾸준히 늘었고 작성한 문서를 보강했다. ";
  await p.setContent(`<style>body{font:13pt/1.6 sans-serif}section{page-break-after:always}</style>` +
    [1, 2, 3].map((n) => `<section><h1>Test page ${n}</h1><p>${para.repeat(12)}</p></section>`).join(""));
  fs.writeFileSync(path.join(TMP, "text.pdf"), await p.pdf({ format: "A4" }));
  // issued certificates: one that needs a password to open, one that opens but has editing locked
  // (the password one has photos, so it's over the size targets and really goes to the server)
  if (HAS_GS) for (const [name, lock, src] of [["password.pdf", "-sUserPassword=030301", "photo.pdf"], ["locked.pdf", "-dPermissions=-3904", "text.pdf"]])
    spawnSync("gs", ["-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite", "-sOwnerPassword=owner", lock, "-dEncryptionR=3", "-dKeyLength=128",
      "-dPassThroughJPEGImages=true", "-sOutputFile=" + path.join(TMP, name), path.join(TMP, src)]);
  await p.close();
}

// one JPEG per page, embedded as-is (like a phone's "photos to PDF")
function jpegPdf(jpegs) {
  const objs = [], pages = [];
  const add = (o) => objs.push(o) && objs.length;
  const cat = add(null), pg = add(null);
  for (const j of jpegs) {
    const { w, h } = imageSize(j), W = 612, H = Math.round((612 * h) / w);
    const im = add(Buffer.concat([Buffer.from(`<< /Type /XObject /Subtype /Image /Width ${w} /Height ${h} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${j.length} >>\nstream\n`), j, Buffer.from("\nendstream")]));
    const cs = `q ${W} 0 0 ${H} 0 0 cm /Im0 Do Q`;
    const c = add(Buffer.from(`<< /Length ${cs.length} >>\nstream\n${cs}\nendstream`));
    pages.push(add(Buffer.from(`<< /Type /Page /Parent ${pg} 0 R /MediaBox [0 0 ${W} ${H}] /Resources << /XObject << /Im0 ${im} 0 R >> >> /Contents ${c} 0 R >>`)));
  }
  objs[cat - 1] = Buffer.from(`<< /Type /Catalog /Pages ${pg} 0 R >>`);
  objs[pg - 1] = Buffer.from(`<< /Type /Pages /Kids [${pages.map((p) => p + " 0 R").join(" ")}] /Count ${pages.length} >>`);
  const parts = [Buffer.from("%PDF-1.4\n")], offs = [];
  let len = parts[0].length;
  objs.forEach((o, i) => { const b = Buffer.concat([Buffer.from(`${i + 1} 0 obj\n`), o, Buffer.from("\nendobj\n")]); offs.push(len); parts.push(b); len += b.length; });
  parts.push(Buffer.from(`xref\n0 ${objs.length + 1}\n0000000000 65535 f \n` + offs.map((o) => String(o).padStart(10, "0") + " 00000 n \n").join("") +
    `trailer\n<< /Size ${objs.length + 1} /Root ${cat} 0 R >>\nstartxref\n${len}\n%%EOF\n`));
  return Buffer.concat(parts);
}

// ------------------------------------------------------------------ page plumbing

async function open(browser, url, { mobile = false } = {}) {
  const ctx = await browser.newContext(mobile ? { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true } : { viewport: { width: 1280, height: 900 } });
  await ctx.route(/cloud\.umami\.is|cloudflareinsights|googlesyndication/, (r) => r.abort());
  await ctx.addInitScript(() => {
    window.__ev = [];
    Object.defineProperty(window, "umami", { value: { track: (n, p) => window.__ev.push([n, p]) } });
  });
  const p = await ctx.newPage();
  const problems = [];
  p.on("pageerror", (e) => problems.push("script error: " + e.message));
  p.on("console", (m) => { if (m.type() === "error" && !/ERR_FAILED|net::/.test(m.text())) problems.push("console: " + m.text().slice(0, 160)); });
  p.on("response", (r) => { if (r.url().startsWith(BASE) && r.status() >= 400) problems.push(`HTTP ${r.status()} ${r.url().slice(BASE.length)}`); });
  await p.goto(BASE + url, { waitUntil: "networkidle" });
  p.problems = problems;
  p.close2 = () => ctx.close();
  return p;
}

// Click #go (or `go`) and wait for the download link or an error message.
async function runTool(p, { go = "#go", done = "#dl", timeout = 120000 } = {}) {
  await p.waitForSelector(go + ":not([disabled])", { timeout: 30000 });
  // On a phone the button is usually tapped at the bottom of the screen; the result must still
  // end up on screen (it used to appear below the fold, and people tapped the button again).
  if (MOBILE) await p.evaluate((go) => { const r = document.querySelector(go).getBoundingClientRect(); scrollBy(0, r.bottom - innerHeight + 10); }, go);
  await p.click(go);
  await p.waitForFunction(([done]) => {
    const err = document.querySelector("#error");
    if (err && err.offsetParent !== null && err.textContent.trim()) return true;
    const d = document.querySelector(done);
    return !!d && d.offsetParent !== null;
  }, [done], { timeout });
  const err = await p.$eval("#error", (e) => (e.offsetParent !== null ? e.textContent.trim() : "")).catch(() => "");
  if (err) throw new Error("tool showed an error: " + err);
  if (MOBILE) {
    await p.waitForTimeout(800);   // smooth scroll
    const off = await p.$eval(done, (d) => { const r = d.getBoundingClientRect(); return r.top < 0 || r.bottom > innerHeight ? `top ${Math.round(r.top)} of ${innerHeight}` : ""; });
    if (off) throw new Error("download button is off screen after the run: " + off);
  }
}

// Photo pages: the ID photo pages (data-live) make the photo as soon as it's added and remake it
// after every change, with no button; the others have a button. Either way, wait for a result
// that matches the current settings.
async function photoResult(p) {
  if (await p.isVisible("#go")) return runTool(p, { done: "#result a[download], #result .warn" });
  await p.waitForFunction(() => {
    const err = document.querySelector("#error");
    if (err && err.offsetParent !== null && err.textContent.trim()) return true;
    const r = document.querySelector("#result");
    return r.offsetParent !== null && !r.classList.contains("busy") && !!r.querySelector("a[download], .warn");
  }, null, { timeout: 60000 });
  const err = await p.$eval("#error", (e) => (e.offsetParent !== null ? e.textContent.trim() : "")).catch(() => "");
  if (err) throw new Error("tool showed an error: " + err);
}

async function download(p, sel = "#dl") {
  const [dl] = await Promise.all([p.waitForEvent("download", { timeout: 60000 }), p.click(sel)]);
  return { bytes: fs.readFileSync(await dl.path()), name: dl.suggestedFilename() };
}

async function select(p, sel, value) {
  await p.selectOption(sel, value);
  await p.dispatchEvent(sel, "change");
}

// ------------------------------------------------------------------ the tool tests

const F = (n) => path.join(TMP, n);
const TEXT = ["Test page 1", "가입자가", "작성한"];   // must survive every PDF tool

function toolTests() {
  const T = [];
  const both = (page, name, fn) => { for (const pre of ["", "/ko"]) T.push({ name: `${pre || "/en"}/${page} ${name}`.replace("/en/", "/"), url: `${pre}/${page}`, fn }); };

  both("", "sharp mode keeps text, shrinks photos", async (p) => {
    await p.setInputFiles("#pdf", F("text.pdf")); await runTool(p);
    let r = await download(p); let e = pdfCheck(r.bytes, { pages: 3, text: TEXT }); if (e) return e;
    await p.reload({ waitUntil: "networkidle" });
    await p.setInputFiles("#pdf", F("photo.pdf")); await runTool(p);
    r = await download(p);
    if (r.bytes.length > fs.statSync(F("photo.pdf")).size * 0.3) return "photo PDF only shrank to " + KB(r.bytes.length);
    return pdfCheck(r.bytes, { pages: 2 });
  });
  both("", "server down: falls back to the browser", async (p) => {
    p.expected = /502/;
    await p.route("**/api/compress", (r) => r.fulfill({ status: 502, contentType: "text/html", body: "<html>Bad gateway</html>" }));
    await p.setInputFiles("#pdf", F("photo.pdf")); await runTool(p);
    const fell = await p.evaluate(() => window.__ev.some((e) => e[0] === "error" && e[1].kind === "fallback"));
    if (!fell) return "no fallback recorded";
    await p.evaluate(() => { window.__ev = window.__ev.filter((e) => e[1]?.kind !== "fallback"); });   // expected here
    return pdfCheck((await download(p)).bytes, { pages: 2 });
  });
  both("", "a broken PDF shows a message, not a crash", async (p) => {
    p.expected = /InvalidPDF|Invalid PDF/;
    await p.setInputFiles("#pdf", { name: "broken.pdf", mimeType: "application/pdf", buffer: Buffer.from("%PDF-1.4\nthis is not really a pdf\n%%EOF") });
    await select(p, "#mode", "browser");
    await p.click("#go");
    await p.waitForFunction(() => document.querySelector("#error")?.offsetParent !== null || document.querySelector("#dl")?.offsetParent !== null, null, { timeout: 30000 });
    return (await p.$eval("#error", (e) => e.offsetParent !== null)) ? null : "no error message for a broken file";
  });
  // A PDF that needs a password used to come back from the server as a blank page, shown as "−94%".
  const shownError = async (p) => {
    await p.waitForFunction(() => document.querySelector("#error")?.offsetParent !== null || document.querySelector("#dl")?.offsetParent !== null, null, { timeout: 60000 });
    return p.$eval("#error", (e) => (e.offsetParent !== null ? e.textContent.trim() : ""));
  };
  for (const page of ["", "compress-pdf-to-300kb.html"]) both(page, "a PDF that needs a password says so, no blank file", async (p) => {
    if (!HAS_GS) return null;
    p.expected = /422|password/i;
    await p.setInputFiles("#pdf", F("password.pdf")); await p.click("#go");
    const msg = await shownError(p);
    return /needs a password|암호가 필요한/.test(msg) ? null : msg ? "message: " + msg : "a download was offered";
  });
  // Editing-locked PDFs gave pdf-lib's English "is encrypted ... ignoreEncryption" and used up a turn.
  for (const [page, setup] of [
    ["merge.html", (p) => p.setInputFiles("#pdfs", [F("locked.pdf"), F("text.pdf")])],
    ["split.html", (p) => p.setInputFiles("#pdf", F("locked.pdf"))],
    ["rotate.html", (p) => p.setInputFiles("#pdf", F("locked.pdf"))],
    ["delete-pages.html", async (p) => { await p.setInputFiles("#pdf", F("locked.pdf")); await p.fill("#pages", "1"); }],
    ["add-page-numbers.html", (p) => p.setInputFiles("#pdf", F("locked.pdf"))],
    ["watermark.html", (p) => p.setInputFiles("#pdf", F("locked.pdf"))],
    ["organize.html", (p) => p.setInputFiles("#pdf", F("locked.pdf"))],
  ]) both(page, "an editing-locked PDF says so and uses no turn", async (p) => {
    if (!HAS_GS) return null;
    p.expected = /is encrypted/;
    let used = 0;
    p.on("request", (r) => { if (r.url().includes("/api/consume")) used++; });
    await setup(p);
    await p.waitForTimeout(800);
    if (!(await p.isVisible("#error")) && await p.isEnabled("#go")) await p.click("#go");
    const msg = await shownError(p);
    if (!/is locked|편집 제한이 걸린/.test(msg)) return msg ? "message: " + msg : "a download was offered";
    return used ? "it used up one of the day's turns" : null;
  });
  // One bad file in a pick used to stop the rest of the pick from being added (and the list wasn't redrawn).
  both("merge.html", "a rejected file doesn't drop the rest of the pick", async (p) => {
    if (!HAS_GS) return null;
    p.expected = /is encrypted/;
    await p.setInputFiles("#pdfs", [F("locked.pdf"), F("text.pdf"), F("photo.pdf")]);
    await p.waitForFunction(() => document.querySelectorAll("#filelist li").length === 2, null, { timeout: 10000 }).catch(() => {});
    const names = await p.$$eval("#filelist li", (l) => l.map((li) => li.textContent));
    if (names.length !== 2) return `${names.length} files in the list, expected text.pdf and photo.pdf`;
    if (!(await p.isVisible("#error"))) return "no message about the locked file";
    await runTool(p).catch(() => {});   // the message about the locked file is still up, so check the result directly
    await p.waitForSelector("#dl", { state: "visible", timeout: 60000 });
    return pdfCheck((await download(p)).bytes, { pages: 5 });
  });
  // People drop photos on PDF tools: they get a link to the tool that takes photos.
  for (const [page, href] of [["", "compress-image.html"], ["compress-pdf-to-300kb.html", "compress-image.html?target=300KB"],
                              ["merge.html", "jpg-to-pdf.html"], ["sign-pdf.html", "jpg-to-pdf.html"]])
    both(page, "a photo gets a link to the photo tool", async (p) => {
      await p.setInputFiles(page === "merge.html" ? "#pdfs" : "#pdf", F("photo.jpg"));
      const a = await p.waitForSelector("#error a", { timeout: 5000 }).catch(() => null);
      if (!a) return "no link in the error message";
      const h = await a.getAttribute("href");
      return h.endsWith("/" + href) ? null : "the link goes to " + h;
    });
  both("rotate.html", "a PDF with no proper file type still opens", async (p) => {
    // Playwright fills in an empty type from the name, so test the other case apps send
    await p.setInputFiles("#pdf", { name: "scan.pdf", mimeType: "application/octet-stream", buffer: fs.readFileSync(F("text.pdf")) });
    if (await p.evaluate(() => document.querySelector("#pdf").files[0].type) !== "application/octet-stream") return "test file got a type";
    await runTool(p);
    return pdfCheck((await download(p)).bytes, { pages: 3 });
  });
  for (const lv of ["balanced", "small", "pages"]) both("", `private mode, ${lv}`, async (p) => {
    await p.setInputFiles("#pdf", F(lv === "pages" ? "text.pdf" : "photo.pdf"));
    await select(p, "#mode", "browser"); await select(p, "#blevel", lv);
    await runTool(p);
    const r = await download(p);
    return pdfCheck(r.bytes, lv === "pages" ? { pages: 3 } : { pages: 2 });
  });
  for (const t of ["50kb", "100kb", "200kb", "300kb", "500kb", "1mb", "2mb"]) both(`compress-pdf-to-${t}.html`, "fits the target", async (p) => {
    await p.setInputFiles("#pdf", F("photo.pdf")); await runTool(p);
    const r = await download(p), lim = kbRange(t.toUpperCase());
    if (r.bytes.length > lim.max) return `result ${KB(r.bytes.length)} is over ${t}`;
    return pdfCheck(r.bytes, { pages: 2 });
  });
  both("compress-pdf-for-email.html", "keeps more than 150 dpi when 10MB has room", async (p) => {
    let dpi = null;
    p.on("response", async (r) => { if (r.url().includes("/api/compress")) dpi = (await r.json().catch(() => ({}))).dpi || 150; });
    const inSize = fs.statSync(F("photos3.pdf")).size;
    if (inSize <= 10e6) return `fixture is only ${KB(inSize)}`;
    await p.setInputFiles("#pdf", F("photos3.pdf")); await runTool(p);
    const r = await download(p);
    if (r.bytes.length > 10e6) return `result ${KB(r.bytes.length)} is over 10MB`;
    if (!(dpi > 150)) return `server went down to ${dpi} dpi though the limit had room (result ${KB(r.bytes.length)})`;
    return pdfCheck(r.bytes, { pages: 3 });
  });
  both("compress-pdf-for-email.html", "fits the target", async (p) => {
    await p.setInputFiles("#pdf", F("photo.pdf")); await runTool(p);
    const r = await download(p);
    if (r.bytes.length > kbRange(await p.$eval("#target", (s) => s.value)).max) return "over the email limit";
    return pdfCheck(r.bytes, { pages: 2 });
  });
  both("merge.html", "2 + 3 pages", async (p) => {
    await p.setInputFiles("#pdfs", [F("photo.pdf"), F("text.pdf")]); await runTool(p);
    return pdfCheck((await download(p)).bytes, { pages: 5, text: TEXT });
  });
  both("split.html", "each page, and a range", async (p) => {
    await p.setInputFiles("#pdf", F("text.pdf")); await runTool(p);
    const n = zipCount((await download(p)).bytes); if (n !== 3) return `ZIP has ${n} files, expected 3`;
    await select(p, "#mode", "range");
    for (const [typed, want] of [["2-3", [2, 3]], ["1, 3", [1, 3]], ["1", [1]]]) {
      await p.fill("#range", typed); await runTool(p);
      const r = await download(p);
      const err = pdfCheck(r.bytes, { pages: want.length, text: want.map((n) => `Test page ${n}`) });
      if (err) return `"${typed}": ${err}`;
      if (typed === "2-3" && r.name !== "text_2-3.pdf") return `range file is named ${r.name}`;
    }
    await p.fill("#range", "9"); await p.click("#go");
    return await p.waitForFunction(() => /\S/.test(document.querySelector("#error")?.textContent || ""), null, { timeout: 5000 }).then(() => null, () => '"9" in a 3-page PDF shows no error');
  });
  both("delete-pages.html", "remove page 2", async (p) => {
    await p.setInputFiles("#pdf", F("text.pdf")); await p.fill("#pages", "2"); await runTool(p);
    return pdfCheck((await download(p)).bytes, { pages: 2, text: ["Test page 1", "Test page 3"] });
  });
  both("rotate.html", "90°", async (p) => {
    await p.setInputFiles("#pdf", F("text.pdf")); await select(p, "#angle", "90"); await runTool(p);
    return pdfCheck((await download(p)).bytes, { pages: 3, rotate: 90 });
  });
  both("organize.html", "save", async (p) => {
    await p.setInputFiles("#pdf", F("text.pdf")); await runTool(p);
    return pdfCheck((await download(p)).bytes, { pages: 3, text: TEXT });
  });
  both("add-page-numbers.html", "numbers", async (p) => {
    await p.setInputFiles("#pdf", F("text.pdf")); await runTool(p);
    return pdfCheck((await download(p)).bytes, { pages: 3, text: TEXT });
  });
  both("watermark.html", "default text", async (p) => {
    await p.setInputFiles("#pdf", F("text.pdf"));
    const mark = await p.$eval("#text", (e) => e.value);
    await runTool(p);
    const r = await download(p);
    // Latin text is written as text; other scripts (대외비) are drawn as an image
    if (!/^[\x20-\x7e]+$/.test(mark) && render(r.bytes) === render(fs.readFileSync(F("text.pdf")))) return "no watermark on page 1";
    return pdfCheck(r.bytes, { pages: 3, text: /^[\x20-\x7e]+$/.test(mark) ? [mark, ...TEXT] : TEXT });
  });
  both("watermark.html", "tiled long phrase", async (p) => {
    await p.setInputFiles("#pdf", F("text.pdf"));
    await p.fill("#text", "햇살카페 알바 채용 서류 제출용 2026.11.4");
    await select(p, "#style", "tiled"); await runTool(p);
    const r = await download(p);
    if (render(r.bytes) === render(fs.readFileSync(F("text.pdf")))) return "no watermark on page 1";
    return pdfCheck(r.bytes, { pages: 3, text: TEXT });
  });
  both("pdf-to-jpg.html", "3 images", async (p) => {
    await p.setInputFiles("#pdf", F("text.pdf")); await runTool(p);
    const n = zipCount((await download(p)).bytes);
    return n === 3 ? null : `ZIP has ${n} files, expected 3`;
  });
  both("jpg-to-pdf.html", "2 photos", async (p) => {
    await p.setInputFiles("#images", [F("photo.jpg"), F("photo2.jpg")]); await runTool(p);
    if (await p.isVisible("#fitrow")) return "the Limit row shows with no limit chosen";
    return pdfCheck((await download(p)).bytes, { pages: 2 });
  });
  both("jpg-to-pdf.html", "under 200KB", async (p) => {
    await p.setInputFiles("#images", [F("photo.jpg"), F("photo2.jpg")]);
    await select(p, "#target", "200KB"); await runTool(p);
    const r = await download(p);
    if (r.bytes.length > 200000) return `${KB(r.bytes.length)} is over 200KB`;
    if (!(await p.textContent("#fit")).includes("✓")) return "the result doesn't say it fits";
    return pdfCheck(r.bytes, { pages: 2 });
  });
  both("jpg-to-pdf.html?target=150KB", "size from the link", async (p) => {
    if ((await p.$eval("#target", (s) => s.value)) !== "custom" || (await p.inputValue("#kmax")) !== "150") return "?target=150KB didn't set a 150KB limit";
    await p.setInputFiles("#images", F("photo.jpg")); await runTool(p);
    const r = await download(p);
    return r.bytes.length > 150000 ? `${KB(r.bytes.length)} is over 150KB` : pdfCheck(r.bytes, { pages: 1 });
  });
  both("receipt-to-pdf.html", "5 receipts, 4 per page → 2 pages", async (p) => {
    await p.setInputFiles("#images", [F("photo.jpg"), F("photo2.jpg"), F("photo.jpg"), F("photo2.jpg"), F("photo.jpg")]); await runTool(p);
    if (await p.isVisible("#fitrow")) return "the Limit row shows with no limit chosen";
    return pdfCheck((await download(p)).bytes, { pages: 2 });
  });
  both("receipt-to-pdf.html", "a text file among the photos: photos kept, error shown", async (p) => {
    await p.setInputFiles("#images", [F("photo.jpg"), F("notes.txt"), F("photo2.jpg")]);
    const n = await p.$$eval("#filelist li", (l) => l.length);
    if (n !== 2) return `${n} files in the list, expected the 2 photos`;
    if (!(await p.isVisible("#error"))) return "no message about the text file";
    await runTool(p);
    return pdfCheck((await download(p)).bytes, { pages: 1 });
  });
  both("receipt-to-pdf.html", "faded receipt on a dark table: clearer text makes the print dark", async (p) => {
    await p.setInputFiles("#images", F("faded.jpg"));
    await select(p, "#per", "1"); await p.check("#clear"); await p.uncheck("#number"); await runTool(p);
    const r = await download(p), e = pdfCheck(r.bytes, { pages: 1 });
    if (e || !HAS_GS) return e;
    // the middle of the paper, where the print is: some of it must be dark
    const g = grayPage(r.bytes, 50);
    let dark = 0, all = 0;
    for (let y = Math.round(g.h * 0.3); y < g.h * 0.7; y++) for (let x = Math.round(g.w / 2 - 40); x < g.w / 2 + 40; x++, all++) if (g.px[y * g.w + x] < 100) dark++;
    return dark / all > 0.03 ? null : `the print didn't turn dark (${(100 * dark / all).toFixed(1)}% dark pixels on the paper)`;
  });
  // Share of the page that is dark table: the photo's table is cut away and the crooked receipt
  // turned straight, so (almost) none of it is left; with the option off it is most of the photo
  const tableShare = (bytes) => {
    const g = grayPage(bytes, 30);
    let dark = 0;
    for (const v of g.px) if (v < 95) dark++;
    return dark / g.px.length;
  };
  both("receipt-to-pdf.html", "receipt photo on a dark table: cut out and straightened", async (p) => {
    await p.setInputFiles("#images", F("tilted.jpg"));
    await select(p, "#per", "1"); await p.uncheck("#number");
    if (!(await p.isChecked("#crop"))) return "cutting out the receipt isn't on by default";
    await runTool(p);
    const r = await download(p), e = pdfCheck(r.bytes, { pages: 1 });
    if (e || !HAS_GS) return e;
    const cut = tableShare(r.bytes);
    await p.uncheck("#crop"); await runTool(p);
    const kept = tableShare((await download(p)).bytes);
    if (kept < 0.3) return `the test photo shows too little table (${(100 * kept).toFixed(0)}%) to tell`;
    return cut < 0.03 ? null : `${(100 * cut).toFixed(1)}% of the page is still table (${(100 * kept).toFixed(0)}% without cutting)`;
  });
  both("receipt-to-pdf.html", "cover fields: the store box has room on a phone", async (p) => {
    await p.setInputFiles("#images", [F("photo.jpg"), F("photo2.jpg")]); await p.check("#cover");
    const w = await p.$eval(".rc-shop", (e) => e.getBoundingClientRect().width);
    const fs16 = await p.$eval(".rc-shop", (e) => parseFloat(getComputedStyle(e).fontSize));
    if (MOBILE && fs16 < 16) return `the boxes use ${fs16}px text, so iPhones zoom in when tapped`;
    return w >= 140 ? null : `the store box is only ${Math.round(w)}px wide`;
  });
  both("receipt-to-pdf.html", "iPhone HEIC photo", async (p) => {
    if (!fs.existsSync(F("photo.heic"))) return null;   // no sips (not macOS): nothing to test with
    await p.setInputFiles("#images", [F("photo.heic"), F("photo2.jpg")]);
    await select(p, "#per", "1"); await runTool(p);
    const r = await download(p), e = pdfCheck(r.bytes, { pages: 2 });
    if (e || !HAS_GS) return e;
    // the HEIC page must hold the photo, not an empty frame: page 1 drawn as grey must not be near-white
    const gray = Buffer.from(render(r.bytes), "base64");
    return gray.length < 3000 ? `page 1 looks empty (${gray.length} bytes as PNG)` : null;
  });
  both("receipt-to-pdf.html", "6 phone photos under 1MB, one per page: pages are saved smaller", async (p) => {
    await p.setInputFiles("#images", Array(6).fill(F("photo.jpg")));
    await select(p, "#per", "1"); await select(p, "#target", "1MB"); await runTool(p);
    const r = await download(p);
    if (r.bytes.length > 1000000) return `${KB(r.bytes.length)} is over 1MB`;
    if (!/dpi/.test(await p.textContent("#note"))) return "the note doesn't say how the pages were made smaller: " + (await p.textContent("#note"));
    return pdfCheck(r.bytes, { pages: 6 });
  });
  both("receipt-to-pdf.html", "1 per page + cover + clear text → cover page added", async (p) => {
    await p.setInputFiles("#images", [F("photo.jpg"), F("photo2.jpg")]);
    await select(p, "#per", "1"); await p.check("#clear"); await p.check("#cover");
    await p.fill("#c-title", "경비 Receipts"); await p.fill(".rc-amount >> nth=0", "12,000"); await p.fill(".rc-amount >> nth=1", "3,500");
    await runTool(p);
    return pdfCheck((await download(p)).bytes, { pages: 3 });
  });
  both("receipt-to-pdf.html", "under 2MB", async (p) => {
    await p.setInputFiles("#images", [F("photo.jpg"), F("photo2.jpg"), F("photo.jpg"), F("photo2.jpg")]);
    await select(p, "#per", "2"); await select(p, "#target", "2MB"); await runTool(p);
    const r = await download(p);
    if (r.bytes.length > 2000000) return `${KB(r.bytes.length)} is over 2MB`;
    if (!(await p.textContent("#fit")).includes("✓")) return "the result doesn't say it fits";
    return pdfCheck(r.bytes, { pages: 2 });
  });
  both("receipt-to-pdf.html?target=1MB", "size from the link", async (p) => {
    if ((await p.$eval("#target", (s) => s.value)) !== "1MB") return "?target=1MB didn't set the 1MB limit";
    return null;
  });
  both("jpg-to-pdf.html", "sideways phone photo stands upright", async (p) => {
    await p.setInputFiles("#images", F("sideways.jpg")); await runTool(p);
    const r = await download(p), e = pdfCheck(r.bytes, { pages: 1 });
    if (e || !HAS_GS) return e;
    const f = path.join(TMP, "check.pdf");
    const box = String(spawnSync("gs", ["-q", "-dNODISPLAY", "-dNOSAFER", "-c", `(${f}) (r) file runpdfbegin 1 pdfgetpage /MediaBox pget pop == quit`]).stdout).match(/[\d.]+/g).map(Number);
    return box[3] - box[1] > box[2] - box[0] ? null : `page is ${box[2] - box[0]}×${box[3] - box[1]}: lying on its side`;
  });
  both("sign-pdf.html", "typed signature", async (p) => {
    await p.setInputFiles("#pdf", F("text.pdf"));
    await p.waitForFunction(() => document.querySelector("#pagecanvas")?.width > 0, null, { timeout: 30000 });
    await p.click('.tab[data-mode="type"]'); await p.fill("#name", "J. Rivera");
    await p.click("#add"); await runTool(p);
    const r = await download(p);
    if (render(r.bytes) === render(fs.readFileSync(F("text.pdf")))) return "page 1 looks the same as before: no signature on it";
    return pdfCheck(r.bytes, { pages: 3, text: TEXT });
  });

  // photos: every resize preset, with the KB target the page picks for it
  const PRESETS = objectLiteral("js/compress-image.js", "PRESETS");
  async function photo(p, { resize, target, format, expect = {} }) {
    await p.setInputFiles("#images", F("photo.jpg"));
    if (format) await select(p, "#format", format);
    if (resize) await select(p, "#resize", resize);
    if (target) await select(p, "#target", target);
    const tgt = await p.$eval("#target", (s) => s.value);
    await photoResult(p);
    const warn = await p.$$eval("#result .warn", (a) => a.map((e) => e.textContent).join(" "));
    if (warn) return "result warning: " + warn.trim();
    const r = await download(p, "#result a[download]");
    const s = imageSize(r.bytes);
    if (!s) return "result is not an image";
    if (format && s.type !== format) return `saved as ${s.type}, expected ${format}`;
    const want = PRESETS[resize || (await p.$eval("#resize", (e) => e.value))];
    if (want && (s.w !== want[0] || s.h !== want[1])) return `${s.w}×${s.h}, expected ${want[0]}×${want[1]}`;
    if (!want && Math.max(s.w, s.h) > 1920) return `${s.w}×${s.h} is over 1920`;
    // fixed sizes are saved at 300 dpi (JFIF header right after SOI: units 1, X and Y density 300)
    const b = r.bytes, dpi = b[3] === 0xe0 && b[13] === 1 ? [(b[14] << 8) | b[15], (b[16] << 8) | b[17]] : null;
    if (want && s.type === "jpeg" && !(dpi && dpi[0] === 300 && dpi[1] === 300)) return `saved at ${dpi ? dpi.join("×") + " dpi" : "no dpi"}, expected 300 dpi`;
    // a preset with a range the list lacks (China visa 40–120KB) fills in the custom fields
    const lim = tgt === "custom" ? await p.evaluate(() => ({ min: +document.querySelector("#kmin").value * 1024, max: +document.querySelector("#kmax").value * 1000 })) : kbRange(tgt);
    if (lim && (r.bytes.length > lim.max || r.bytes.length < lim.min)) return `${KB(r.bytes.length)} is outside ${tgt === "custom" ? `${lim.min}–${lim.max} bytes` : tgt}`;
    if (expect.min && r.bytes.length < expect.min) return `${KB(r.bytes.length)} is under ${KB(expect.min)}`;
    return null;
  }
  both("compress-image.html", "defaults", (p) => photo(p, {}));
  both("compress-image.html", "20–50KB range", (p) => photo(p, { target: "20-50KB" }));
  both("compress-image.html", "WebP 100KB", (p) => photo(p, { target: "100KB", format: "webp" }));
  for (const t of ["20kb", "50kb", "100kb", "200kb"]) both(`compress-image-to-${t}.html`, "fits", (p) => photo(p, {}));
  // the Korean page leaves out the US visa (own page) and Indian exam sizes
  const NOT_KO = ["us-visa", "bank-photo", "upsc-photo"];
  for (const r of Object.keys(PRESETS)) both("compress-id-photo.html", `preset ${r}`, async (p) => !(NOT_KO.includes(r) && p.url().includes("/ko/")) ? photo(p, { resize: r })
    : (await p.$(`#resize option[value="${r}"]`)) ? `${r} is still in the Korean size list` : null);
  both("us-visa-photo.html", "600×600, 54–240KB", (p) => photo(p, { expect: { min: 54000 } }));
  both("compress-id-photo.html", "KUKSIWON picks 413×531, 500KB", async (p) => {
    const err = await photo(p, { resize: "kr-kuksiwon" });
    const v = await p.evaluate(() => document.querySelector("#target").value);
    return err || (v === "500KB" ? null : `the size limit is "${v}", expected 500KB`);
  });
  both("compress-id-photo.html", "China visa picks 40–120KB", async (p) => {
    const err = await photo(p, { resize: "cn-visa" });
    const v = await p.evaluate(() => ["#target", "#kmin", "#kmax"].map((q) => document.querySelector(q).value).join(" "));
    return err || (v === "custom 40 120" ? null : `the size limit is "${v}", expected custom 40–120`);
  });
  both("compress-id-photo.html", "made without a button, follows the zoom", async (p) => {
    await p.setInputFiles("#images", F("photo.jpg"));
    await photoResult(p);
    if (await p.isVisible("#go")) return "the Compress button is still shown for one photo";
    // the frame is far down the page (under the exam chips): the first result scrolls to it
    const inView = () => { const t = document.querySelector("#crop").getBoundingClientRect().top; return t >= 0 && t < innerHeight * 0.6; };
    if (!(await p.waitForFunction(inView, null, { timeout: 3000 }).then(() => true, () => false))) return "the crop frame wasn't brought into view after adding a photo";
    const a = await download(p, "#result a[download]");
    await p.$eval("#zoom", (z) => { z.value = 200; z.dispatchEvent(new Event("input")); });
    await photoResult(p);
    const b = await download(p, "#result a[download]"), s = imageSize(b.bytes);
    if (!s || s.w !== PRESETS["id-3x4"][0] || s.h !== PRESETS["id-3x4"][1]) return `zoomed photo is ${s && s.w}×${s && s.h}`;
    return Buffer.compare(a.bytes, b.bytes) ? null : "zooming didn't change the photo";
  });
  both("compress-id-photo.html", "two photos use the button", async (p) => {
    await p.setInputFiles("#images", [F("photo.jpg"), F("photo2.jpg")]);
    if (!(await p.isVisible("#go"))) return "no Compress button for two photos";
    await runTool(p, { done: "#dlzip" });
    const n = await p.$$eval("#result li a[download]", (a) => a.length);
    return n === 2 ? null : `${n} downloads, expected 2`;
  });

  // signatures: every preset from a photo of a paper signature
  const SIGS = objectLiteral("js/signature-image.js", "PRESETS");
  for (const [k, v] of Object.entries(SIGS)) both("signature-image.html", `preset ${k}`, async (p) => {
    await p.click('.tab[data-mode="upload"]');
    await p.setInputFiles("#sigfile", F("sig.png"));
    await select(p, "#size", k);
    await runTool(p);
    const r = await download(p), s = imageSize(r.bytes);
    if (!s || s.w !== v.box[0] || s.h !== v.box[1]) return `${s && s.w}×${s && s.h}, expected ${v.box.join("×")}`;
    const lim = kbRange(v.target);
    if (r.bytes.length > lim.max || r.bytes.length < lim.min) return `${KB(r.bytes.length)} is outside ${v.target}KB`;
    return null;
  });

  // pasted form rules (sentences people really paste into Google): the box sets size and KB range
  // before any photo is added, and the file that comes out meets them
  const PASTED = [
    ["compress-id-photo.html", "width 140px,height 110px. image should not exceed 50kb. (jpg format)", { w: 140, h: 110, max: 50 }],
    ["compress-image-to-50kb.html", "Photo 200 x 230 pixels, file size 20 KB to 50 KB, JPG", { w: 200, h: 230, min: 20, max: 50 }],
    ["signature-image.html", "the signature must be in blue or black only. upload jpeg/jpg file with aspect ratio of signature (height : width) = 1 : r, where r must be between 2.75 and 3.75. signature must occupy 70-80% of the image. the file size should be between 3 kb and 300 kb",
      { ratio: [2.75, 3.75], min: 3, max: 300 }],
    ["compress-id-photo.html", "사진 크기는 400 x 500 픽셀로 변경되며 1 : 1.25 비율로 맞춰주셔야 사진이 정상적으로 보입니다. 파일은 50kbyte를 초과할 수 없습니다.", { w: 400, h: 500, max: 50 }],
    ["compress-id-photo.html", "크기: 가로 115~235픽셀, 세로 150~315픽셀 형식: PNG 파일 권장(JPG, GIF, PNG 파일 가능) 용량: 500KB 이하", { w: 235, h: 315, max: 500 }],
  ];
  for (const [page, text, want] of PASTED) both(page, `pasted rules "${text.slice(0, 24)}…"`, async (p) => {
    const fold = await p.$("details.specs:not([open]) > summary");   // Korean ID photo page: folded into one line
    if (fold) await fold.click();
    if (!(await p.isVisible("#specs"))) return "the paste box is hidden before a file is added";
    await p.fill("#specs", text);
    await p.waitForSelector("#specsout:not([hidden])");
    const sig = page.startsWith("signature");
    if (sig) { await p.click('.tab[data-mode="upload"]'); await p.setInputFiles("#sigfile", F("sig.png")); await runTool(p); }
    else { await p.setInputFiles("#images", F("photo.jpg")); await photoResult(p); }
    const warn = sig ? "" : await p.$$eval("#result .warn", (a) => a.map((e) => e.textContent).join(" "));
    if (warn) return "result warning: " + warn.trim();
    const r = await download(p, sig ? "#dl" : "#result a[download]"), s = imageSize(r.bytes);
    if (!s) return "result is not an image";
    if (want.w && (s.w !== want.w || s.h !== want.h)) return `${s.w}×${s.h}, expected ${want.w}×${want.h}`;
    if (want.ratio && (s.w / s.h < want.ratio[0] || s.w / s.h > want.ratio[1])) return `${s.w}×${s.h}: width/height outside ${want.ratio.join("–")}`;
    if (r.bytes.length > want.max * 1000 || r.bytes.length < (want.min || 0) * 1024) return `${KB(r.bytes.length)} is outside ${want.min || 0}–${want.max}KB`;
    return null;
  });
  const live =["/ sharp mode", "/ko/ sharp mode", "/compress-pdf-to-1mb.html"];
  return T.filter((t) => (!filters.length || filters.some((f) => t.name.includes(f))) && (!LIVE || live.some((l) => t.name.startsWith(l))));
}

// ------------------------------------------------------------------ the page checks

async function pageChecks(browser) {
  const xml = await (await fetch(BASE + "/sitemap.xml")).text();
  const urls = [...xml.matchAll(/<loc>https:\/\/pdfslimio\.com([^<]*)<\/loc>/g)].map((m) => m[1]);
  const links = new Set(), fails = [];
  for (const u of urls) {
    const p = await open(browser, u, { mobile: true });
    const over = await p.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    if (over > 1) p.problems.push(`scrolls sideways by ${over}px at phone width`);
    // phones: the upload box says "tap" (no drag and drop there) and starts on the first screen
    // (an iPhone shows about 660px of a page under Safari's bars)
    const drop = await p.evaluate(() => { const d = document.querySelector(".drop"); return d && { top: d.getBoundingClientRect().top + scrollY, title: d.querySelector(".drop-title").textContent }; });
    if (drop && /drop|click|끌어다|클릭/i.test(drop.title)) p.problems.push(`upload box says "${drop.title}" on a phone`);
    if (drop && drop.top > 600) p.problems.push(`upload box starts at ${Math.round(drop.top)}px, below the first phone screen`);
    // guides: the tool button sits on the first phone screen, and a bar with it shows while
    // reading but not over the end box (search visitors used to leave before reaching any button)
    if (/\/guides\/.+\.html$/.test(u)) {
      const g = await p.evaluate(async () => {
        const top = document.querySelector(".cta-top"), bar = document.querySelector(".cta-sticky"), end = document.querySelector(".cta-box");
        if (!top || !bar || !end) return "no tool button under the intro";
        const y = top.getBoundingClientRect().top + scrollY;
        if (y > 600) return `tool button starts at ${Math.round(y)}px, below the first phone screen`;
        const wait = () => new Promise((r) => setTimeout(r, 300));
        scrollTo(0, y + 1200); await wait();
        if (!bar.classList.contains("on")) return "the button bar does not show while reading";
        end.scrollIntoView({ block: "center" }); await wait();
        if (bar.classList.contains("on")) return "the button bar still shows over the end box";
        scrollTo(0, 0); await wait();
        // the list at the end offers guides in the same language (picked by topic in gen_guides.py)
        const rel = [...document.querySelectorAll(".related a.guide-card")].map((a) => a.getAttribute("href"));
        const dir = location.pathname.replace(/[^/]*$/, "");
        if (rel.length < 3 || rel.some((h) => !h.startsWith(dir))) return `related guides: ${rel.join(", ") || "none"}`;
      });
      if (g) p.problems.push(g);
    }
    const ev = await p.evaluate(() => window.__ev.filter((e) => e[0] === "error").map((e) => e[1].kind + ": " + e[1].msg));
    p.problems.push(...ev.map((e) => "error event " + e));
    for (const h of await p.$$eval("a[href^='/'], img[src^='/'], link[href^='/'], script[src^='/']", (a) => a.map((e) => e.getAttribute("href") || e.getAttribute("src"))))
      links.add(h.split("#")[0]);
    if (p.problems.length) fails.push([u, p.problems]);
    await p.close2();
  }
  for (const l of links) {
    if (!l) continue;
    const r = await fetch(BASE + l, { redirect: "follow" });
    if (r.status >= 400) fails.push([l, [`link returns HTTP ${r.status}`]]);
  }
  return { count: urls.length, links: links.size, fails };
}

// ------------------------------------------------------------------ main

// A server left over from an earlier run would answer instead of ours (ours can't bind the port),
// so the tests would quietly check whatever code that one was started with.
if (!LIVE && await fetch(BASE + "/").then(() => true, () => false)) {
  console.error(`Port ${PORT} is already in use (a test server from an earlier run?). Stop it and run again.`);
  fs.rmSync(TMP, { recursive: true, force: true });
  process.exit(2);
}
const server = LIVE ? null : spawn("node", [path.join(ROOT, "server/server.cjs")], {
  env: { ...process.env, PORT: String(PORT), HOST: "127.0.0.1", DAILY_LIMIT: "100000", IP_DAILY_LIMIT: "100000" },
  stdio: "ignore",
});
let code = 0;
try {
  for (let i = 0; i < 50; i++) { try { if ((await fetch(BASE + "/")).ok) break; } catch {} await new Promise((r) => setTimeout(r, 200)); }
  if (!HAS_GS) console.log("! Ghostscript not found: page counts and text are not checked");
  const browser = await chromium.launch({ channel: "chrome" });
  const failed = [];
  if (!onlyPages) {
    await makeFixtures(browser);
    for (const t of toolTests()) {
      const started = Date.now();
      const p = await open(browser, t.url, { mobile: MOBILE });
      let err;
      try { err = await t.fn(p); } catch (e) { err = e.message.split("\n")[0]; }
      const ev = await p.evaluate(() => window.__ev.filter((e) => e[0] === "error" && e[1].kind !== "shown").map((e) => e[1].kind + ": " + e[1].msg)).catch(() => []);
      const probs = [...p.problems, ...ev].filter((m) => !(p.expected && p.expected.test(m)));
      if (!err && probs.length) err = probs.join("; ");
      console.log(`${err ? "✗" : "✓"} ${t.name} (${((Date.now() - started) / 1000).toFixed(1)}s)${err ? "\n    " + err : ""}`);
      if (err) failed.push(t.name);
      await p.close2();
    }
  }
  if (onlyPages || !filters.length) {
    const r = await pageChecks(browser);
    for (const [u, probs] of r.fails) console.log(`✗ ${u}\n    ${probs.join("\n    ")}`);
    console.log(`${r.fails.length ? "✗" : "✓"} ${r.count} sitemap pages, ${r.links} internal links checked`);
    if (r.fails.length) failed.push("pages");
  }
  await browser.close();
  console.log(failed.length ? `\n${failed.length} failed` : "\nall passed");
  code = failed.length ? 1 : 0;
} catch (e) {
  console.error(e); code = 2;
} finally {
  if (server) server.kill();
  fs.rmSync(TMP, { recursive: true, force: true });
}
process.exit(code);
