# tblfix_sched.py <win> <YYYY.MM.DD>... : restyle the tables of scheduled posts (see tblfix.py) and save them
# with their schedule unchanged. For each date: open the editor, skip the "작성 중인 글" prompt, pick the post
# from the 예약 발행 list, check its title against the draft, style every table, then open the 발행 panel and
# publish only if it still says 예약 · that date · 08:00 · 전체공개 and every table was styled. Otherwise it
# leaves the editor without saving. Drafts are matched by the 제목: line of marketing/naver/NN-*.html.
import glob, json, os, re, sys, time
import tblfix as tf
W = sys.argv[1]; tf.W = W
NAVER = os.path.dirname(tf.T)
EDITOR = 'https://blog.naver.com/todayz777?Redirect=Write&'

def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)
def drafts():
    out = {}
    for f in sorted(glob.glob(f'{NAVER}/[0-9]*.html')):
        m = re.search(r'제목: (.*)', open(f).read())
        if m: out[m.group(1).strip()] = f
    return out
def go(url):
    t = tf.tree(); i = tf.idx(t, r'^텍스트 필드 \(settable\) 주소창')
    tf.sh('orca', 'computer', 'set-value', '--app', 'com.google.Chrome', '--window-id', W, '--element-index', i, '--value', url)
    tf.k('click', '--element-index', i); tf.k('press-key', '--key', 'Return')
def leave_unsaved():
    go('https://blog.naver.com/todayz777'); time.sleep(2)
    tf.press(r'^버튼 나가기$'); time.sleep(2)
def wait_for(pat, n=20):
    for _ in range(n):
        t = tf.tree()
        if re.search(pat, t): return t
        time.sleep(1)

D = drafts()
for date in sys.argv[2:]:
    if not tf.guard(): log(date, 'STOP owner busy for 3 h'); break
    go(EDITOR); time.sleep(5)
    t = wait_for(r'예약 발행 \d+ 건')
    if t and '작성 중인 글이 있습니다' in t: tf.press(r'^버튼 취소$'); time.sleep(1.5)
    tf.press(r'^버튼 예약 발행 \d+ 건'); time.sleep(1.5)
    t = tf.tree()
    item = [l for l in t.splitlines() if re.search(rf'\d+ 버튼 .* {re.escape(date)} 08:00$', l)]
    if len(item) != 1: log(date, 'FAIL list item', len(item)); continue
    title = re.match(rf'\s*\d+ 버튼 (.*) {re.escape(date)} 08:00$', item[0]).group(1).strip()
    draft = D.get(title)
    if not draft: log(date, 'FAIL no draft for', title); continue
    tf.press(rf'^버튼 .* {re.escape(date)} 08:00$'); time.sleep(4)
    if not wait_for(rf'텍스트, Value: {re.escape(title)}'): log(date, 'FAIL post did not load'); leave_unsaved(); continue
    log(date, os.path.basename(draft))
    try: n, ok = tf.fix(W, draft)
    except SystemExit as e: log(date, 'FAIL', e); leave_unsaved(); continue
    if n == 0: log(date, 'no tables, left as it was'); leave_unsaved(); continue
    if ok != n: log(date, f'FAIL styled {ok}/{n}, left without saving'); leave_unsaved(); continue
    if not tf.guard(): log(date, 'STOP owner busy for 3 h (post left open)'); break
    tf.press(r'^버튼 발행$'); time.sleep(2)
    t = tf.tree(); y, mo, d = date.split('.')
    tags = re.findall(r'\d+ container (\S+)\n', t.split('태그 편집')[1].split('발행 시간')[0]) if '태그 편집' in t else []
    ok_panel = (re.search(r'라디오 버튼 \(settable\) 예약, Value: 1', t) and f'Value: {y}. {mo}. {d}' in t
                and re.search(r'시간 선택, Value: 08', t) and re.search(r'분 선택, Value: 00', t)
                and re.search(r'전체공개, Value: 1', t) and len(tags) == 10)
    if not ok_panel: log(date, 'FAIL panel check, tags', len(tags)); leave_unsaved(); continue
    b = [l.split()[0] for l in t.splitlines() if re.match(r'\s*\d+ 버튼 발행$', l)]
    tf.sh('orca', 'computer', 'click', '--app', 'com.google.Chrome', '--window-id', W, '--element-index', b[-1], '--no-screenshot')
    tf.done(); time.sleep(5)
    home = re.search(r'주소창 및 검색창, Value: blog\.naver\.com/todayz777(,|$)', tf.tree(), re.M)
    log(date, f'SAVED {ok}/{n} tables' if home else 'CHECK: publish clicked but did not return to the blog home')
