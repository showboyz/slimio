const { PDFDocument } = PDFLib;
const drop = $("drop");
const controls = $("controls");
const filelist = $("filelist");
const goBtn = $("go");
const result = $("result");
const dl = $("dl");
const prog = SlimIO.bindProgress("prog");

// A4 at 150 dpi. Every page is drawn on a canvas and put in the PDF as one JPEG, so the
// cover table (Korean text included), the numbers and the faded-text fix all share one path.
const PW = 1240, PH = 1754, MARGIN = 60, GAP = 28;
const A4 = [595.28, 841.89];
const AREA = { w: PW - MARGIN * 2, h: PH - MARGIN * 2 - 30 };   // where receipts go, above the page number
const FONT = '"Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR","Segoe UI",Arial,sans-serif';
const COVER_ROWS = 22;   // receipts listed per cover page
const QUALITY = 0.9;     // JPG quality of the pages when there is no size limit

let items = [];   // { name, size, file, modified, date, shop, amount }

function escapeHtml(s) {
    return String(s).replace(/[&<>"]/g, (c) =>
        ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

function coverOn() { return $("cover").checked; }

function render() {
    filelist.innerHTML = "";
    items.forEach((it, i) => {
        const li = document.createElement("li");
        li.className = "rc-item";
        li.innerHTML =
            `<span class="fname">${i + 1}. ${escapeHtml(it.name)} <span class="fsize">${SlimIO.formatSize(it.size)}</span></span>`;
        const actions = document.createElement("span");
        actions.style.display = "flex";
        actions.style.gap = "6px";
        ["up", "down", "rm"].forEach((a) => {
            const b = document.createElement("button");
            b.className = "fbtn";
            b.title = { up: SlimIO.t("Move up"), down: SlimIO.t("Move down"), rm: SlimIO.t("Remove") }[a];
            b.textContent = { up: "▲", down: "▼", rm: "✕" }[a];
            b.addEventListener("click", () => onItemAction(a, i));
            actions.appendChild(b);
        });
        li.appendChild(actions);
        if (coverOn()) {
            const row = document.createElement("div");
            row.className = "rc-fields";
            [["date", "Date", 16], ["shop", "Store / purpose", 40], ["amount", "Amount", 16]].forEach(([k, ph, max]) => {
                const inp = document.createElement("input");
                inp.type = "text";
                inp.placeholder = SlimIO.t(ph);
                inp.setAttribute("aria-label", `${i + 1}. ${SlimIO.t(ph)}`);
                inp.maxLength = max;
                if (k === "amount") inp.inputMode = "decimal";
                inp.value = it[k];
                inp.className = "rc-" + k;
                inp.addEventListener("input", () => { it[k] = inp.value; });
                row.appendChild(inp);
            });
            li.appendChild(row);
        }
        filelist.appendChild(li);
    });
    goBtn.disabled = items.length === 0;
    controls.classList.toggle("hidden", items.length === 0);
    $("sortrow").hidden = items.length < 2;
    SlimIO.refreshStatus();
}

function onItemAction(action, i) {
    if (action === "up" && i > 0) { [items[i - 1], items[i]] = [items[i], items[i - 1]]; render(); }
    else if (action === "down" && i < items.length - 1) { [items[i + 1], items[i]] = [items[i], items[i + 1]]; render(); }
    else if (action === "rm") { items.splice(i, 1); render(); }
}

// Natural order, so "receipt 2" comes before "receipt 10"
$("sort-name").addEventListener("click", () => {
    items.sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }));
    render();
});
$("sort-date").addEventListener("click", () => {
    items.sort((a, b) => a.modified - b.modified || a.name.localeCompare(b.name, undefined, { numeric: true }));
    render();
});
$("cover").addEventListener("change", () => { $("coverbox").hidden = !coverOn(); render(); });

