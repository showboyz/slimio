const http = require("http");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawn } = require("child_process");

const PORT = process.env.PORT || 3001;
const DAILY_LIMIT = parseInt(process.env.DAILY_LIMIT || "20", 10);

// naive per-IP daily counter
const usage = new Map();
function today() { return new Date().toISOString().slice(0, 10); }
function clientIp(req) {
   return (req.headers["x-forwarded-for"] || "").split(",")[0].trim() ||
       req.socket.remoteAddress || "unknown";
}
function consume(ip) {
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

const server = http.createServer(async (req, res) => {
   res.setHeader("Access-Control-Allow-Origin", "*");
   res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
   res.setHeader("Access-Control-Allow-Headers", "Content-Type");
   if (req.method === "OPTIONS") { res.writeHead(204); return res.end(); }

   const ip = clientIp(req);

   if (req.url === "/api/check" && req.method === "GET") {
       const left = remaining(ip);
       return sendJson(res, 200, { ok: left > 0, remaining: left, limit: DAILY_LIMIT });
   }

   if (req.url === "/api/compress" && req.method === "POST") {
       if (remaining(ip) <= 0) {
          return sendJson(res, 429, { error: "daily limit reached", limit: DAILY_LIMIT });
       }
       const level = (req.headers["x-level"] || "ebook").replace(/[^a-zA-Z]/g, "");
       const jpg = req.headers["x-jpg"] ? parseInt(req.headers["x-jpg"], 10) : undefined;
       consume(ip);

       const chunks = [];
       for await (const c of req) chunks.push(c);
       const inBuf = Buffer.concat(chunks);
       if (inBuf.length < 200) return sendJson(res, 400, { error: "empty file" });

       const tmpIn = path.join(os.tmpdir(), `trout_${Date.now()}.pdf`);
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

    sendJson(res, 404, { error: "not found" });
});

function sendJson(res, code, body) {
   const data = Buffer.from(JSON.stringify(body));
   res.writeHead(code, { "Content-Type": "application/json" });
   res.end(data);
}

server.listen(PORT, "127.0.0.1", () => {
   console.log(`Ghostscript compression server on http://127.0.0.1:${PORT}`);
   console.log(`daily limit: ${DAILY_LIMIT}`);
});
