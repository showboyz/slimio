// Measures what the seven size pages really do to one made-up phone-scan PDF (3 pages, ~3.6MB).
// Usage: node tools/measure_pdf_sizes.mjs <output dir>   -> scan3.pdf, out-<size>.pdf, result.json
// Then turn result.json into tools/measured.json (bytes, mode images|kept, dpi) and run tools/gen_measured.py.
import { chromium } from "playwright-core";
import { spawn, spawnSync } from "child_process";
import fs from "fs";
const ROOT = new URL("..", import.meta.url).pathname, PORT = 3195, BASE = `http://127.0.0.1:${PORT}`, OUT = process.argv[2] || ".";
const server = spawn("node", [ROOT + "/server/server.cjs"], { env: { ...process.env, PORT: String(PORT), HOST: "127.0.0.1", DAILY_LIMIT: "100000", IP_DAILY_LIMIT: "100000" }, stdio: "ignore" });
for (let i = 0; i < 50; i++) { try { if ((await fetch(BASE + "/")).ok) break; } catch {} await new Promise((r) => setTimeout(r, 200)); }
function imageSize(b) { for (let i = 2; i < b.length - 9;) { if (b[i] !== 0xff) { i++; continue; } const m = b[i + 1], len = b.readUInt16BE(i + 2); if (m >= 0xc0 && m <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(m)) return { w: b.readUInt16BE(i + 7), h: b.readUInt16BE(i + 5) }; i += 2 + len; } }
function jpegPdf(jpegs) {
  const objs = [], pages = []; const add = (o) => objs.push(o) && objs.length; const cat = add(null), pg = add(null);
  for (const j of jpegs) { const { w, h } = imageSize(j), W = 595, H = Math.round((595 * h) / w);
    const im = add(Buffer.concat([Buffer.from(`<< /Type /XObject /Subtype /Image /Width ${w} /Height ${h} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${j.length} >>\nstream\n`), j, Buffer.from("\nendstream")]));
    const cs = `q ${W} 0 0 ${H} 0 0 cm /Im0 Do Q`; const c = add(Buffer.from(`<< /Length ${cs.length} >>\nstream\n${cs}\nendstream`));
    pages.push(add(Buffer.from(`<< /Type /Page /Parent ${pg} 0 R /MediaBox [0 0 ${W} ${H}] /Resources << /XObject << /Im0 ${im} 0 R >> >> /Contents ${c} 0 R >>`))); }
  objs[cat - 1] = Buffer.from(`<< /Type /Catalog /Pages ${pg} 0 R >>`); objs[pg - 1] = Buffer.from(`<< /Type /Pages /Kids [${pages.map((p) => p + " 0 R").join(" ")}] /Count ${pages.length} >>`);
  const parts = [Buffer.from("%PDF-1.4\n")], offs = []; let len = parts[0].length;
  objs.forEach((o, i) => { const b = Buffer.concat([Buffer.from(`${i + 1} 0 obj\n`), o, Buffer.from("\nendobj\n")]); offs.push(len); parts.push(b); len += b.length; });
  parts.push(Buffer.from(`xref\n0 ${objs.length + 1}\n0000000000 65535 f \n` + offs.map((o) => String(o).padStart(10, "0") + " 00000 n \n").join("") + `trailer\n<< /Size ${objs.length + 1} /Root ${cat} 0 R >>\nstartxref\n${len}\n%%EOF\n`));
  return Buffer.concat(parts);
}
const browser = await chromium.launch({ channel: "chrome" });
const fx = await browser.newPage();
await fx.goto(BASE + "/");
// a phone-scan style page: paper with an uneven shadow, printed lines, a table, a stamp, sensor noise
const scanPage = (n) => fx.evaluate(async (n) => {
  const w = 1654, h = 2339, c = new OffscreenCanvas(w, h), x = c.getContext("2d");
  const g = x.createLinearGradient(0, 0, w, h); g.addColorStop(0, "#f6f3ec"); g.addColorStop(1, "#dcd6c8"); x.fillStyle = g; x.fillRect(0, 0, w, h);
  x.fillStyle = "#1c1c1c"; x.font = "bold 62px sans-serif"; x.fillText(["Certificate of Enrollment", "Statement of Results", "Application Form"][n], 140, 220);
  x.font = "36px serif";
  const words = "The applicant named below has completed all required courses and met the conditions set out in the regulations of the institution for the academic year";
  for (let i = 0; i < 30; i++) x.fillText(words.slice((i * 7) % 40, (i * 7) % 40 + 78), 140, 340 + i * 52);
  x.strokeStyle = "#333"; x.lineWidth = 3;
  for (let r = 0; r < 7; r++) { x.strokeRect(140, 1960 - 0 + r * 0, 0, 0); }
  x.strokeRect(140, 1950, 1370, 250); for (let r = 1; r < 5; r++) { x.beginPath(); x.moveTo(140, 1950 + r * 50); x.lineTo(1510, 1950 + r * 50); x.stroke(); }
  x.font = "30px monospace"; for (let r = 0; r < 5; r++) x.fillText(`Item ${r + 1}     ${(r + 3) * 1234}     2026-10-${10 + r}`, 160, 1985 + r * 50);
  x.strokeStyle = "#b32020"; x.lineWidth = 6; x.beginPath(); x.arc(1280, 1650, 110, 0, 7); x.stroke(); x.fillStyle = "#b32020"; x.font = "bold 34px sans-serif"; x.fillText("APPROVED", 1190, 1660);
  const d = x.getImageData(0, 0, w, h), a = d.data;
  for (let i = 0; i < a.length; i += 4) { const k = (Math.random() - 0.5) * 30; a[i] += k; a[i + 1] += k; a[i + 2] += k; }
  x.putImageData(d, 0, 0);
  const b = await c.convertToBlob({ type: "image/jpeg", quality: 0.85 });
  return Array.from(new Uint8Array(await b.arrayBuffer()));
}, n);
const pages = []; for (let i = 0; i < 3; i++) pages.push(Buffer.from(await scanPage(i)));
const input = jpegPdf(pages); fs.writeFileSync(OUT + "/scan3.pdf", input); fs.writeFileSync(OUT + "/scan3-p1.jpg", pages[0]);
console.log("input", input.length);
const result = { input: { bytes: input.length, pages: 3 }, pdf: {} };
for (const t of ["50kb", "100kb", "200kb", "300kb", "500kb", "1mb", "2mb"]) {
  const p = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await p.goto(BASE + `/compress-pdf-to-${t}.html`, { waitUntil: "networkidle" });
  await p.setInputFiles("#pdf", OUT + "/scan3.pdf");
  await p.waitForSelector("#go:not([disabled])"); const t0 = Date.now(); await p.click("#go");
  await p.waitForFunction(() => { const e = document.querySelector("#error"); if (e && e.offsetParent && e.textContent.trim()) return true; const d = document.querySelector("#dl"); return !!d && d.offsetParent !== null; }, null, { timeout: 120000 });
  const err = await p.$eval("#error", (e) => (e.offsetParent ? e.textContent.trim() : "")).catch(() => "");
  if (err) { console.log(t, "ERROR", err); result.pdf[t] = { error: err }; await p.close(); continue; }
  const [dl] = await Promise.all([p.waitForEvent("download"), p.click("#dl")]);
  const buf = fs.readFileSync(await dl.path()); fs.writeFileSync(`${OUT}/out-${t}.pdf`, buf);
  const pg = (buf.toString("latin1").match(/\/Type\s*\/Page[^s]/g) || []).length;
  const msg = await p.$eval("#result", (e) => e.innerText.replace(/\s+/g, " ").slice(0, 200)).catch(() => "");
  result.pdf[t] = { bytes: buf.length, pages: pg, secs: Math.round((Date.now() - t0) / 100) / 10, msg };
  console.log(t, buf.length, "pages", pg, "|", msg);
  await p.close();
}
fs.writeFileSync(OUT + "/result.json", JSON.stringify(result, null, 1));
await browser.close(); server.kill();