// HEIC (iPhone) photos copied to a computer often have no image type at all, so they go by name,
// and the file dialog is told to show them. Phones keep plain image/*: iPhones turn HEIC into JPG
// themselves unless the list names HEIC, and Android shows its photo picker only for image types.
function looksHeic(f) { return /\.(heic|heif)$/i.test(f.name) || /^image\/hei[cf]/i.test(f.type); }
const PHONE = /Android|iP(hone|ad|od)/.test(navigator.userAgent) || (/Mac/.test(navigator.platform) && navigator.maxTouchPoints > 1);
if (!PHONE) $("images").accept = "image/*,.heic,.heif";

function addFiles(list) {
    SlimIO.clearError();
    let skipped = 0;
    for (const f of list) {
        if (!f.type.startsWith("image/") && !looksHeic(f)) { skipped++; continue; }
        items.push({ name: f.name, size: f.size, file: f, modified: f.lastModified || 0, date: "", shop: "", amount: "" });
    }
    render();
    if (skipped) SlimIO.showError(SlimIO.t("Please choose image files (JPG, PNG, WebP…)."));
}

drop.addEventListener("click", () => $("images").click());
$("images").addEventListener("change", (e) => { addFiles(e.target.files); e.target.value = ""; });
drop.addEventListener("dragover", (e) => { e.preventDefault(); drop.classList.add("drag"); });
drop.addEventListener("dragleave", () => drop.classList.remove("drag"));
drop.addEventListener("drop", (e) => {
    e.preventDefault();
    drop.classList.remove("drag");
    if (e.dataTransfer.files.length) addFiles(e.dataTransfer.files);
});

// PDF size limit: "5MB", "500KB" or "custom" with the KB box. 0 = no limit.
// Decimal (1KB = 1000 bytes), so the file passes whichever way a form counts.
function limitBytes() {
    const v = $("target").value;
    if (v === "custom") { const kb = Number($("kmax").value); return kb >= 50 ? Math.round(kb * 1000) : 0; }
    const m = v.match(/^(\d+(?:\.\d+)?)(KB|MB)$/i);
    return m ? Math.round(parseFloat(m[1]) * (m[2].toUpperCase() === "MB" ? 1e6 : 1e3)) : 0;
}
function limitLabel() {
    return $("target").value === "custom" ? Math.round(Number($("kmax").value)) + "KB" : $("target").value;
}
$("target").addEventListener("change", () => { $("krange").hidden = $("target").value !== "custom"; });
// ?target=5MB from guides and links; a size that isn't in the menu goes in the KB box
(() => {
    const t = (new URLSearchParams(location.search).get("target") || "").toUpperCase();
    const m = t.match(/^(\d+(?:\.\d+)?)(KB|MB)$/);
    if (!m) return;
    if ([...$("target").options].some((o) => o.value === t)) $("target").value = t;
    else { $("target").value = "custom"; $("kmax").value = Math.round(parseFloat(m[1]) * (m[2] === "MB" ? 1000 : 1)); }
})();
$("krange").hidden = $("target").value !== "custom";

// Most browsers other than Safari can't open HEIC, so a decoder (about 650KB) is fetched the
// first time one needs it.
const HEIC_LIB = "https://cdn.jsdelivr.net/npm/heic-to@1.5.2/dist/iife/heic-to.js";
let heicLib = null;
function loadHeic() {
    if (!heicLib) heicLib = new Promise((resolve, reject) => {
        const s = document.createElement("script");
        s.src = HEIC_LIB;
        s.onload = () => (window.HeicTo ? resolve(window.HeicTo) : reject(new Error("no decoder")));
        s.onerror = () => { heicLib = null; reject(new Error(SlimIO.t("The HEIC photo decoder could not be loaded. Check your connection and try again."))); };
        document.head.appendChild(s);
    });
    return heicLib;
}
// HEIF files say so in their first bytes: "ftyp" and a brand such as heic or mif1
async function isHeic(file) {
    const b = new Uint8Array(await file.slice(0, 12).arrayBuffer());
    const s = String.fromCharCode(...b);
    return s.slice(4, 8) === "ftyp" && ["heic", "heix", "hevc", "hevx", "heim", "heis", "mif1", "msf1"].includes(s.slice(8, 12));
}

