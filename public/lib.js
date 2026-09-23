// SlimIO shared helpers. Same-origin backend serves /api/* on the same host.
// Pages run purely in the browser (pdf.js + pdf-lib via CDN) — no server change.
const API_BASE = "";
const SERVER_BASE = "";

const SlimIO = (() => {
   const $ = (id) => document.getElementById(id);

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
            if (el) el.textContent = "Limit service currently unavailable.";
         });
   }
   function updateLimit(remaining, limit) {
      const el = $("limit");
      if (el) el.textContent = `Operations left today: ${remaining} / ${limit}`;
      const go = $("go");
      if (go && remaining === 0) go.disabled = true;
   }
   async function consume() {
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

   window.addEventListener("error", (e) => log("JS ERROR: " + e.message));
   window.addEventListener("unhandledrejection", (e) =>
      log("REJECTION: " + ((e.reason && e.reason.message) || e.reason)));

   return {
      $, formatSize, base64ToBytes, toBlob, download,
      showError, clearError, log,
      refreshStatus, updateLimit, consume, bindProgress,
   };
})();
