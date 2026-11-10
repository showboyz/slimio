// node marketing/naver/card.mjs <card.html> <out.jpg> [width=1200] : renders a blog picture drawn in HTML (title card,
// summary chart, experiment result) to a JPG for public/img/blog. The page is laid out at <width> CSS px and the
// picture is the size of its <body>. JPEG quality steps down from 92 until the file is at most 200KB (marketing/WRITING.md 4).
// The scripts that drew the October pictures lived in a scratchpad and were deleted with it; this one stays in the repo.
import { chromium } from "playwright-core";
import fs from "node:fs";
import path from "node:path";

const [src, out, w = "1200"] = process.argv.slice(2);
if (!src || !out) { console.error("usage: card.mjs <card.html> <out.jpg> [width]"); process.exit(2); }
const browser = await chromium.launch({ channel: "chrome" });
const page = await browser.newPage({ viewport: { width: +w, height: 600 }, deviceScaleFactor: 1 });
await page.goto("file://" + path.resolve(src));
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(300);
const body = await page.$("body");
let q = 92, buf;
for (; q >= 50; q -= 4) {
  buf = await body.screenshot({ type: "jpeg", quality: q });
  if (buf.length <= 200 * 1024) break;
}
await browser.close();
fs.writeFileSync(out, buf);
const box = buf.length > 200 * 1024 ? " (still over 200KB)" : "";
console.log(`${out}: ${(buf.length / 1024).toFixed(1)}KB, quality ${Math.max(q, 50)}${box}`);
