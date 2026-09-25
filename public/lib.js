// SlimIO shared helpers. Same-origin backend serves /api/* on the same host.
// Pages run purely in the browser (pdf.js + pdf-lib via CDN) — no server change.
const API_BASE = "";
const SERVER_BASE = "";

const SlimIO = (() => {
   const $ = (id) => document.getElementById(id);

   // UI strings: the English text is the key. Korean pages load /i18n/ko.js
   // (window.SLIMIO_KO) before this file; English pages just get the key back.
   const lang = (document.documentElement.lang || "en").slice(0, 2);
   const dict = (lang === "ko" && window.SLIMIO_KO) || {};
   function t(s, vars) {
      const out = dict[s] || s;
      return vars ? out.replace(/\{(\w+)\}/g, (m, k) => (k in vars ? vars[k] : m)) : out;
   }
   function pages(n) {
      return lang === "ko" ? `${n}페이지` : `${n} page${n === 1 ? "" : "s"}`;
   }

   function formatSize(n) {
      if (n < 1024) return `${n} B`;
      if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
      return `${(n / 1024 / 1024).toFixed(2)} MB`;
   }

   function base64ToBytes(b64) {
      const bin = atob(b64);
      const out = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
      return out;
   }

   function toBlob(bytes, type) {
      return new Blob([bytes], { type });
   }

   function download(bytes, name, type) {
      const url = URL.createObjectURL(toBlob(bytes, type || "application/pdf"));
      const a = document.createElement("a");
      a.href = url;
      a.download = name;
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 4000);
   }

   function showError(msg, id) {
      const el = $(id || "error");
      if (!el) return;
      el.textContent = msg;
      el.style.display = "block";
      log(msg);
   }
   function clearError(id) {
      const el = $(id || "error");
      if (el) el.style.display = "none";
   }

   function log(msg) {
      const el = $("log");
      if (!el) return;
      el.style.display = "block";
      el.textContent += msg + "\n";
      el.scrollTop = el.scrollHeight;
   }

   // per-IP daily limit, reused from the rate-limit backend
   function refreshStatus() {
      fetch(`${API_BASE}/api/check`)
         .then((r) => r.json())
         .then((c) => updateLimit(c.remaining, c.limit))
         .catch(() => {
            const el = $("limit");
            if (el) el.textContent = t("Limit service currently unavailable.");
         });
   }
   function updateLimit(remaining, limit) {
      const el = $("limit");
      if (el) el.textContent = t("Operations left today: {remaining} / {limit}", { remaining, limit });
      const go = $("go");
      if (go && remaining === 0) go.disabled = true;
   }
   // Plausible custom event: which tool actually gets used (not just visited)
   function track(tool) {
      try { window.plausible && window.plausible("Tool Used", { props: { tool } }); } catch (e) {}
   }
   function toolName() {
      return location.pathname.replace(/^\/|\.html$/g, "") || "compress";
   }

   async function consume() {
      track(toolName());
      try {
         const c = await fetch(`${API_BASE}/api/consume`, { method: "POST" }).then((r) => r.json());
         updateLimit(c.remaining, c.limit);
         return c;
      } catch (e) {
         return null;
      }
   }

   function bindProgress(barId) {
      const bar = $(barId || "prog");
      const wrap = bar && bar.parentElement;
      return {
         bar,
         show() { if (wrap) wrap.style.display = "block"; },
         set(pct) { if (bar) bar.style.width = Math.round(pct) + "%"; },
         hide() { if (wrap) wrap.style.display = "none"; },
      };
   }

   // Map a point in the page's *visual* space (as the reader sees it, after /Rotate)
   // to pdf-lib user space. Returns {x, y, angle}: angle is added to the visual text angle.
   function page2user(page) {
      const box = page.getCropBox();
      const r = ((page.getRotation().angle % 360) + 360) % 360;
      const W = box.width, H = box.height;
      const vw = r % 180 ? H : W, vh = r % 180 ? W : H;
      function map(vx, vy) {
         let x, y;
         if (r === 90) { x = W - vy; y = vx; }
         else if (r === 180) { x = W - vx; y = H - vy; }
         else if (r === 270) { x = vy; y = H - vx; }
         else { x = vx; y = vy; }
         return { x: x + box.x, y: y + box.y, angle: r };
      }
      return { width: vw, height: vh, map };
   }

   window.addEventListener("error", (e) => log("JS ERROR: " + e.message));
   window.addEventListener("unhandledrejection", (e) =>
      log("REJECTION: " + ((e.reason && e.reason.message) || e.reason)));

   return {
      $, t, pages, lang, formatSize, base64ToBytes, toBlob, download,
      showError, clearError, log,
      refreshStatus, updateLimit, consume, bindProgress, track, page2user,
   };
})();

// Tool pages call $("id") directly.
const $ = SlimIO.$;
