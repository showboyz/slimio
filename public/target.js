// Compress a PDF to fit under a target size.
// 1) Ghostscript on the server (text stays sharp and selectable).
// 2) If still too big, rasterize in the browser, stepping resolution/quality
//    down until it fits, keeping the best quality that does.
// Needs pdf.js + pdf-lib + lib.js loaded first.
const SlimTarget = (() => {
   // Resolutions tried from sharpest down (scale is x 72dpi). At each one we take
   // the highest JPEG quality that fits, but not below that scale's floor — below
   // it a smaller resolution at better quality looks cleaner than blocky JPEG.
   const LADDER = [[1.5, 0.6], [1.25, 0.5], [1.0, 0.38], [0.85, 0.3], [0.7, 0.25], [0.55, 0.22], [0.45, 0.2], [0.35, 0.2]];
   const QUALITIES = [0.85, 0.75, 0.65, 0.57, 0.5, 0.44, 0.38, 0.33, 0.28, 0.25, 0.22, 0.2];
   const SERVER_MAX = 50 * 1024 * 1024;

   // Decimal (1KB = 1000 bytes) so the file passes whichever definition an upload form checks against.
   function parseSize(s) {
      const m = String(s).match(/^(\d+(?:\.\d+)?)\s*(kb|mb)$/i);
      if (!m) return null;
      return Math.round(parseFloat(m[1]) * (m[2].toLowerCase() === "mb" ? 1e6 : 1e3));
   }

   async function viaServer(file, target) {
      const level = target >= 1e6 ? "ebook" : "screen";
      const resp = await fetch(`${SERVER_BASE}/api/compress`, {
         method: "POST",
         // X-Target lets the server keep as much detail as the limit has room for
         headers: SlimIO.apiHeaders({ "X-Level": level, "X-Target": String(target) }),
         body: await file.arrayBuffer(),
      });
      const j = await resp.json().catch(() => ({}));
      if (resp.status === 429) return { limited: true };
      if (j.remaining !== undefined) SlimIO.updateLimit(j.remaining, j.limit);
      if (j.code === "password") throw new Error("password");   // the browser can't open it either
      if (!j.ok) {
         SlimIO.reportError("fallback", "HTTP " + resp.status + " " + (j.error || ""));
         return { failed: true };
      }
      return { bytes: SlimIO.base64ToBytes(j.pdf) };
   }

   function jpeg(canvas, q) {
      return new Promise((resolve, reject) =>
         canvas.toBlob(async (b) => {
            if (!b) return reject(new Error("toBlob failed"));
            resolve(new Uint8Array(await b.arrayBuffer()));
         }, "image/jpeg", q));
   }

   async function buildPdf(sizes, jpgs) {
      const out = await PDFLib.PDFDocument.create();
      for (let i = 0; i < jpgs.length; i++) {
         const img = await out.embedJpg(jpgs[i]);
         const page = out.addPage([sizes[i].w, sizes[i].h]);   // keep original paper size
         page.drawImage(img, { x: 0, y: 0, width: sizes[i].w, height: sizes[i].h });
      }
      return out.save({ useObjectStreams: true });
   }

   // Returns { bytes, scale, quality } for the best-looking raster that fits,
   // or the smallest one produced if nothing fits.
   async function viaRaster(data, target, onProgress) {
      const src = await pdfjsLib.getDocument({ data }).promise;
      const n = src.numPages;
      const sizes = [];
      // Photo PDFs (our JPG→PDF, many scan apps) have pages as big as the photo in points
      // (3024×4032 pt = 42×56 in): the ladder's scales would upscale them (×1.5 → 4536 px).
      // Such pages are drawn as if their long side were A3's 1190 pt, never above 1 px per pt,
      // and get two sharper steps first (3570 and 2678 px on the long side) so a 2MB target
      // keeps more of the photo than a 500KB one.
      const fits = [];
      for (let p = 1; p <= n; p++) {
         const base = (await src.getPage(p)).getViewport({ scale: 1 });
         sizes[p - 1] = { w: base.width, h: base.height };
         fits[p - 1] = Math.min(1, 1190 / Math.max(base.width, base.height));
      }
      const minFit = Math.min(...fits);
      const ladder = minFit < 1 ? [[3, 0.6], [2.25, 0.6], ...LADDER] : LADDER;
      let smallest = null;
      for (let si = 0; si < ladder.length; si++) {
         const [scale, floor] = ladder[si];
         const qualities = QUALITIES.filter((q) => q >= floor);
         const last = si === ladder.length - 1;
         const perQ = qualities.map(() => []);
         let px = 0;
         for (let p = 1; p <= n; p++) {
            const page = await src.getPage(p);
            const fit = fits[p - 1];
            const vp = page.getViewport({ scale: fit < 1 ? Math.min(scale * fit, 1) : scale });
            px = Math.max(px, Math.ceil(Math.max(vp.width, vp.height)));
            const canvas = document.createElement("canvas");
            canvas.width = Math.max(1, Math.ceil(vp.width));
            canvas.height = Math.max(1, Math.ceil(vp.height));
            const ctx = canvas.getContext("2d");
            ctx.fillStyle = "#fff";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            await page.render({ canvasContext: ctx, viewport: vp }).promise;
            for (let qi = 0; qi < qualities.length; qi++) perQ[qi].push(await jpeg(canvas, qualities[qi]));
            canvas.width = canvas.height = 0;   // free memory early
            onProgress && onProgress((si + p / n) / ladder.length);
         }
         for (let qi = 0; qi < qualities.length; qi++) {
            const est = perQ[qi].reduce((a, b) => a + b.length, 0) + 600 * n + 1024;
            if (est > target * 1.02 && !(last && qi === qualities.length - 1)) continue;
            const bytes = await buildPdf(sizes, perQ[qi]);
            const res = { bytes, scale, quality: qualities[qi], fit: minFit, px };
            if (!smallest || bytes.length < smallest.bytes.length) smallest = res;
            if (bytes.length <= target) return { ...res, fits: true };
         }
      }
      return { ...smallest, fits: false };
   }

   // Main entry. Returns { bytes, method, fits, note } or { limited } / throws.
   async function run(file, target, onProgress, onStatus) {
      const data = new Uint8Array(await file.arrayBuffer());
      if (file.size <= target) {
         SlimIO.track();
         return { bytes: data, method: "original", fits: true };
      }

      let best = null;
      let charged = false;
      if (file.size <= SERVER_MAX) {
         onStatus && onStatus(SlimIO.t("Compressing with Ghostscript…"));
         try {
            const r = await viaServer(file, target);
            if (r.limited) return { limited: true };
            charged = !r.failed;   // server counted this use
            if (r.bytes) {
               best = { bytes: r.bytes, method: "server", fits: r.bytes.length <= target };
               if (best.fits) { SlimIO.track(); return best; }
            }
         } catch (e) {
            if (e.message === "password") throw e;
            SlimIO.reportError("fallback", "network: " + e.message);   // fall through to browser
         }
      }
      if (charged) SlimIO.track();   // server path counted the use but the result didn't fit
      else {
         const c = await SlimIO.consume();
         if (c && !c.ok) return { limited: true };
      }

      onStatus && onStatus(SlimIO.t("Converting pages to images to reach the target…"));
      const r = await viaRaster(data, target, onProgress);
      const raster = { bytes: r.bytes, method: "raster", fits: r.fits, scale: r.scale, quality: r.quality, fit: r.fit, px: r.px };
      if (!best || raster.fits || raster.bytes.length < best.bytes.length) best = raster;
      return best;
   }

   return { run, parseSize };
})();
