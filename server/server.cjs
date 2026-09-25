const http = require("http");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawn } = require("child_process");

const PORT = process.env.PORT || 3001;
const HOST = process.env.HOST || "0.0.0.0";
const DAILY_LIMIT = parseInt(process.env.DAILY_LIMIT || "20", 10);
const PUBLIC_DIR = process.env.PUBLIC_DIR || path.join(__dirname, "..", "public");
const MAX_UPLOAD = 50 * 1024 * 1024; // 256MB machine: cap uploads so one request can't OOM it
const LEVELS = new Set(["screen", "ebook", "printer", "prepress"]);

const MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css",
    ".js": "application/javascript",
    ".json": "application/json",
    ".xml": "application/xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".txt": "text/plain; charset=utf-8",
    ".webp": "image/webp",
    ".ico": "image/x-icon",
};

// naive per-IP daily counter
const usage = new Map();
function today() { return new Date().toISOString().slice(0, 10); }
function clientIp(req) {
   return (req.headers["x-forwarded-for"] || "").split(",")[0].trim() ||
       req.socket.remoteAddress || "unknown";
}
let usageDay = today();
function consume(ip) {
   if (usageDay !== today()) { usage.clear(); usageDay = today(); } // drop yesterday's counters
   const key = ip + ":" + today();
   const n = (usage.get(key) || 0) + 1;
   usage.set(key, n);
   return n;
}
function remaining(ip) {
   const key = ip + ":" + today();
   return Math.max(0, DAILY_LIMIT - (usage.get(key) || 0));
}

function gs(args, input, output) {
   return new Promise((resolve, reject) => {
       const gsArgs = [
          "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite",
          "-dPDFSETTINGS=/" + args.level,
          "-sOutputFile=" + output,
          input,
       ];
       if (args.jpg !== undefined) {
          gsArgs.push("-dDownsampleColorImages=true");
          gsArgs.push("-dColorImageResolution=" + (args.jpg || 150));
          gsArgs.push("-dAutoRotatePages=/None");
       }
       try {
          const proc = spawn("gs", gsArgs, { stdio: ["ignore", "pipe", "pipe"] });
          let err = "";
          proc.stderr.on("data", (d) => (err += d));
          proc.on("close", (code) => code === 0 ? resolve() : reject(new Error(err || "gs exit " + code)));
          proc.on("error", reject);
       } catch (e) { reject(e); }
   });
}

