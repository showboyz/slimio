import { json, getClientIp, todayKey } from "./lib.js";

const DAILY_TTL = 24 * 60 * 60;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const clientIp = getClientIp(request);
    const limit = parseInt(env.DAILY_LIMIT || "10", 10);
    const key = `rate:${clientIp}:${todayKey()}`;

    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
           "Access-Control-Allow-Origin": "*",
           "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
           "Access-Control-Allow-Headers": "Content-Type",
           "Access-Control-Max-Age": "86400",
       },
      });
    }

    if (url.pathname === "/api/consume" && request.method === "POST") {
      const current = await env.RATES.get(key, "json");
      const count = (current?.count || 0) + 1;
      await env.RATES.put(key, JSON.stringify({ count }), {
        expirationTtl: DAILY_TTL,
      });
      if (count > limit) {
        return json(429, { ok: false, remaining: 0, limit, used: count });
      }
      return json(200, { ok: true, remaining: limit - count, limit, used: count });
    }

    if (url.pathname === "/api/check") {
      const current = await env.RATES.get(key, "json");
      const used = current?.count || 0;
      const remaining = Math.max(0, limit - used);
      return json(200, { ok: remaining > 0, remaining, limit, used });
    }

    return json(404, { error: "not found" });
  },
};