// Decoded with the EXIF rotation applied, so phone photos stand the right way up
async function decode(file) {
    try { if (window.createImageBitmap) return await createImageBitmap(file, { imageOrientation: "from-image" }); } catch (e) { /* <img> below */ }
    const url = URL.createObjectURL(file);
    try { const img = new Image(); img.src = url; await img.decode(); return img; } catch (e) { /* HEIC below */ } finally { URL.revokeObjectURL(url); }
    if (!looksHeic(file) && !(await isHeic(file))) return null;
    const label = goBtn.textContent;
    goBtn.textContent = SlimIO.t("Opening HEIC photos…");
    try { return await (await loadHeic())({ blob: file, type: "bitmap" }); }
    catch (e) { if (e && e.message && heicLib === null) throw e; return null; }   // a failed download says so; a bad file is "Could not read"
    finally { goBtn.textContent = label; }
}

function release(pic) {
    if (pic.close) pic.close();
    else if (pic.getContext) { pic.width = 0; pic.height = 0; }   // iOS counts canvas memory until it's emptied
}

// Where the receipt is in a photo of it lying on a table: the largest bright shape that the darker
// table surrounds. Worked out on a copy about 320 px long, so it takes a few milliseconds.
// Returns the receipt's box in the photo's pixels, measured from the photo's centre in a frame
// turned by `angle` (radians) so a slightly crooked receipt stands straight — or null when there is
// no receipt to cut out: a white table, a scan or screenshot, or a receipt that already fills the photo.
function findReceipt(pic) {
    const k = Math.min(1, 320 / Math.max(pic.width, pic.height));
    const w = Math.max(1, Math.round(pic.width * k)), h = Math.max(1, Math.round(pic.height * k)), n = w * h;
    const c = document.createElement("canvas");
    c.width = w; c.height = h;
    const cx = c.getContext("2d", { willReadFrequently: true });
    cx.drawImage(pic, 0, 0, w, h);
    const px = cx.getImageData(0, 0, w, h).data;
    release(c);
    const g = new Uint8Array(n), hist = new Uint32Array(256);
    for (let i = 0; i < n; i++) { g[i] = (px[i * 4] * 77 + px[i * 4 + 1] * 151 + px[i * 4 + 2] * 28) >> 8; hist[g[i]]++; }

    // Otsu's threshold: the grey level that best splits the photo into paper and table
    let all = 0;
    for (let v = 0; v < 256; v++) all += v * hist[v];
    let cnt = 0, acc = 0, best = -1, t = 128, gap = 0;
    for (let v = 0; v < 255; v++) {
        cnt += hist[v]; acc += v * hist[v];
        if (!cnt || cnt === n) continue;
        const dark = acc / cnt, bright = (all - acc) / (n - cnt), between = cnt * (n - cnt) * (bright - dark) ** 2;
        if (between > best) { best = between; t = v; gap = bright - dark; }
    }
    if (gap < 50) return null;   // paper and table about as bright: nothing to tell apart

    // The table: dark pixels joined to the photo's edge. If much of the edge is bright, the table
    // is white or the receipt fills the photo.
    const out = new Uint8Array(n), queue = new Int32Array(n);
    let qn = 0, edge = 0, brightEdge = 0;
    const seed = (i) => { edge++; if (g[i] > t) brightEdge++; else if (!out[i]) { out[i] = 1; queue[qn++] = i; } };
    for (let x = 0; x < w; x++) { seed(x); if (h > 1) seed((h - 1) * w + x); }
    for (let y = 1; y < h - 1; y++) { seed(y * w); if (w > 1) seed(y * w + w - 1); }
    if (brightEdge > edge * 0.35) return null;
    for (let q = 0; q < qn; q++) {
        const i = queue[q], x = i % w;
        for (const j of [x > 0 ? i - 1 : -1, x < w - 1 ? i + 1 : -1, i - w, i + w]) {
            if (j >= 0 && j < n && !out[j] && g[j] <= t) { out[j] = 1; queue[qn++] = j; }
        }
    }
    // Everything else, print and creases included, is paper or other things on the table; the
    // receipt is the biggest connected piece.
    const label = new Int32Array(n);
    let paper = null;
    for (let s = 0, id = 0; s < n; s++) {
        if (out[s] || label[s]) continue;
        id++; label[s] = id;
        let m = 0; queue[m++] = s;
        for (let q = 0; q < m; q++) {
            const i = queue[q], x = i % w;
            for (const j of [x > 0 ? i - 1 : -1, x < w - 1 ? i + 1 : -1, i - w, i + w]) {
                if (j >= 0 && j < n && !out[j] && !label[j]) { label[j] = id; queue[m++] = j; }
            }
        }
        if (!paper || m > paper.length) paper = queue.slice(0, m);
    }
    if (!paper || paper.length < n * 0.04 || paper.length > n * 0.9) return null;

    // Its tilt from the shape's second moments: turn the long side to the nearest upright or level
    let mx = 0, my = 0;
    for (const i of paper) { mx += i % w; my += (i / w) | 0; }
    mx /= paper.length; my /= paper.length;
    let sxx = 0, syy = 0, sxy = 0;
    for (const i of paper) { const dx = i % w - mx, dy = ((i / w) | 0) - my; sxx += dx * dx; syy += dy * dy; sxy += dx * dy; }
    const theta = 0.5 * Math.atan2(2 * sxy, sxx - syy);
    const half = (sxx + syy) / 2, r = Math.sqrt(((sxx - syy) / 2) ** 2 + sxy * sxy);
    let angle = Math.round(theta / (Math.PI / 2)) * (Math.PI / 2) - theta;
    // squarish shapes have no clear long side; under 0.5° isn't worth it, over 25° is a guess
    if ((half + r) / Math.max(1, half - r) < 1.15 || Math.abs(angle) > 0.44 || Math.abs(angle) < 0.009) angle = 0;

    // The box of the turned shape, ignoring a few stray pixels, plus a small margin
    const cos = Math.cos(angle), sin = Math.sin(angle);
    const xs = new Float32Array(paper.length), ys = new Float32Array(paper.length);
    paper.forEach((i, j) => {
        const dx = i % w + 0.5 - w / 2, dy = ((i / w) | 0) + 0.5 - h / 2;
        xs[j] = dx * cos - dy * sin; ys[j] = dx * sin + dy * cos;
    });
    xs.sort(); ys.sort();
    const at = (a, f) => a[Math.min(a.length - 1, Math.floor(a.length * f))];
    let x0 = at(xs, 0.002), x1 = at(xs, 0.998), y0 = at(ys, 0.002), y1 = at(ys, 0.998);
    const bw = x1 - x0, bh = y1 - y0;
    if (paper.length < bw * bh * 0.7) return null;   // not a rectangle: a hand, a pile, a curled strip
    if (bw * bh > n * 0.85) return null;             // the receipt nearly fills the photo already
    x0 -= bw * 0.015 + 1; x1 += bw * 0.015 + 1; y0 -= bh * 0.015 + 1; y1 += bh * 0.015 + 1;
    return { x: x0 / k, y: y0 / k, w: (x1 - x0) / k, h: (y1 - y0) / k, angle };
}

