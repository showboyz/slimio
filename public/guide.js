// Guide pages: keep the tool one tap away and measure how far people read.
// Readers who land from search on a long guide rarely scroll to the CTA box at the end, so a bar
// with the same button slides up once the button under the intro has scrolled away, and hides
// again when the end box comes into view. Clicks are counted by Umami's data-umami-event
// attributes (pos = top / sticky / bottom / body); this file sends `guide-read` at half and end.
(() => {
   try { if (/[?&]notrack\b/.test(location.search)) localStorage.setItem("umami.disabled", "1"); } catch (e) {}
   const guide = location.pathname.replace(/^\/(ko\/)?guides\/(.*)\.html$/, "$1$2");
   const top = document.querySelector(".cta-top"), end = document.querySelector(".cta-box"), bar = document.querySelector(".cta-sticky");
   let closed = false;
   try { closed = sessionStorage.getItem("slimio.ctaClosed") === "1"; } catch (e) {}
   const sent = {};
   const read = (depth) => {
      if (sent[depth]) return;
      sent[depth] = true;
      if (window.umami) window.umami.track("guide-read", { guide, depth });
   };
   let queued = false;
   function update() {
      queued = false;
      const h = innerHeight, y = scrollY;
      const endTop = end ? end.getBoundingClientRect().top : Infinity;
      if (y + h >= document.documentElement.scrollHeight / 2) read("half");
      if (endTop < h) read("end");
      if (bar) bar.classList.toggle("on", !closed && !!top && top.getBoundingClientRect().bottom < 0 && endTop > h);
   }
   addEventListener("scroll", () => { if (!queued) { queued = true; requestAnimationFrame(update); } }, { passive: true });
   addEventListener("resize", update);
   if (bar) bar.querySelector("button").addEventListener("click", () => {
      closed = true;
      bar.classList.remove("on");
      try { sessionStorage.setItem("slimio.ctaClosed", "1"); } catch (e) {}
   });
   update();
})();