async function handle(req, res) {
   res.setHeader("Access-Control-Allow-Origin", "*");
   res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
   res.setHeader("Access-Control-Allow-Headers", "Content-Type");
   if (req.method === "OPTIONS") { res.writeHead(204); return res.end(); }

   const ip = clientIp(req);

     if (req.url === "/api/check" && req.method === "GET") {
        const left = remaining(ip);
        return sendJson(res, 200, { ok: left > 0, remaining: left, limit: DAILY_LIMIT });
     }

     if (req.url === "/api/consume" && req.method === "POST") {
        const allowed = remaining(ip) > 0;   // decide before counting, so the last use is allowed
        if (allowed) consume(ip);
        return sendJson(res, 200, { ok: allowed, remaining: remaining(ip), limit: DAILY_LIMIT });
     }

   if (req.url === "/api/compress" && req.method === "POST") {
       if (remaining(ip) <= 0) {
          return sendJson(res, 429, { error: "daily limit reached", limit: DAILY_LIMIT });
       }
       if (parseInt(req.headers["content-length"] || "0", 10) > MAX_UPLOAD) {
          return sendJson(res, 413, { error: "file too large (max 50 MB)" });
       }
       const level = LEVELS.has(req.headers["x-level"]) ? req.headers["x-level"] : "ebook";
       const jpg = req.headers["x-jpg"] ? parseInt(req.headers["x-jpg"], 10) : undefined;

       const chunks = [];
       let size = 0;
       for await (const c of req) {
          size += c.length;
          if (size > MAX_UPLOAD) return sendJson(res, 413, { error: "file too large (max 50 MB)" });
          chunks.push(c);
       }
       const inBuf = Buffer.concat(chunks);
       if (inBuf.length < 200) return sendJson(res, 400, { error: "empty file" });
       consume(ip);

       const tmpIn = path.join(os.tmpdir(), `trout_${Date.now()}_${Math.random().toString(36).slice(2)}.pdf`);
       const tmpOut = tmpIn + "_out.pdf";
       fs.writeFileSync(tmpIn, inBuf);

       try {
          await gs({ level, jpg }, tmpIn, tmpOut);
          const outBuf = fs.readFileSync(tmpOut);
          sendJson(
             res, 200,
             {
                ok: true,
                inBytes: inBuf.length,
                outBytes: outBuf.length,
                savedPct: ((1 - outBuf.length / inBuf.length) * 100).toFixed(1),
                remaining: remaining(ip),
                limit: DAILY_LIMIT,
                pdf: outBuf.toString("base64"),
             }
          );
        } catch (e) {
          sendJson(res, 500, { error: e.message, inBytes: inBuf.length, outBytes: 0, remaining: remaining(ip), limit: DAILY_LIMIT });
        } finally {
          fs.unlink(tmpIn, () => {});
          fs.unlink(tmpOut, () => {});
        }
       return;
     }

      // static file serving fallback: / -> index.html
     let urlPath;
     try {
         urlPath = decodeURIComponent(req.url.split("?")[0]);
     } catch (e) {
         sendJson(res, 400, { error: "bad request" }); // malformed %-escape; must not crash the process
         return;
     }
     const query = req.url.includes("?") ? req.url.slice(req.url.indexOf("?")) : "";
     if (urlPath === "/index.html") return redirect(res, "/" + query);   // one URL per page
     if (urlPath === "/") urlPath = "/index.html";
     const filePath = path.join(PUBLIC_DIR, path.normalize(urlPath).replace(/^(\.\.[/\\])+/, ""));

     if (!filePath.startsWith(PUBLIC_DIR)) {
         sendJson(res, 403, { error: "forbidden" });
         return;
     }

     fs.readFile(filePath, (err, data) => {
         if (err) {
             // /merge -> /merge.html (people type URLs without the extension)
             if (!path.extname(urlPath) && fs.existsSync(filePath.replace(/\/$/, "") + ".html")) {
                 return redirect(res, urlPath.replace(/\/$/, "") + ".html" + query);
             }
             fs.readFile(path.join(PUBLIC_DIR, "404.html"), (e2, page) => {
                 if (e2) return sendJson(res, 404, { error: "not found" });
                 res.writeHead(404, { "Content-Type": MIME[".html"] });
                 res.end(page);
             });
             return;
         }
         const ext = path.extname(filePath);
         const headers = { "Content-Type": MIME[ext] || "application/octet-stream" };
         if (/[?&]v=/.test(query)) headers["Cache-Control"] = "public, max-age=31536000, immutable";   // content-hashed
         else if ([".png", ".jpg", ".svg", ".webp", ".ico"].includes(ext)) headers["Cache-Control"] = "public, max-age=86400";
         res.writeHead(200, headers);
         res.end(data);
     });
}

const server = http.createServer((req, res) => {
   handle(req, res).catch((e) => {
       console.error("request failed:", req.method, req.url, e);
       if (!res.headersSent) sendJson(res, 500, { error: "server error" });
       else res.destroy();
   });
});

function redirect(res, location) {
   res.writeHead(301, { Location: location });
   res.end();
}

function sendJson(res, code, body) {
   const data = Buffer.from(JSON.stringify(body));
   res.writeHead(code, { "Content-Type": "application/json" });
   res.end(data);
}

server.listen(PORT, HOST, () => {
    console.log(`Ghostscript compression server on http://${HOST}:${PORT}`);
    console.log(`daily limit: ${DAILY_LIMIT}`);
});