// A receipt is never drawn larger than the page's receipt area, so a 12-megapixel phone photo is
// shrunk to that as soon as it's read and the full-size copy freed. Thirty photos then add about
// 0.2GB to Chrome's memory instead of 1.7GB, which is what keeps a phone's browser from giving up.
// With `crop`, the table around the receipt is cut away first, from the full-size photo.
async function load(file, crop) {
    const full = await decode(file);
    if (!full) return null;
    const box = crop ? findReceipt(full) : null;
    const b = box || { x: -full.width / 2, y: -full.height / 2, w: full.width, h: full.height, angle: 0 };
    const s = Math.min(AREA.w / b.w, AREA.h / b.h, 1);
    if (!box && s >= 1) return full;
    const c = document.createElement("canvas");
    c.width = Math.max(1, Math.round(b.w * s)); c.height = Math.max(1, Math.round(b.h * s));
    const x = c.getContext("2d");
    x.fillStyle = "#fff"; x.fillRect(0, 0, c.width, c.height);
    x.imageSmoothingQuality = "high";
    x.setTransform(s, 0, 0, s, -b.x * s, -b.y * s);   // photo → turned around its centre → box
    x.rotate(b.angle);
    x.translate(-full.width / 2, -full.height / 2);
    x.drawImage(full, 0, 0);
    release(full);
    c.cropped = !!box;
    return c;
}

