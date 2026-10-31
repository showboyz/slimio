// banner.mjs <jobs.json> : renders each {html, out} job (one box, see banners.py) to a PNG of just the box, at 2x.
import fs from "fs";
import { chromium } from "../../../node_modules/playwright-core/index.mjs";

const jobs = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const browser = await chromium.launch({ channel: "chrome" });
const page = await browser.newPage({ viewport: { width: 700, height: 600 }, deviceScaleFactor: 2 });
for (const { html, out } of jobs) {
  await page.setContent(`<!doctype html><meta charset="utf-8"><body style="margin:0;background:transparent;
    font-family:-apple-system,'Apple SD Gothic Neo','Noto Sans KR',sans-serif"><div id="b" style="width:620px;padding:0 0">${html}</div>`);
  const box = await page.$("#b > div");
  await box.evaluate(e => (e.style.margin = "0"));
  await box.screenshot({ path: out, omitBackground: true });
  console.log(out);
}
await browser.close();
