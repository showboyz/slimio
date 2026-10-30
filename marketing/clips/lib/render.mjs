// node render.mjs <clip dir> : renders <dir>/spec.json with clip.html to <dir>/<name>.mp4 (30fps, 1080×1920, silent AAC track)
// and <dir>/cover.jpg (a frame from the first scene). Needs ffmpeg and the repo's playwright-core.
import { chromium } from '../../../node_modules/playwright-core/index.mjs';
import { execFileSync } from 'child_process';
import fs from 'fs'; import path from 'path';
const dir = path.resolve(process.argv[2]); const lib = path.dirname(new URL(import.meta.url).pathname);
const spec = JSON.parse(fs.readFileSync(dir + '/spec.json', 'utf8'));
const frames = dir + '/frames'; fs.rmSync(frames, { recursive: true, force: true }); fs.mkdirSync(frames);
const b = await chromium.launch({ channel: 'chrome' });
const p = await (await b.newContext({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 })).newPage();
for (const s of spec.scenes) if (s.img) s.img = 'file://' + path.resolve(dir, s.img);
await p.addInitScript(S => { window.SPEC = S; }, spec);
await p.goto(`file://${lib}/clip.html`);
const total = await p.evaluate(() => window.ready); await p.waitForTimeout(500);
const FPS = 30, N = Math.round(total * FPS);
for (let f = 0; f < N; f++) {
  await p.evaluate(t => window.seek(t), f / FPS);
  await p.screenshot({ path: `${frames}/${String(f).padStart(5, '0')}.png` });
}
await p.evaluate(t => window.seek(t), spec.coverAt ?? 1.2); await p.screenshot({ path: dir + '/cover.jpg', type: 'jpeg', quality: 90 });
await b.close();
const out = `${dir}/${spec.name}.mp4`;
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', '30', '-i', `${frames}/%05d.png`, '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-shortest',
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'slow', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', out]);
fs.rmSync(frames, { recursive: true, force: true });
console.log(out, total.toFixed(1) + 's', (fs.statSync(out).size / 1e6).toFixed(2) + 'MB');
