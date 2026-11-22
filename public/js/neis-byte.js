// NEIS byte counter (/ko/neis-byte-counter.html, Korean only).
// The 2026 학교생활기록부 기재요령 (교육부; 초 p.150, 중 p.162, 고 p.208) says the education information
// system counts in bytes: 한글 1자 = 3 bytes, English letters and digits = 1, Enter = 1. That is the UTF-8
// length of the text with each line break as one "\n", so everything else (space 1, · 2, “ ” 3, emoji 4)
// is counted the same way. The guide has no line for symbols, and the page says so.
// Nothing is sent anywhere: the text stays in the page.
const enc = new TextEncoder();

export const neisBytes = (s) => enc.encode(s.replace(/\r\n?/g, "\n")).length;

// "영역별 입력 가능 최대 글자수" tables of the 2026 guides, in 한글 characters (× 3 = bytes).
// Elementary schools have no limit on 창의적 체험활동, 교과학습발달상황 or 행동특성 (the system's own limit only).
const AREAS = {
   high: [
      ["과목별 세부능력 및 특기사항", 500, "과목별 500자. 2026학년도 1~2학년 공통과목(공통국어·공통수학·공통영어·통합사회·통합과학·한국사·과학탐구실험)은 1·2를 합쳐 500자예요."],
      ["개인별 세부능력 및 특기사항", 500],
      ["행동특성 및 종합의견", 300],
      ["자율·자치활동 특기사항", 500, "3학년은 자율활동이에요."],
      ["동아리활동 특기사항", 500],
      ["진로활동 특기사항", 500],
      ["봉사활동 활동내용", 50, "실적별 50자예요."],
      ["독서활동 (과목별)", 250],
      ["독서활동 (공통)", 500],
      ["일상생활 활동상황 특기사항", 1000],
      ["출결상황 특기사항", 500],
      ["인적·학적사항 특기사항", 500],
      ["수상명", 100],
      ["자격증 명칭 또는 종류", 100],
   ],
   middle: [
      ["과목별 세부능력 및 특기사항", 500],
      ["개인별 세부능력 및 특기사항", 500],
      ["행동특성 및 종합의견", 300],
      ["자율·자치활동 특기사항", 500, "3학년은 자율활동이에요."],
      ["동아리활동 특기사항", 500],
      ["진로활동 특기사항", 500],
      ["봉사활동 활동내용", 50, "실적별 50자예요."],
      ["자유학기 진로탐색활동", 1000],
      ["자유학기 주제선택활동", 1000],
      ["자유학기 예술·체육활동", 1000],
      ["자유학기 동아리활동", 1000],
      ["독서활동 (과목별)", 250],
      ["독서활동 (공통)", 500],
      ["일상생활 활동상황 특기사항", 1000],
      ["출결상황 특기사항", 500],
      ["인적·학적사항 특기사항", 500],
      ["수상명", 100],
   ],
   elem: [
      ["출결상황 특기사항", 500],
      ["인적·학적사항 특기사항", 500],
      ["봉사활동 활동내용", 50, "실적별 50자예요."],
   ],
};
const YEAR_NOTE = "최대 글자수는 학년 단위예요";   // 고등학교 표: 과목별 세특은 예외

const text = $("text"), level = $("level"), area = $("area"), custom = $("custom");
const fmt = (n) => n.toLocaleString("ko-KR");

function fillAreas() {
   const lv = level.value;
   area.innerHTML = "";
   for (const [name, chars] of AREAS[lv]) area.add(new Option(`${name} — ${fmt(chars)}자 (${fmt(chars * 3)}Byte)`, chars * 3));
   area.add(new Option("직접 입력 (바이트)", "custom"));
   $("elemnote").hidden = lv !== "elem";
}

function limit() {
   if (area.value !== "custom") return +area.value;
   const n = parseInt(custom.value, 10);
   return n > 0 ? n : 0;
}

function areaNote() {
   if (area.value === "custom") return "";
   const row = AREAS[level.value][area.selectedIndex];
   const parts = [];
   if (row && row[2]) parts.push(row[2]);
   if (row && !(level.value === "high" && row[0].startsWith("과목별"))) parts.push(YEAR_NOTE + ". 한 학년 동안 쓴 내용을 합친 양이 이 안에 들어가야 해요.");
   return parts.join(" ");
}

// The longest start of the text that fits in `max` bytes (whole characters only).
function cut(s, max) {
   let used = 0, i = 0;
   for (const ch of s) {
      const b = ch === "\n" ? 1 : enc.encode(ch).length;
      if (used + b > max) break;
      used += b; i += ch.length;
   }
   return i;
}

const esc = (s) => s.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" })[c]);
let tracked = false;

function update() {
   const s = text.value.replace(/\r\n?/g, "\n");
   const bytes = neisBytes(s);
   const max = limit();
   let ko = 0, ascii = 0, other = 0, spaces = 0, lines = 0;
   for (const ch of s) {
      if (ch === "\n") lines++;
      else if (/\s/.test(ch)) spaces++;
      else if (/[가-힣ㄱ-ㅎㅏ-ㅣ]/.test(ch)) ko++;
      else if (ch.charCodeAt(0) < 128) ascii++;
      else other++;
   }
   const chars = [...s].length;
   $("bytes").textContent = fmt(bytes);
   $("max").textContent = max ? fmt(max) : "—";
   $("chars").textContent = fmt(chars);
   $("nospace").textContent = fmt(chars - spaces - lines);
   $("kinds").textContent = `한글 ${fmt(ko)}자 · 영문·숫자·문장부호 ${fmt(ascii)}자 · 띄어쓰기 ${fmt(spaces)}개 · 엔터 ${fmt(lines)}개 · 그 밖의 기호 ${fmt(other)}자`;

   const meter = $("meter"), left = $("left"), over = bytes > max && max > 0;
   meter.style.width = max ? Math.min(100, (bytes / max) * 100) + "%" : "0";
   meter.classList.toggle("over", over);
   $("stat").classList.toggle("over", over);
   if (!max) left.textContent = "바이트 한도를 입력하면 남은 양을 알려 드려요.";
   else if (over) left.textContent = `${fmt(bytes - max)}Byte 넘었어요 (한글로 약 ${fmt(Math.ceil((bytes - max) / 3))}자 줄이기)`;
   else left.textContent = `${fmt(max - bytes)}Byte 남았어요 (한글로 약 ${fmt(Math.floor((max - bytes) / 3))}자 더)`;

   // where the limit falls: the part that won't fit, highlighted
   const box = $("overflow");
   if (over) {
      const i = cut(s, max);
      $("overtext").innerHTML = esc(s.slice(Math.max(0, i - 40), i)) + "<mark>" + esc(s.slice(i)) + "</mark>";
      box.hidden = false;
   } else box.hidden = true;

   $("note").textContent = areaNote();
   $("note").hidden = !$("note").textContent;
   $("customrow").hidden = area.value !== "custom";
   if (s && !tracked) { tracked = true; SlimIO.track(); }
}

level.addEventListener("change", () => { fillAreas(); update(); });
area.addEventListener("change", update);
custom.addEventListener("input", update);
text.addEventListener("input", update);
$("copy").addEventListener("click", async () => {
   try { await navigator.clipboard.writeText(text.value); $("copy").textContent = "복사했어요"; }
   catch (e) { text.select(); document.execCommand("copy"); $("copy").textContent = "복사했어요"; }
   setTimeout(() => ($("copy").textContent = "글 복사"), 1500);
});
$("clear").addEventListener("click", () => { text.value = ""; update(); text.focus(); });

fillAreas();
update();