// Grid choice for one page: of the layouts that hold exactly n receipts (2 → 2×1 or 1×2,
// 6 → 3×2, 2×3 ...), the one that draws the receipts biggest. Tall, narrow receipts get
// columns; wide ones get rows.
function bestGrid(n, pics, area) {
    const cands = [];
    for (let c = 1; c <= n; c++) if (n % c === 0) cands.push([c, n / c]);
    let best = null;
    for (const [c, r] of cands) {
        const cw = (area.w - GAP * (c - 1)) / c, ch = (area.h - GAP * (r - 1)) / r;
        let score = 0;
        for (const p of pics) { const s = Math.min(cw / p.width, ch / p.height, 1.6); score += s * s * p.width * p.height; }
        if (!best || score > best.score) best = { c, r, cw, ch, score };
    }
    return best;
}

// Turns a drawn receipt black on white so faded thermal print shows. White is set by the paper
// (the brightest few percent of the photo) and black by the faintest print near that brightness,
// not by the photo as a whole: a dark table around a small receipt used to wash its print out.
function clearUp(ctx, x, y, w, h) {
    const d = ctx.getImageData(x, y, w, h), px = d.data, hist = new Uint32Array(256);
    for (let i = 0; i < px.length; i += 4) {
        const g = (px[i] * 77 + px[i + 1] * 151 + px[i + 2] * 28) >> 8;
        px[i] = g; hist[g]++;
    }
    // the grey level that a share q of the pixels at least `from` bright are darker than
    const level = (from, q) => {
        let total = 0, acc = 0;
        for (let v = from; v < 256; v++) total += hist[v];
        for (let v = from; v < 256; v++) { acc += hist[v]; if (acc >= total * q) return v; }
        return 255;
    };
    const paper = level(0, 0.97);
    const lo = Math.min(paper * 0.8, Math.max(paper * 0.55, level(Math.round(paper * 0.5), 0.02)));
    const span = Math.max(8, paper * 0.94 - lo);
    const map = new Uint8ClampedArray(256);   // a slight curve keeps faint strokes dark
    for (let v = 0; v < 256; v++) map[v] = 255 * Math.pow(Math.max(0, Math.min(1, (v - lo) / span)), 1.3);
    for (let i = 0; i < px.length; i += 4) px[i] = px[i + 1] = px[i + 2] = map[px[i]];
    ctx.putImageData(d, x, y);
}

function newPage() {
    const c = document.createElement("canvas");
    c.width = PW; c.height = PH;
    const x = c.getContext("2d");
    x.fillStyle = "#fff"; x.fillRect(0, 0, PW, PH);
    return { c, x };
}

function footer(x, n, total) {
    x.fillStyle = "#888"; x.font = `22px ${FONT}`; x.textAlign = "center"; x.textBaseline = "alphabetic";
    x.fillText(`${n} / ${total}`, PW / 2, PH - 26);
}

function amountOf(s) {
    const n = parseFloat(String(s).replace(/[^0-9.\-]/g, ""));
    return isFinite(n) ? n : 0;
}
// "12,000원" and "3,500원" add up to "15,500원"; a sign in front such as "$" is kept the same way.
// Mixed or missing units give a bare number.
function withUnit(list, n) {
    const vals = list.map((it) => it.amount.trim()).filter(Boolean);
    const same = (re) => { const u = vals.map((v) => v.match(re)[0].trim()); return u.every((s) => s === u[0]) ? u[0] : ""; };
    return same(/^[^\d.+\-]*/) + n.toLocaleString() + same(/[^\d.,]*$/);
}

