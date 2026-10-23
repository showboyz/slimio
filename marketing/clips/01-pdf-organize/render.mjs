import { chromium } from 'playwright-core';
import fs from 'fs';
const FPS=30, DUR=Number(process.argv[2]||21);
fs.rmSync('frames',{recursive:true,force:true}); fs.mkdirSync('frames');
const b = await chromium.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
const p = await (await b.newContext({ viewport:{width:1080,height:1920}, deviceScaleFactor:1 })).newPage();
await p.goto('file://'+process.cwd()+'/scene.html'); await p.waitForTimeout(800);
const only = process.argv[3];
for (let f=0; f<FPS*DUR; f++) {
  const t=f/FPS; if (only && !only.split(',').map(Number).some(x=>Math.abs(x-t)<1e-6)) continue;
  await p.evaluate(t=>window.seek(t), t);
  await p.screenshot({ path:`frames/${String(f).padStart(5,'0')}.png` });
}
await b.close();
