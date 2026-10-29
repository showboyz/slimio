// hl.cjs <screenshot.png> <x0> <x1> <y0> [after.png] : prints "cx cy n", the centre (screenshot pixels) of Chrome's
// active find-match highlight (#FF9632) between columns x0 and x1 and below row y0, or "none". With a second
// screenshot taken after the find bar closed, only pixels that lost the colour count, so orange in a post image
// is ignored. Used by tblfix.py to click the found cell.
const sharp = require('sharp');
const [file, x0, x1, y0, after] = [process.argv[2], +process.argv[3], +process.argv[4], +process.argv[5] || 0, process.argv[6]];
const raw = f => sharp(f).removeAlpha().raw().toBuffer({ resolveWithObject: true });
const hit = (d, i) => Math.abs(d[i] - 255) < 8 && Math.abs(d[i + 1] - 150) < 14 && Math.abs(d[i + 2] - 50) < 18;
Promise.all([raw(file), after ? raw(after) : null]).then(([{ data, info }, b]) => {
  let sx = 0, sy = 0, n = 0;
  for (let y = y0; y < info.height; y++) for (let x = x0; x < Math.min(x1, info.width); x++) {
    const i = (y * info.width + x) * 3;
    if (hit(data, i) && !(b && b.info.width === info.width && hit(b.data, i))) { sx += x; sy += y; n++; }
  }
  console.log(n > 20 ? `${Math.round(sx / n)} ${Math.round(sy / n)} ${n}` : 'none');
});