// Shortens s with "…" until it fits maxW in the current font
function clip(x, s, maxW) {
    if (x.measureText(s).width <= maxW) return s;
    const ch = [...s];
    while (ch.length > 1 && x.measureText(ch.join("") + "…").width > maxW) ch.pop();
    return ch.join("") + "…";
}

// One page of n receipts (or fewer on the last page)
function receiptPage(pics, startNo, per, opts) {
    const { c, x } = newPage();
    const g = bestGrid(per, pics, AREA);
    pics.forEach((pic, k) => {
        const col = k % g.c, row = Math.floor(k / g.c);
        const cx = MARGIN + col * (g.cw + GAP), cy = MARGIN + row * (g.ch + GAP);
        const s = Math.min(g.cw / pic.width, g.ch / pic.height, 1.6);
        const w = Math.max(1, Math.round(pic.width * s)), h = Math.max(1, Math.round(pic.height * s));
        const dx = Math.round(cx + (g.cw - w) / 2), dy = Math.round(cy + (g.ch - h) / 2);
        x.imageSmoothingQuality = "high";
        x.drawImage(pic, dx, dy, w, h);
        if (opts.clear) clearUp(x, dx, dy, w, h);
        x.strokeStyle = "#bbb"; x.lineWidth = 2; x.strokeRect(dx - 1, dy - 1, w + 2, h + 2);
        if (opts.number) {
            const label = String(startNo + k);
            x.font = `bold 30px ${FONT}`;
            const bw = Math.max(46, x.measureText(label).width + 22);
            x.fillStyle = "#111"; x.fillRect(dx, dy, bw, 44);
            x.fillStyle = "#fff"; x.textAlign = "center"; x.textBaseline = "middle";
            x.fillText(label, dx + bw / 2, dy + 23);
        }
    });
    return c;
}

// Cover / list: title, who and when, then No. · Date · Store · Amount and the total.
function coverPages(list) {
    const title = $("c-title").value.trim() || SlimIO.t("Receipts");
    const who = $("c-who").value.trim();
    const hasAmount = list.some((it) => it.amount.trim());
    const total = hasAmount ? withUnit(list, list.reduce((n, it) => n + amountOf(it.amount), 0)) : "";
    const rowH = 54, width = PW - MARGIN * 2, out = [];
    for (let p = 0, first = true; p < list.length || first; p += COVER_ROWS, first = false) {
        const { c, x } = newPage();
        let y = MARGIN + 30;
        if (first) {
            x.fillStyle = "#111"; x.textAlign = "left"; x.textBaseline = "alphabetic";
            let size = 54;   // a long title gets a smaller font before it gets cut
            do x.font = `bold ${size}px ${FONT}`; while (x.measureText(title).width > width && (size -= 2) >= 36);
            x.fillText(clip(x, title, width), MARGIN, y + 40);
            y += 70;
            x.font = `28px ${FONT}`; x.fillStyle = "#444";
            if (who) { x.fillText(clip(x, who, width), MARGIN, y + 28); y += 44; }
            x.fillText(SlimIO.t(list.length === 1 ? "{n} receipt" : "{n} receipts", { n: list.length }) + (hasAmount ? " · " + SlimIO.t("Total") + " " + total : ""), MARGIN, y + 28);
            y += 70;
        } else y += 20;
        const cols = [MARGIN, MARGIN + 90, MARGIN + 330, PW - MARGIN];   // No | Date | Store | Amount (right edge)
        x.fillStyle = "#eee"; x.fillRect(MARGIN, y, width, rowH);
        x.fillStyle = "#111"; x.font = `bold 26px ${FONT}`; x.textBaseline = "middle";
        x.textAlign = "left";
        x.fillText("No.", cols[0] + 14, y + rowH / 2);
        x.fillText(SlimIO.t("Date"), cols[1], y + rowH / 2);
        x.fillText(SlimIO.t("Store / purpose"), cols[2], y + rowH / 2);
        x.textAlign = "right"; x.fillText(SlimIO.t("Amount"), cols[3] - 14, y + rowH / 2);
        y += rowH;
        x.font = `26px ${FONT}`;
        list.slice(p, p + COVER_ROWS).forEach((it, k) => {
            x.fillStyle = "#222"; x.textAlign = "left";
            x.fillText(String(p + k + 1), cols[0] + 14, y + rowH / 2);
            x.fillText(clip(x, it.date, cols[2] - cols[1] - 16), cols[1], y + rowH / 2);
            x.fillText(clip(x, it.shop, cols[3] - cols[2] - 230), cols[2], y + rowH / 2);
            x.textAlign = "right"; x.fillText(clip(x, it.amount, 200), cols[3] - 14, y + rowH / 2);
            y += rowH;
            x.strokeStyle = "#ddd"; x.lineWidth = 1.5;
            x.beginPath(); x.moveTo(MARGIN, y); x.lineTo(PW - MARGIN, y); x.stroke();
        });
        if (p + COVER_ROWS >= list.length && hasAmount) {
            x.font = `bold 30px ${FONT}`; x.fillStyle = "#111"; x.textAlign = "left";
            x.fillText(SlimIO.t("Total"), cols[2], y + rowH / 2 + 6);
            x.textAlign = "right"; x.fillText(clip(x, total, cols[3] - cols[2] - 140), cols[3] - 14, y + rowH / 2 + 6);
        }
        out.push(c);
    }
    return out;
}

