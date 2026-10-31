# tedit.py <win> <draft.html> <post-id> <YYYY-MM-DD> <HH> : put the draft's body into an existing reserved Tistory post and
# keep its reservation. Opens /manage/newpost/<id>, checks the title is the draft's, HTML mode, select-all + paste the
# body, 완료, checks the panel still says 공개 · 예약 · that date · HH:00 (sets it again if not), presses 공개 발행, then
# checks the post list row. Stops on the first thing that doesn't look right.
import os, sys, re, time, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../naver/editor'))
import tblfix as tf
from tblfix_sched import go
W, draft, pid, date, hh = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
tf.W = W
src = open(draft).read()
title = re.search(r'제목: (.*)', src).group(1).strip()
body = re.sub(r'^<!--.*?-->\s*', '', src, flags=re.S).strip() + '\n'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import cta
if cta.EYEBROW not in body or cta.EYEBROW_END not in body:   # marketing/WRITING.md: every post gets the two buttons
    sys.exit(f'{draft}: no SlimIO button boxes - run python3 marketing/tistory/cta.py {draft} first')
y, mo, d = (int(x) for x in date.split('-'))

def need(ok, why):
    if not ok: print('FAIL', why, flush=True); sys.exit(1)
def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

go(f'https://ddoua.tistory.com/manage/newpost/{pid}?type=post'); tf.done(); time.sleep(6)
t = tf.tree()
if '작성 중인 글' in t or '이어서 작성' in t:   # resume-draft prompt: keep the saved post, not a stale draft
    tf.press(r'^버튼 취소$'); time.sleep(1.5); t = tf.tree()
got = next((l for l in t.splitlines() if '제목을 입력하세요' in l), '')
need(f'Value: {title}' in got, f'title field {got.strip()[:90]!r} is not the draft title')
if tf.idx(t, r'^팝업 버튼 기본모드$'):
    need(tf.press(r'^팝업 버튼 기본모드$'), 'mode menu'); time.sleep(1)
    need(tf.press(r'^메뉴 항목 HTML$'), 'HTML item'); time.sleep(1.2)
    tf.press(r'^버튼 확인$'); time.sleep(1.5)
need(tf.idx(tf.tree(), r'^팝업 버튼 HTML$'), 'not in HTML mode')
subprocess.run('pbcopy', input=body, text=True)
i = tf.idx(tf.tree(), r'^텍스트 엔트리 영역 \(settable\)$'); need(i, 'body field')
tf.k('click', '--element-index', i); time.sleep(0.4)
tf.k('hotkey', '--key', 'CmdOrCtrl+A'); time.sleep(0.4)
tf.k('hotkey', '--key', 'CmdOrCtrl+V'); time.sleep(2)
log('body replaced', len(body), 'chars')

def open_panel():
    for _ in range(3):
        if tf.idx(tf.tree(), r'^라디오 버튼 \(settable\) 공개,'): return True
        tf.sh('bash', f'{tf.T}/k.sh', W, 'click', '--x', '1772', '--y', '1166'); tf.done(); time.sleep(2.5)
    return bool(tf.idx(tf.tree(), r'^라디오 버튼 \(settable\) 공개,'))
need(open_panel(), 'publish panel')
need(tf.press(r'^라디오 버튼 \(settable\) 공개, Value: 0$') or tf.idx(tf.tree(), r'^라디오 버튼 \(settable\) 공개, Value: 1$'), 'public radio')
time.sleep(0.8)
def val(name):
    l = [x for x in tf.tree().splitlines() if f'증감자 {name}' in x]
    return (int(re.search(r'Value: (\d+)', l[0]).group(1)), l[0].split()[0]) if l else (None, None)
if not (tf.idx(tf.tree(), rf'^버튼 {date}$') and val('시간')[0] == hh and val('분')[0] == 0):
    log('reservation not shown as', date, hh, '- setting it again')
    need(tf.press(r'^버튼 예약$'), 'reserve button'); time.sleep(1)
    need(tf.press(r'^버튼 2026-\d\d-\d\d$'), 'date button'); time.sleep(1)
    for _ in range(3):
        if f'{y}년 {mo}월' in tf.tree(): break
        tf.press(r'^버튼 다음날짜$'); time.sleep(0.8)
    need(f'{y}년 {mo}월' in tf.tree(), 'month')
    need(tf.press(rf'^버튼 {d}$'), 'day'); time.sleep(0.8)
    def step(name, target):
        for _ in range(70):
            v, i = val(name)
            if v == target: return True
            tf.sh('orca', 'computer', 'perform-secondary-action', '--app', 'com.google.Chrome', '--window-id', W, '--element-index', i,
                  '--action', 'increment' if v < target else 'decrement', '--no-screenshot'); time.sleep(0.15)
        return False
    need(step('시간', hh) and step('분', 0), 'time')
need(tf.idx(tf.tree(), rf'^버튼 {date}$') and val('시간')[0] == hh and val('분')[0] == 0, 'reservation in the panel')
b = tf.idx(tf.tree(), r'^버튼 (공개 발행|공개 수정|수정|발행)$'); need(b, 'publish button')
tf.sh('orca', 'computer', 'click', '--app', 'com.google.Chrome', '--window-id', W, '--element-index', b, '--no-screenshot')
tf.done(); time.sleep(6)
rows = tf.tree().splitlines()
k = [n for n, l in enumerate(rows) if '[예약]' in l and title[:25] in l]
need(k, 'no [예약] row')
when = next((l for l in rows[k[0]:k[0] + 12] if re.search(r'Value: 2026-\d\d-\d\d \d\d:\d\d', l)), '')
log('SAVED', title[:30], re.search(r'2026-\S+ \S+', when).group(0) if when else '?')
