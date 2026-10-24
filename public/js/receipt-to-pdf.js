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
const FONT = '"Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR","Segoe UI",Arial,sans-serif';

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
            [["date", "Date", "text", 10], ["shop", "Store / purpose", "text", 40], ["amount", "Amount", "text", 14]].forEach(([k, ph]) => {
                const inp = document.createElement("input");
                inp.type = "text";
                inp.placeholder = SlimIO.t(ph);
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

function addFiles(list) {
    SlimIO.clearError();
    for (const f of list) {
        if (!f.type.startsWith("image/")) { SlimIO.showError(SlimIO.t("Please choose image files (JPG, PNG, WebP…).")); return; }
        items.push({ name: f.name, size: f.size, file: f, modified: f.lastModified || 0, date: "", shop: "", amount: "" });
    }
    render();
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

// Decoded with the EXIF rotation applied, so phone photos stand the right way up
async function decode(file) {
    try { if (window.createImageBitmap) return await createImageBitmap(file, { imageOrientation: "from-image" }); } catch (e) { /* <img> below */ }
    const url = URL.createObjectURL(file);
    try { const img = new Image(); img.src = url; await img.decode(); return img; } catch (e) { return null; } finally { URL.revokeObjectURL(url); }
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

// Stretches the grey levels of a drawn receipt so faded thermal paper turns black on white.
function clearUp(ctx, x, y, w, h) {
    const d = ctx.getImageData(x, y, w, h), px = d.data, hist = new Uint32Array(256);
    for (let i = 0; i < px.length; i += 4) {
        const g = (px[i] * 77 + px[i + 1] * 151 + px[i + 2] * 28) >> 8;
        px[i] = g; hist[g]++;
    }
    const total = w * h;
    let lo = 0, hi = 255, acc = 0;
    for (let v = 0; v < 256; v++) { acc += hist[v]; if (acc >= total * 0.01) { lo = v; break; } }
    acc = 0;
    for (let v = 255; v >= 0; v--) { acc += hist[v]; if (acc >= total * 0.35) { hi = v; break; } }   // paper is the bright majority
    if (hi - lo < 20) hi = Math.min(255, lo + 20);
    const k = 255 / (hi - lo);
    for (let i = 0; i < px.length; i += 4) {
        const v = Math.max(0, Math.min(255, (px[i] - lo) * k));
        px[i] = px[i + 1] = px[i + 2] = v;
    }
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

// One page of n receipts (or fewer on the last page)
function receiptPage(group, startNo, per, opts) {
    const { c, x } = newPage();
    const area = { w: PW - MARGIN * 2, h: PH - MARGIN * 2 - 30 };
    const g = bestGrid(per, group.map((e) => e.pic), area);
    group.forEach((e, k) => {
        const col = k % g.c, row = Math.floor(k / g.c);
        const cx = MARGIN + col * (g.cw + GAP), cy = MARGIN + row * (g.ch + GAP);
        const s = Math.min(g.cw / e.pic.width, g.ch / e.pic.height, 1.6);
        const w = Math.max(1, Math.round(e.pic.width * s)), h = Math.max(1, Math.round(e.pic.height * s));
        const dx = Math.round(cx + (g.cw - w) / 2), dy = Math.round(cy + (g.ch - h) / 2);
        x.imageSmoothingQuality = "high";
        x.drawImage(e.pic, dx, dy, w, h);
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
    const total = list.reduce((n, it) => n + amountOf(it.amount), 0);
    const hasAmount = list.some((it) => it.amount.trim());
    const rowH = 54, perPage = 22, out = [];
    for (let p = 0, first = true; p < list.length || first; p += perPage, first = false) {
        const { c, x } = newPage();
        let y = MARGIN + 30;
        if (first) {
            x.fillStyle = "#111"; x.textAlign = "left"; x.textBaseline = "alphabetic"; x.font = `bold 54px ${FONT}`;
            x.fillText(title, MARGIN, y + 40);
            y += 70;
            x.font = `28px ${FONT}`; x.fillStyle = "#444";
            if (who) { x.fillText(who, MARGIN, y + 28); y += 44; }
            x.fillText(SlimIO.t("{n} receipts", { n: list.length }) + (hasAmount ? " · " + SlimIO.t("Total") + " " + total.toLocaleString() : ""), MARGIN, y + 28);
            y += 70;
        } else y += 20;
        const cols = [MARGIN, MARGIN + 90, MARGIN + 330, PW - MARGIN];   // No | Date | Store | Amount (right edge)
        x.fillStyle = "#eee"; x.fillRect(MARGIN, y, PW - MARGIN * 2, rowH);
        x.fillStyle = "#111"; x.font = `bold 26px ${FONT}`; x.textBaseline = "middle";
        x.textAlign = "left";
        x.fillText("No.", cols[0] + 14, y + rowH / 2);
        x.fillText(SlimIO.t("Date"), cols[1], y + rowH / 2);
        x.fillText(SlimIO.t("Store / purpose"), cols[2], y + rowH / 2);
        x.textAlign = "right"; x.fillText(SlimIO.t("Amount"), cols[3] - 14, y + rowH / 2);
        y += rowH;
        x.font = `26px ${FONT}`;
        list.slice(p, p + perPage).forEach((it, k) => {
            x.fillStyle = "#222"; x.textAlign = "left";
            x.fillText(String(p + k + 1), cols[0] + 14, y + rowH / 2);
            x.fillText(it.date, cols[1], y + rowH / 2);
            let shop = it.shop;
            while (shop.length > 1 && x.measureText(shop).width > cols[3] - cols[2] - 230) shop = shop.slice(0, -1);
            x.fillText(shop === it.shop ? shop : shop + "…", cols[2], y + rowH / 2);
            x.textAlign = "right"; x.fillText(it.amount, cols[3] - 14, y + rowH / 2);
            y += rowH;
            x.strokeStyle = "#ddd"; x.lineWidth = 1.5;
            x.beginPath(); x.moveTo(MARGIN, y); x.lineTo(PW - MARGIN, y); x.stroke();
        });
        if (p + perPage >= list.length && hasAmount) {
            x.font = `bold 30px ${FONT}`; x.fillStyle = "#111"; x.textAlign = "left";
            x.fillText(SlimIO.t("Total"), cols[2], y + rowH / 2 + 6);
            x.textAlign = "right"; x.fillText(total.toLocaleString(), cols[3] - 14, y + rowH / 2 + 6);
        }
        out.push(c);
    }
    return out;
}

function toJpeg(canvas, scale, quality) {
    let src = canvas;
    if (scale < 1) {
        src = document.createElement("canvas");
        src.width = Math.round(canvas.width * scale); src.height = Math.round(canvas.height * scale);
        const x = src.getContext("2d");
        x.imageSmoothingQuality = "high";
        x.drawImage(canvas, 0, 0, src.width, src.height);
    }
    return new Promise((resolve, reject) => {
        src.toBlob(async (b) => {
            if (!b) return reject(new Error("toBlob failed"));
            try { resolve(new Uint8Array(await b.arrayBuffer())); } catch (e) { reject(e); }
        }, "image/jpeg", quality);
    });
}

async function build(pages, scale, quality) {
    const out = await PDFDocument.create();
    for (let i = 0; i < pages.length; i++) {
        const img = await out.embedJpg(await toJpeg(pages[i], scale, quality));
        out.addPage(A4).drawImage(img, { x: 0, y: 0, width: A4[0], height: A4[1] });
    }
    return out.save();
}

// Under a limit: quality goes down first, then the pixel size, until the whole PDF fits.
async function fitToLimit(pages, limit) {
    let smallest = null, step = 0;
    const tick = () => prog.set(Math.min(98, 40 + ++step * 3));
    const rungs = [];
    for (const scale of [1, 0.8, 0.64, 0.5, 0.4]) for (const q of [0.85, 0.7, 0.55, 0.4]) rungs.push([scale, q]);
    for (const [scale, q] of rungs) {
        const bytes = await build(pages, scale, q);
        tick();
        if (!smallest || bytes.length < smallest.bytes.length) smallest = { bytes, scale, q, fits: false };
        if (bytes.length <= limit) return { bytes, scale, q, fits: true };
    }
    return smallest;
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
    const entries = [];
    try {
        const check = await SlimIO.consume();
        if (check && !check.ok) { SlimIO.showError(SlimIO.t("Daily limit reached. Come back tomorrow.")); return; }

        for (let i = 0; i < items.length; i++) {
            const pic = await decode(items[i].file);
            if (!pic) { SlimIO.showError(SlimIO.t('Could not read "{name}".', { name: items[i].name })); return; }
            entries.push({ pic, it: items[i] });
            prog.set(Math.round(((i + 1) / items.length) * 30));
        }
        const per = Number($("per").value);
        const opts = { clear: $("clear").checked, number: $("number").checked };
        const pages = [];
        if (coverOn()) pages.push(...coverPages(items));
        const covers = pages.length;
        for (let i = 0; i < entries.length; i += per) {
            pages.push(receiptPage(entries.slice(i, i + per), i + 1, per, opts));
            prog.set(30 + Math.round(((i + per) / entries.length) * 10));
        }
        // "3 / 5" at the foot of every page
        pages.forEach((c, k) => footer(c.getContext("2d"), k + 1, pages.length));

        const r = limit ? await fitToLimit(pages, limit) : { bytes: await build(pages, 1, 0.9), fits: true, scale: 1, q: 0.9 };
        SlimIO.event("receipt-to-pdf-result", { target: limit ? limitLabel() : "none", fits: r.fits, receipts: items.length,
            per, cover: covers > 0, clear: opts.clear, outKB: Math.round(r.bytes.length / 1024) });
        showResult(pages.length, r, limit);
    } catch (e) {
        SlimIO.showError(SlimIO.t("Conversion failed: {msg}", { msg: e.message }));
    } finally {
        entries.forEach((e) => e.pic.close && e.pic.close());
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