function toJpeg(canvas, quality) {
    return new Promise((resolve, reject) => {
        canvas.toBlob(async (b) => {
            if (!b) return reject(new Error("toBlob failed"));
            try { resolve(new Uint8Array(await b.arrayBuffer())); } catch (e) { reject(e); }
        }, "image/jpeg", quality);
    });
}

// A finished page saved again smaller, for the size limit
async function reencode(jpeg, scale, quality) {
    const pic = await decode(new Blob([jpeg], { type: "image/jpeg" }));
    const c = document.createElement("canvas");
    c.width = Math.round(PW * scale); c.height = Math.round(PH * scale);
    const x = c.getContext("2d");
    x.imageSmoothingQuality = "high";
    x.drawImage(pic, 0, 0, c.width, c.height);
    release(pic);
    try { return await toJpeg(c, quality); } finally { release(c); }
}

async function build(jpegs) {
    const out = await PDFDocument.create();
    for (const j of jpegs) {
        const img = await out.embedJpg(j);
        out.addPage(A4).drawImage(img, { x: 0, y: 0, width: A4[0], height: A4[1] });
    }
    return out.save();
}

// Under a limit: quality goes down first, then the pixel size, until the whole PDF fits.
// A setting stops as soon as its pages add up to more than the limit; the last one, the
// smallest, always finishes so there is something to give back.
async function fitToLimit(pages, limit) {
    const full = await build(pages);
    if (full.length <= limit) return { bytes: full, scale: 1, q: QUALITY, fits: true };
    const rungs = [];
    for (const scale of [1, 0.8, 0.64, 0.5, 0.4]) for (const q of [0.85, 0.7, 0.55, 0.4]) rungs.push([scale, q]);
    for (let i = 0; i < rungs.length; i++) {
        const [scale, q] = rungs[i], last = i === rungs.length - 1;
        prog.set(Math.min(98, 45 + i * 3));
        const jpegs = [];
        let sum = 0;
        for (const page of pages) {
            const j = await reencode(page, scale, q);
            jpegs.push(j); sum += j.length;
            if (sum > limit && !last) break;
        }
        if (sum > limit && !last) continue;
        const bytes = await build(jpegs);
        if (bytes.length <= limit || last) return { bytes, scale, q, fits: bytes.length <= limit };
    }
}

