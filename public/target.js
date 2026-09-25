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

   function parseSize(s) {
      const m = String(s).match(/^(\d+(?:\.\d+)?)\s*(kb|mb)$/i);
      if (!m) return null;
      return Math.round(parseFloat(m[1]) * (m[2].toLowerCase() === "mb" ? 1024 * 1024 : 1024));
   }

   function toolName() {
      return location.pathname.replace(/^\/|\.html$/g, "") || "compress";
   }

   async function viaServer(file, target) {
      const level = target >= 1024 * 1024 ? "ebook" : "screen";
      const resp = await fetch(`${SERVER_BASE}/api/compress`, {
         method: "POST",
         headers: { "X-Level": level },
         body: await file.arrayBuffer(),
      });
      const j = await resp.json().catch(() => ({}));
      if (resp.status === 429) return { limited: true };
      if (j.remaining !== undefined) SlimIO.updateLimit(j.remaining, j.limit);
      if (!j.ok) return { failed: true };
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
      let smallest = null;
      for (let si = 0; si < LADDER.length; si++) {
         const [scale, floor] = LADDER[si];
         const qualities = QUALITIES.filter((q) => q >= floor);
         const last = si === LADDER.length - 1;
         const perQ = qualities.map(() => []);
         for (let p = 1; p <= n; p++) {
            const page = await src.getPage(p);
            const base = page.getViewport({ scale: 1 });
            sizes[p - 1] = { w: base.width, h: base.height };
            const vp = page.getViewport({ scale });
            const canvas = document.createElement("canvas");
            canvas.width = Math.max(1, Math.ceil(vp.width));
            canvas.height = Math.max(1, Math.ceil(vp.height));
            const ctx = canvas.getContext("2d");
            ctx.fillStyle = "#fff";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            await page.render({ canvasContext: ctx, viewport: vp }).promise;
            for (let qi = 0; qi < qualities.length; qi++) perQ[qi].push(await jpeg(canvas, qualities[qi]));
            canvas.width = canvas.height = 0;   // free memory early
            onProgress && onProgress((si + p / n) / LADDER.length);
         }
         for (let qi = 0; qi < qualities.length; qi++) {
            const est = perQ[qi].reduce((a, b) => a + b.length, 0) + 600 * n + 1024;
            if (est > target * 1.02 && !(last && qi === qualities.length - 1)) continue;
            const bytes = await buildPdf(sizes, perQ[qi]);
            const res = { bytes, scale, quality: qualities[qi] };
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
         SlimIO.track(toolName());
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
               if (best.fits) { SlimIO.track(toolName()); return best; }
            }
         } catch (e) { /* network: fall through to browser */ }
      }
      if (charged) SlimIO.track(toolName());
      else {
         const c = await SlimIO.consume();
         if (c && !c.ok) return { limited: true };
      }

      onStatus && onStatus(SlimIO.t("Converting pages to images to reach the target…"));
      const r = await viaRaster(data, target, onProgress);
      const raster = { bytes: r.bytes, method: "raster", fits: r.fits, scale: r.scale, quality: r.quality };
      if (!best || raster.fits || raster.bytes.length < best.bytes.length) best = raster;
      return best;
   }

   return { run, parseSize };
})();
