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
      trackDownload();
      const url = URL.createObjectURL(toBlob(bytes, type || "application/pdf"));
      const a = document.createElement("a");
      a.href = url;
      a.download = name;
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 4000);
   }

   // PDF tools take only PDFs. Some apps hand over a PDF with no type, so a .pdf name counts too.
   function isPdf(f) {
      return !!f && (f.type === "application/pdf"
         || ((!f.type || f.type === "application/octet-stream") && /\.pdf$/i.test(f.name)));
   }
   // Not a PDF: say so. People do drop photos on "compress PDF to 300KB", so a picture also
   // gets a link to the tool that takes pictures.
   function notPdf(f, msg) {
      const pic = f && (/^image\//.test(f.type) || /\.(jpe?g|png|webp|heic|heif|gif|bmp|avif)$/i.test(f.name));
      if (!pic) return showError(msg || t("Please choose a PDF file."));
      const shrink = /compress/.test(toolName());
      const m = location.pathname.match(/compress-pdf-to-(\d+)(kb|mb)/i);
      const target = m ? m[1] + m[2].toUpperCase() : "";
      showError(shrink ? t("This is a picture, not a PDF. Pictures are made smaller in the image compressor.")
         : t("This is a picture, not a PDF. To turn pictures into a PDF, use JPG to PDF."));
      const el = $("error");
      if (!el) return;
      const a = document.createElement("a");
      a.href = (lang === "ko" ? "/ko/" : "/") + (shrink ? "compress-image.html" + (target ? "?target=" + target : "") : "jpg-to-pdf.html");
      a.textContent = !shrink ? t("JPG to PDF →") : target ? t("Make the picture under {kb} →", { kb: target }) : t("Compress image →");
      el.append(" ", a);
   }

   // Issued certificates often come with an open password or with editing locked. pdf-lib won't
   // touch either ("is encrypted") and pdf.js asks for the password, so say it in plain words.
   function lockedPdf(e, name) {
      const m = String((e && e.message) || e || "");
      const msg = (e && e.name === "PasswordException") || /password/i.test(m)
         ? t("This PDF needs a password to open. Open it with the password, save a copy without one, and add that copy.")
         : /is encrypted/i.test(m)
         ? t("This PDF is locked (a password or an editing lock), so it can't be changed here. Submit it as it is, or get a copy without the lock.")
         : "";
      return msg && name ? `“${name}”: ${msg}` : msg;
   }
   function pdfError(key, e, vars) {
      return lockedPdf(e, vars && vars.name) || t(key, { ...vars, msg: e.message });
   }

   function showError(msg, id) {
      const el = $(id || "error");
      if (!el) return;
      el.textContent = msg;
      el.style.display = "block";
      log(msg);
      reportError("shown", msg);
   }
   function clearError(id) {
      const el = $(id || "error");
      if (el) el.style.display = "none";
   }

   // The #log panel is for debugging only: open any page with ?debug to show it.
   const debug = /[?&]debug\b/.test(location.search);
   function log(msg) {
      const el = $("log");
      if (!el) return;
      if (debug) el.style.display = "block";
      el.textContent += msg + "\n";
      el.scrollTop = el.scrollHeight;
   }

   // Free daily uses are counted per browser: a random ID kept in localStorage and sent with
   // every API call (the server also caps uses per IP). No ID if storage is off — the server
   // then counts by IP.
   function deviceId() {
      try {
         let d = localStorage.getItem("slimio.device");
         if (!/^[a-z0-9]{16,40}$/i.test(d || "")) {
            d = window.crypto && crypto.randomUUID ? crypto.randomUUID().replace(/-/g, "")
               : Math.random().toString(36).slice(2) + Date.now().toString(36) + Math.random().toString(36).slice(2);
            localStorage.setItem("slimio.device", d);
         }
         return d;
      } catch (e) {
         return "";
      }
   }
   function apiHeaders(extra) {
      const d = deviceId();
      return Object.assign(d ? { "X-Device": d } : {}, extra);
   }

   function refreshStatus() {
      fetch(`${API_BASE}/api/check`, { headers: apiHeaders() })
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
   // Umami custom event: a tool was actually used, not just visited.
   // Visiting any page with ?notrack stops counting this browser (for the site owner).
   try { if (/[?&]notrack\b/.test(location.search)) localStorage.setItem("umami.disabled", "1"); } catch (e) {}
   function toolName() {
      const p = location.pathname.replace(/^\/|\.html$/g, "").replace(/\/$/, "");
      return !p ? "compress" : p === "ko" ? "ko/compress" : p;
   }
   // Any Umami event, tagged with the current tool (props may override it).
   function event(name, props) {
      try { window.umami && window.umami.track(name, Object.assign({ tool: toolName() }, props)); } catch (e) {}
   }
   // Umami "error" event, so we learn what goes wrong for real visitors. Never the file:
   // quoted parts of a message (file names) are dropped. At most 5 different errors per page view.
   // kind: "shown" (an error message the visitor saw), "fallback" (server compression failed and
   // the browser took over), "js" / "promise" (an uncaught script error).
   const reported = new Set();
   function reportError(kind, msg) {
      const m = String(msg || "").replace(/"[^"]*"|“[^”]*”/g, '"…"').replace(/\s+/g, " ").trim().slice(0, 140);
      if (!m || reported.has(kind + m) || reported.size >= 5) return;
      reported.add(kind + m);
      event("error", { kind, msg: m });
   }
   function track(tool) {
      event("tool-used", tool ? { tool } : null);
   }
   // The user actually took the result (not just ran the tool).
   function trackDownload() {
      event("downloaded", inApp ? { app: inApp } : null);
      const next = $("next");   // "Next, you might want to…" cards (tools/gen_related.py)
      if (next && next.hidden) next.hidden = false;
   }

   // Browsers inside apps (Naver, KakaoTalk, Instagram…). Android's in-app browsers often can't
   // save a file made in the page (a blob: URL), so the result box tells those visitors how to
   // reopen the page in a real browser.
   const ua = navigator.userAgent;
   const inApp = /NAVER\(inapp/i.test(ua) ? "naver" : /KAKAOTALK/i.test(ua) ? "kakaotalk" : /DaumApps/i.test(ua) ? "daum"
      : /Instagram/.test(ua) ? "instagram" : /FBAN|FBAV|FB_IAB/.test(ua) ? "facebook" : /\bLine\//.test(ua) ? "line"
      : /; wv\)/.test(ua) ? "webview" : "";
   const android = /Android/i.test(ua);

   // iPhone HEIC/HEIF photos. Safari opens them itself; Chrome, Edge and Firefox can't, so a
   // decoder (heic-to: about 650KB to download, 3MB unpacked) is fetched the first time one is needed.
   // Photos copied to a computer often have no image type at all, so they also go by name, and the
   // file dialog on computers is told to show them. Phones keep plain image/*: iPhones turn HEIC into
   // JPG themselves unless the list names HEIC, and Android shows its photo picker only for image types.
   function looksHeic(f) { return !!f && (/\.(heic|heif)$/i.test(f.name || "") || /^image\/hei[cf]/i.test(f.type)); }
   function isImage(f) { return !!f && (/^image\//.test(f.type) || looksHeic(f)); }
   const phone = /Android|iP(hone|ad|od)/.test(ua) || (/Mac/.test(navigator.platform) && navigator.maxTouchPoints > 1);
   function acceptHeic(input) {
      if (input && !phone && !/heic/.test(input.accept)) input.accept = (input.accept ? input.accept + "," : "") + ".heic,.heif";
   }
   const HEIC_LIB = "https://cdn.jsdelivr.net/npm/heic-to@1.5.2/dist/iife/heic-to.js";
   let heicLib = null;
   function loadHeic() {
      if (!heicLib) heicLib = new Promise((resolve, reject) => {
         const s = document.createElement("script");
         s.src = HEIC_LIB;
         s.onload = () => (window.HeicTo ? resolve(window.HeicTo) : reject(new Error("no decoder")));
         s.onerror = () => { heicLib = null; s.remove(); reject(new Error(t("The HEIC photo decoder could not be loaded. Check your connection and try again."))); };
         document.head.appendChild(s);
      });
      return heicLib;
   }
   // HEIF files say so in their first bytes: "ftyp" and a brand such as heic or mif1
   async function sniffHeic(file) {
      const s = String.fromCharCode(...new Uint8Array(await file.slice(0, 12).arrayBuffer()));
      return s.slice(4, 8) === "ftyp" && ["heic", "heix", "hevc", "hevx", "heim", "heis", "mif1", "msf1"].includes(s.slice(8, 12));
   }
   // Open a photo with its EXIF rotation applied, so phone photos stand the right way up. Returns an
   // ImageBitmap or <img> (release it with .close() when there is one), or null when the browser
   // can't open the file and it isn't HEIC. `busy` (an element) says "Opening HEIC photos…" while the
   // decoder works, and gets its text back when the last decode on it ends. A decoder that can't be
   // downloaded throws, so the page can say so.
   const busyText = new Map();
   async function openImage(file, busy) {
      try { if (window.createImageBitmap) return await createImageBitmap(file, { imageOrientation: "from-image" }); } catch (e) { /* <img> below */ }
      const url = URL.createObjectURL(file);
      try { const img = new Image(); img.src = url; await img.decode(); return img; } catch (e) { /* HEIC below */ } finally { URL.revokeObjectURL(url); }
      if (!looksHeic(file) && !(await sniffHeic(file).catch(() => false))) return null;
      if (busy) {
         if (!busyText.has(busy)) busyText.set(busy, { n: 0, text: busy.textContent });
         busyText.get(busy).n++;
         busy.textContent = t("Opening HEIC photos…");
      }
      try { return await (await loadHeic())({ blob: file, type: "bitmap" }); }
      catch (e) { if (e && e.message && heicLib === null) throw e; return null; }   // a failed download says so; a bad file is null
      finally {
         const b = busy && busyText.get(busy);
         if (b && --b.n === 0) { busy.textContent = b.text; busyText.delete(busy); }
      }
   }
   function inAppNote(box) {
      // The Naver app on iPhone saves files fine (checked 2026-10-12), so no note there.
      if (!inApp || (inApp === "naver" && !android) || box.querySelector(".inapp")) return;
      const here = location.href.replace(/#.*$/, "");
      const open = inApp === "kakaotalk" ? "kakaotalk://web/openExternal?url=" + encodeURIComponent(here)
         : android ? "intent://" + here.replace(/^https?:\/\//, "") + "#Intent;scheme=https;package=com.android.chrome;end"
         : "";
      const p = document.createElement("p");
      p.className = "inapp";
      p.textContent = open
         ? t("In-app browsers sometimes can't save files. If nothing downloads, open this page in a browser and run it again.")
         : t("In-app browsers sometimes can't save files. If nothing downloads, choose “Open in Safari” (or another browser) from the app's ⋯ menu and run it again.");
      if (open) {
         const a = document.createElement("a");
         a.href = open;
         a.textContent = inApp === "kakaotalk" ? t("Open in browser") : t("Open in Chrome");
         a.addEventListener("click", () => event("open-browser", { app: inApp }));
         p.append(" ", a);
      }
      box.appendChild(p);
   }

   // Show a finished result. On a phone the run button is often at the bottom of the screen, so
   // the result used to appear below it, off screen, and people tapped the button again. Scroll
   // it into view, and flash it so a second run visibly gives a new result.
   // { scroll: false }: a result remade while the visitor edits (the ID photo crop) stays put.
   function reveal(box, opts) {
      box = box || $("result");
      if (!box) return;
      inAppNote(box);
      const r = box.getBoundingClientRect();
      if ((!opts || opts.scroll !== false) && (r.top < 0 || r.bottom > innerHeight)) {
         const still = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
         box.scrollIntoView({ block: r.height < innerHeight - 40 ? "center" : "start", behavior: still ? "auto" : "smooth" });
      }
      box.classList.remove("flash");
      void box.offsetWidth;   // restart the animation
      box.classList.add("flash");
   }
   // Long-pressing a result picture to save it skips the download button: count it too.
   let held = false;
   document.addEventListener("contextmenu", (e) => {
      if (held || !e.target.closest || !e.target.closest(".result img")) return;
      held = true;
      event("held-image", inApp ? { app: inApp } : null);
   }, true);
   // Funnel step between "viewed" and "tool-used": the visitor gave the tool something to
   // work on (picked, dropped or drew). Sent once per page view.
   let added = false;
   function inputAdded(how) {
      if (added) return;
      added = true;
      event("file-added", { how });
   }
   document.addEventListener("change", (e) => {
      const t = e.target;
      if (t && t.type === "file" && t.files && t.files.length) inputAdded("pick");
   }, true);
   document.addEventListener("drop", (e) => {
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length) inputAdded("drop");
   }, true);

   async function consume() {
      track();
      try {
         const c = await fetch(`${API_BASE}/api/consume`, { method: "POST", headers: apiHeaders() }).then((r) => r.json());
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

   window.addEventListener("error", (e) => {
      log("JS ERROR: " + e.message);
      const src = e.filename || "";
      if (src && !src.startsWith(location.origin) && !/cdnjs|jsdelivr|unpkg/.test(src)) return;   // browser extensions
      if (/ResizeObserver loop/.test(e.message)) return;   // harmless browser notice
      reportError("js", e.message + (src ? " @" + src.split("/").pop().split("?")[0] + ":" + e.lineno : ""));
   });
   window.addEventListener("unhandledrejection", (e) => {
      const m = (e.reason && e.reason.message) || e.reason;
      log("REJECTION: " + m);
      reportError("promise", m);
   });

   return {
      $, t, pages, lang, debug, formatSize, base64ToBytes, toBlob, download,
      showError, clearError, log, isPdf, notPdf, lockedPdf, pdfError,
      refreshStatus, updateLimit, consume, bindProgress, track, event, reportError, trackDownload, inputAdded, apiHeaders, page2user,
      reveal, inApp, isImage, looksHeic, acceptHeic, openImage,
   };
})();

// Phones have no drag and drop, so the drop areas say "tap" there instead of "drop here or click".
// The tools overwrite this text with the file name once a file is added.
(() => {
   if (!matchMedia("(pointer: coarse)").matches) return;
   const t = SlimIO.t;
   document.querySelectorAll(".drop").forEach((d) => {
      const input = d.querySelector("input[type=file]");
      const title = d.querySelector(".drop-title"), or = d.querySelector(".drop-or");
      if (!input || !title || !or) return;
      const pdf = input.accept.includes("pdf");
      const several = input.multiple && !input.accept.includes(",");   // merge, JPG→PDF
      title.textContent = pdf ? t(several ? "Tap to choose PDF files" : "Tap to choose a PDF") : t("Tap to choose photos");
      or.textContent = several ? t("You can pick several at once")
             : pdf ? t("Pick a file saved on your phone") : t("From your gallery or files");
   });
})();

// Tool pages call $("id") directly.
const $ = SlimIO.$;