async function convert() {
    if (items.length === 0) return;
    SlimIO.clearError();
    const limit = limitBytes();
    if ($("target").value === "custom" && !limit) { SlimIO.showError(SlimIO.t("Enter a size of at least 50KB.")); return; }
    goBtn.disabled = true;
    goBtn.textContent = SlimIO.t("Converting…");
    prog.show();
    result.style.display = "none";
    let group = [];
    try {
        const check = await SlimIO.consume();
        if (check && !check.ok) { SlimIO.showError(SlimIO.t("Daily limit reached. Come back tomorrow.")); return; }

        const per = Number($("per").value);
        const opts = { clear: $("clear").checked, number: $("number").checked, crop: $("crop").checked };
        let cropped = 0;
        const covers = coverOn() ? coverPages(items) : [];
        const count = covers.length + Math.ceil(items.length / per);
        // Pages are drawn one at a time and kept only as JPEG, with "3 / 5" at the foot
        const pages = [];
        const finish = async (c) => { footer(c.getContext("2d"), pages.length + 1, count); pages.push(await toJpeg(c, QUALITY)); release(c); };
        for (const c of covers) await finish(c);
        for (let i = 0; i < items.length; i += per) {
            for (const it of items.slice(i, i + per)) {
                const pic = await load(it.file, opts.crop);
                if (!pic) { SlimIO.showError(SlimIO.t('Could not read "{name}".', { name: it.name })); return; }
                if (pic.cropped) cropped++;
                group.push(pic);
            }
            const c = receiptPage(group, i + 1, per, opts);
            group.forEach(release); group = [];
            await finish(c);
            prog.set(Math.round((Math.min(i + per, items.length) / items.length) * (limit ? 45 : 95)));
        }

        const r = limit ? await fitToLimit(pages, limit) : { bytes: await build(pages), fits: true, scale: 1, q: QUALITY };
        SlimIO.event("receipt-to-pdf-result", { target: limit ? limitLabel() : "none", fits: r.fits, receipts: items.length,
            per, cover: covers.length > 0, clear: opts.clear, cropped, outKB: Math.round(r.bytes.length / 1024) });
        showResult(pages.length, r, limit);
    } catch (e) {
        SlimIO.showError(SlimIO.t("Conversion failed: {msg}", { msg: e.message }));
    } finally {
        group.forEach(release);
        goBtn.disabled = false;
        goBtn.textContent = SlimIO.t("Make PDF");
        prog.hide();
    }
}

goBtn.addEventListener("click", convert);

function showResult(pageCount, r, limit) {
    const bytes = r.bytes, label = limitLabel();
    result.style.display = "block";
    $("merged").textContent = SlimIO.t(items.length === 1 ? "{n} receipt" : "{n} receipts", { n: items.length }) + " · " + SlimIO.pages(pageCount);
    $("after").textContent = SlimIO.formatSize(bytes.length);
    $("fitrow").hidden = !limit;
    $("fit").textContent = r.fits ? SlimIO.t("✓ under {size}", { size: label }) : SlimIO.t("✗ over {size}", { size: label });
    const note = $("note");
    note.hidden = !limit;
    note.className = "note" + (r.fits ? "" : " warn");
    if (!limit) note.textContent = "";
    else if (r.fits && r.scale === 1 && r.q >= 0.85) note.textContent = SlimIO.t("Already under {size} — full quality.", { size: label });
    else if (r.fits) note.textContent = SlimIO.t("To fit {size}, the pages were saved at {dpi} dpi, JPG quality {q}%.", { size: label, dpi: Math.round(150 * r.scale), q: Math.round(r.q * 100) });
    else note.textContent = SlimIO.t("This is the smallest we could make it. To get under {size}, put fewer receipts in one PDF.", { size: label });
    dl.textContent = SlimIO.t("↓ Download PDF");
    dl.onclick = () => SlimIO.download(bytes, "receipts.pdf", "application/pdf");
    SlimIO.reveal(result);
}

SlimIO.refreshStatus();
