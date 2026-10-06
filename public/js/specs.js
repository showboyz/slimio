// Read upload requirements pasted from an application form, e.g.
//   "dimensions of 50mm x 20mm or 140 x 60 pixels. size of the file should be between 30kb to 49kb"
//   "about 6.0 cm (width) x 2.0 cm (height) at a resolution of 300 dpi, 10 kb to 20 kb, jpeg"
// Returns { w, h, minKB, maxKB, format, notes[] } with whatever it found (fields may be missing).
window.SlimSpecs = (() => {
     const NUM = "(\\d+(?:\\.\\d+)?)";
     const KB = "\\s*(kb|k\\.b\\.|kilobytes?|mb)";
     const toKB = (n, unit) => (/^mb/i.test(unit) ? parseFloat(n) * 1000 : parseFloat(n));

     function sizes(text) {
             const t = text.toLowerCase().replace(/\s+/g, " ");
             let minKB = null, maxKB = null, m;
             // ranges: "between 10 kb and 20 kb", "10kb to 20kb", "10-20 kb", "10 to 20 kb", "from 20 to 50kb"
             const range = new RegExp(NUM + "(?:" + KB + ")?\\s*(?:-|–|~|to|and)\\s*" + NUM + KB);
             if ((m = t.match(range))) {
                     const unit2 = m[4], a = toKB(m[1], m[2] || unit2), b = toKB(m[3], unit2);
                     if (a < b) { minKB = a; maxKB = b; }
             }
             if (maxKB === null) {
                     const max = new RegExp("(?:not exceed(?:ing)?|not more than|no more than|less than|under|below|upto|up to|maximum(?: of)?|max\\.?|within|<=?)\\s*(?:size )?(?:of )?" + NUM + KB);
                     if ((m = t.match(max))) maxKB = toKB(m[1], m[2]);
             }
             if (minKB === null) {
                     const min = new RegExp("(?:at least|not less than|minimum(?: of)?|min\\.?|more than|above)\\s*(?:size )?(?:of )?" + NUM + KB);
                     if ((m = t.match(min))) minKB = toKB(m[1], m[2]);
             }
             if (maxKB === null && minKB === null && (m = t.match(new RegExp("\\b" + NUM + KB)))) maxKB = toKB(m[1], m[2]);   // "make it 20 kb"
             return { minKB, maxKB };
     }

     function dims(text) {
             const t = text.toLowerCase().replace(/\s+/g, " ").replace(/\((?:width|w|height|h)\)/g, "");
             const notes = [];
             const dpiM = t.match(/(\d{2,4})\s*(?:dpi|ppi|pixels? per inch)/);
             const dpi = dpiM ? parseInt(dpiM[1], 10) : null;
             // every "A x B unit" pair (also "A unit x B unit")
             const pairs = [];
             const re = /(\d+(?:\.\d+)?)\s*(px|pixels?|cm|mm|in(?:ch(?:es)?)?)?\s*[x×*]\s*(\d+(?:\.\d+)?)\s*(px|pixels?|cm|mm|in(?:ch(?:es)?)?)?/g;
             let m;
             while ((m = re.exec(t))) {
                     const unit = (m[4] || m[2] || "").replace(/s$/, "");
                     const before = t.slice(Math.max(0, m.index - 30), m.index);
                     pairs.push({ a: parseFloat(m[1]), b: parseFloat(m[3]), unit: unit || "px",
                             role: /max/.test(before) ? "max" : /min/.test(before) ? "min" : "" });
             }
             // "width 140px, height 110px" / "width: 140 pixels and height: 110 pixels"
             const w1 = t.match(/width\s*(?:of|:|=|-)?\s*(\d+(?:\.\d+)?)\s*(px|pixels?|cm|mm)?/);
             const h1 = t.match(/height\s*(?:of|:|=|-)?\s*(\d+(?:\.\d+)?)\s*(px|pixels?|cm|mm)?/);
             if (w1 && h1) pairs.push({ a: parseFloat(w1[1]), b: parseFloat(h1[1]), unit: (w1[2] || h1[2] || "px").replace(/s$/, ""), role: "" });

             const toPx = (v, unit) => {
                     if (unit === "px" || unit === "pixel") return Math.round(v);
                     const inches = unit === "cm" ? v / 2.54 : unit === "mm" ? v / 25.4 : v;
                     return Math.round(inches * (dpi || 200));
             };
             const px = pairs.filter((p) => p.unit === "px" || p.unit === "pixel");
             let pick = null;
             if (px.length) {
                     // a min/max pair ("minimum 250 x 80 and maximum 580 x 180"): use the max, it fits both
                     pick = px.find((p) => p.role === "max") || px[0];
             } else if (pairs.length) {
                     pick = pairs[0];
                     if (!dpi) notes.push("no-dpi");
             }
             if (!pick) return { notes };
             const w = toPx(pick.a, pick.unit), h = toPx(pick.b, pick.unit);
             if (w < 16 || h < 16 || w > 4000 || h > 4000) return { notes };
             return { w, h, dpi, fromUnit: pick.unit, notes };
     }

     function parse(text) {
             if (!text || !text.trim()) return null;
             const s = sizes(text), d = dims(text);
             const t = text.toLowerCase();
             const format = /\bpng\b/.test(t) && !/\bjpe?g\b/.test(t) ? "png" : /\bjpe?g\b/.test(t) ? "jpeg" : null;
             return { ...s, w: d.w || null, h: d.h || null, dpi: d.dpi || null, fromUnit: d.fromUnit || null, format, notes: d.notes || [] };
     }

     return { parse };
})();
