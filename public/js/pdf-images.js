// In-browser PDF compression that works like Ghostscript's image downsampling: find the
// image objects inside the PDF, shrink the oversized ones and re-encode them as JPEG.
// Text, fonts and vector graphics are left alone, so they stay sharp and selectable.
// Needs pdf-lib (window.PDFLib). Image kinds it doesn't understand are left as they are.
window.SlimImages = (() => {
     const { PDFDocument, PDFName, PDFRawStream, PDFNumber, PDFArray, PDFDict } = PDFLib;

     const name = (dict, key) => {
             const v = dict.get(PDFName.of(key));
             return v instanceof PDFName ? v.decodeText() : null;
     };
     const num = (dict, key) => {
             const v = dict.get(PDFName.of(key));
             return v instanceof PDFNumber ? v.asNumber() : null;
     };

     // Colour space as "rgb" | "gray" | null (unsupported: CMYK, Indexed, Lab, ...).
     function colorKind(doc, dict) {
             let cs = dict.get(PDFName.of("ColorSpace"));
             if (cs && !(cs instanceof PDFName) && !(cs instanceof PDFArray)) cs = doc.context.lookup(cs);
             if (cs instanceof PDFName) {
                     const n = cs.decodeText();
                     return n === "DeviceRGB" ? "rgb" : n === "DeviceGray" ? "gray" : null;
             }
             if (cs instanceof PDFArray && cs.size() === 2 && cs.get(0) instanceof PDFName && cs.get(0).decodeText() === "ICCBased") {
                     const icc = doc.context.lookup(cs.get(1));
                     const n = icc && icc.dict ? num(icc.dict, "N") : null;
                     return n === 3 ? "rgb" : n === 1 ? "gray" : null;
             }
             return null;
     }

     function singleFilter(dict) {
             const f = dict.get(PDFName.of("Filter"));
             if (f instanceof PDFName) return f.decodeText();
             if (f instanceof PDFArray && f.size() === 1 && f.get(0) instanceof PDFName) return f.get(0).decodeText();
             return f ? "multi" : "none";
     }

     async function inflate(bytes) {
             const ds = new DecompressionStream("deflate");
             const out = new Response(new Blob([bytes]).stream().pipeThrough(ds));
             return new Uint8Array(await out.arrayBuffer());
     }

     // Undo PNG row predictors (DecodeParms /Predictor >= 10), 8 bits per component.
     function unpredict(data, colors, columns) {
             const bpp = colors, rowLen = colors * columns, rows = Math.floor(data.length / (rowLen + 1));
             const out = new Uint8Array(rows * rowLen);
             for (let r = 0; r < rows; r++) {
                     const type = data[r * (rowLen + 1)], src = r * (rowLen + 1) + 1, dst = r * rowLen, prev = dst - rowLen;
                     for (let i = 0; i < rowLen; i++) {
                             const x = data[src + i], a = i >= bpp ? out[dst + i - bpp] : 0, b = r ? out[prev + i] : 0, c = r && i >= bpp ? out[prev + i - bpp] : 0;
                             let v;
                             if (type === 0) v = x;
                             else if (type === 1) v = x + a;
                             else if (type === 2) v = x + b;
                             else if (type === 3) v = x + ((a + b) >> 1);
                             else { const p = a + b - c, pa = Math.abs(p - a), pb = Math.abs(p - b), pc = Math.abs(p - c); v = x + (pa <= pb && pa <= pc ? a : pb <= pc ? b : c); }
                             out[dst + i] = v & 255;
                     }
             }
             return out;
     }

     // Decode one image stream into something drawable, or null if we can't.
     async function decode(doc, stream) {
             const d = stream.dict, filter = singleFilter(d);
             const w = num(d, "Width"), h = num(d, "Height"), bpc = num(d, "BitsPerComponent");
             if (!w || !h || d.get(PDFName.of("ImageMask")) || d.get(PDFName.of("Decode"))) return null;
             const kind = colorKind(doc, d);
             if (!kind) return null;
             if (filter === "DCTDecode") {
                     try { return { img: await createImageBitmap(new Blob([stream.contents], { type: "image/jpeg" })), w, h, kind }; }
                     catch (e) { return null; }
             }
             if ((filter === "FlateDecode" || filter === "none") && bpc === 8) {
                     let px = filter === "none" ? stream.contents : await inflate(stream.contents);
                     const parms = d.get(PDFName.of("DecodeParms"));
                     const pd = parms instanceof PDFDict ? parms : parms ? doc.context.lookup(parms) : null;
                     const pred = pd instanceof PDFDict ? num(pd, "Predictor") : null;
                     const colors = kind === "rgb" ? 3 : 1;
                     if (pred && pred >= 10) px = unpredict(px, colors, w);
                     else if (pred && pred !== 1) return null;   // TIFF predictor: rare, skip
                     if (px.length < w * h * colors) return null;
                     const rgba = new Uint8ClampedArray(w * h * 4);
                     for (let i = 0, j = 0; i < w * h; i++, j += colors) {
                             rgba[i * 4] = px[j];
                             rgba[i * 4 + 1] = px[colors === 3 ? j + 1 : j];
                             rgba[i * 4 + 2] = px[colors === 3 ? j + 2 : j];
                             rgba[i * 4 + 3] = 255;
                     }
                     return { img: await createImageBitmap(new ImageData(rgba, w, h)), w, h, kind };
             }
             return null;
     }

     function jpeg(canvas, quality) {
             return new Promise((res, rej) => canvas.toBlob((b) => (b ? res(b) : rej(new Error("encode failed"))), "image/jpeg", quality));
     }

     // Largest pixel size an image needs: the biggest page side at the target dpi.
     function pixelCap(doc, dpi) {
             let maxPt = 0;
             for (const p of doc.getPages()) { const { width, height } = p.getSize(); maxPt = Math.max(maxPt, width, height); }
             return Math.round(((maxPt || 842) / 72) * dpi);
     }

     async function compress(input, { dpi = 150, quality = 0.75, onProgress } = {}) {
             const doc = await PDFDocument.load(input, { updateMetadata: false });
             const cap = pixelCap(doc, dpi);
             const images = [];
             for (const [ref, obj] of doc.context.enumerateIndirectObjects()) {
                     if (obj instanceof PDFRawStream && name(obj.dict, "Subtype") === "Image") images.push([ref, obj]);
             }
             let replaced = 0, skipped = 0, saved = 0;
             for (let i = 0; i < images.length; i++) {
                     const [ref, stream] = images[i];
                     onProgress && onProgress((i + 1) / images.length);
                     const src = await decode(doc, stream);
                     if (!src) { skipped++; continue; }
                     const s = Math.min(1, cap / Math.max(src.w, src.h));
                     const w = Math.max(1, Math.round(src.w * s)), h = Math.max(1, Math.round(src.h * s));
                     const c = document.createElement("canvas");
                     c.width = w; c.height = h;
                     const ctx = c.getContext("2d");
                     ctx.imageSmoothingQuality = "high";
                     ctx.drawImage(src.img, 0, 0, w, h);
                     src.img.close && src.img.close();
                     const out = new Uint8Array(await (await jpeg(c, quality)).arrayBuffer());
                     if (out.length >= stream.contents.length * 0.9) { skipped++; continue; }   // not worth it
                     const dict = { Type: "XObject", Subtype: "Image", Width: w, Height: h, BitsPerComponent: 8,
                             ColorSpace: "DeviceRGB", Filter: "DCTDecode", Length: out.length };
                     for (const k of ["SMask", "Intent", "Interpolate"]) {
                             const v = stream.dict.get(PDFName.of(k));
                             if (v) dict[k] = v;
                     }
                     doc.context.assign(ref, doc.context.stream(out, dict));
                     saved += stream.contents.length - out.length;
                     replaced++;
             }
             const bytes = await doc.save({ useObjectStreams: true });
             return { bytes, images: images.length, replaced, skipped, saved };
     }

     return { compress };
})();
