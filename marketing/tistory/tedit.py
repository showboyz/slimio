# tedit.py <win> <draft.html> <post-id> (<YYYY-MM-DD> <HH> | live) [panel] : put the draft's body into an existing Tistory
# post. For a reserved post give its date and hour: the panel must still say 공개 · 예약 · that date · HH:00 (it sets
# them again if not) and the post list must show the [예약] row. For a published post give 'live': its date is left
# alone and the public page must show the buttons afterwards. Opens /manage/newpost/<id>, checks the title is the
# draft's, HTML mode, select-all + paste the body, 완료, panel checks, 공개 발행. 'panel' stops with the panel open and
# prints it (to look at a case the script doesn't know yet). Stops on the first thing that doesn't look right.
import os, sys, re, time, subprocess, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../naver/editor'))
import tblfix as tf
from tblfix_sched import go, wait_for
W, draft, pid = sys.argv[1], sys.argv[2], sys.argv[3]
LIVE = sys.argv[4] == 'live'
date, hh = (None, None) if LIVE else (sys.argv[4], int(sys.argv[5]))
STOP_AT_PANEL = sys.argv[-1] == 'panel'
tf.W = W
src = open(draft).read()
title = re.search(r'제목: (.*)', src).group(1).strip()
body = re.sub(r'^<!--.*?-->\s*', '', src, flags=re.S).strip() + '\n'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import cta
if cta.EYEBROW not in body or cta.EYEBROW_END not in body:   # marketing/WRITING.md: every post gets the two buttons
    sys.exit(f'{draft}: no SlimIO button boxes - run python3 marketing/tistory/cta.py {draft} first')

def need(ok, why):
    if not ok: print('FAIL', why, flush=True); sys.exit(1)
def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

def leave_prompt():
    # the editor asks Chrome's 'leave site?' when we navigate away; nothing of ours is saved half-way, so leave
    if '사이트에서 나가시겠습니까' in tf.tree(): tf.press(r'^버튼 나가기$'); time.sleep(3)
leave_prompt()
go(f'https://ddoua.tistory.com/manage/newpost/{pid}?type=post'); tf.done(); time.sleep(2)
leave_prompt(); time.sleep(2)
t = wait_for(r'제목을 입력하세요|작성 중인 글|이어서 작성', 30) or ''
if '작성 중인 글' in t or '이어서 작성' in t:   # resume-draft prompt: keep the saved post, not a stale draft
    tf.press(r'^버튼 취소$'); time.sleep(1.5); t = tf.tree()
got = next((l for l in t.splitlines() if '제목을 입력하세요' in l), '')
need(f'Value: {title}' in got, f'title field {got.strip()[:90]!r} is not the draft title')
MODE = r'^(팝업 )?버튼 {}( 더보기)?$'   # new post: '팝업 버튼 기본모드'; edit page: '버튼 HTML 더보기'
if tf.idx(t, MODE.format('기본모드')):
    need(tf.press(MODE.format('기본모드')), 'mode menu'); time.sleep(1)
    need(tf.press(r'^메뉴 항목 HTML$'), 'HTML item'); time.sleep(1.2)
    tf.press(r'^버튼 확인$'); time.sleep(1.5)
need(tf.idx(tf.tree(), MODE.format('HTML')), 'not in HTML mode')
subprocess.run('pbcopy', input=body, text=True)
i = tf.idx(tf.tree(), r'^텍스트 엔트리 영역 \(settable\)$'); need(i, 'body field')
tf.k('click', '--element-index', i); time.sleep(0.4)
# Cmd+A never reaches the code editor (2026-10-31: the paste went in front of the old body and both were saved).
# Chrome's context menu 모두 선택 does: right-click inside the code, the menu opens down-right of the pointer.
X, Y = 1000, 420
tf.k('click', '--x', str(X), '--y', str(Y), '--mouse-button', 'right'); time.sleep(1)
tf.k('click', '--x', str(X + 38), '--y', str(Y + 206)); time.sleep(0.6)
tf.k('hotkey', '--key', 'CmdOrCtrl+V'); time.sleep(2)
log('body replaced', len(body), 'chars')

def open_panel():
    for _ in range(3):
        if tf.idx(tf.tree(), r'^라디오 버튼 \(settable\) 공개,'): return True
        tf.sh('bash', f'{tf.T}/k.sh', W, 'click', '--x', '1772', '--y', '1166'); tf.done(); time.sleep(2.5)
    return bool(tf.idx(tf.tree(), r'^라디오 버튼 \(settable\) 공개,'))
need(open_panel(), 'publish panel')
if STOP_AT_PANEL:
    t = tf.tree(); a = t.find('발행정보 입력폼')
    print(t[a:a + 3000]); sys.exit(0)
need(tf.press(r'^라디오 버튼 \(settable\) 공개, Value: 0$') or tf.idx(tf.tree(), r'^라디오 버튼 \(settable\) 공개, Value: 1$'), 'public radio')
time.sleep(0.8)
def val(name):
    l = [x for x in tf.tree().splitlines() if f'증감자 {name}' in x]
    return (int(re.search(r'Value: (\d+)', l[0]).group(1)), l[0].split()[0]) if l else (None, None)
if not LIVE:
    y, mo, d = (int(x) for x in date.split('-'))
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
else:
    need(not tf.idx(tf.tree(), r'^증감자 시간'), 'a published post shows a reservation time')
b = tf.idx(tf.tree(), r'^버튼 (공개 발행|공개 수정|수정|발행)$'); need(b, 'publish button')
tf.sh('orca', 'computer', 'click', '--app', 'com.google.Chrome', '--window-id', W, '--element-index', b, '--no-screenshot')
tf.done(); time.sleep(6)
def snippets():
    text = re.sub(r'<div style="margin:36px auto.*?</div>', '', body, flags=re.S)   # not the boxes' own lines
    paras = [tf.plain(p) for p in re.findall(r'<p[^>]*>(.*?)</p>', text, re.S)]
    paras = [p for p in paras if len(p) > 25]
    return [paras[0][:20], paras[-1][:20], cta.EYEBROW, cta.EYEBROW_END]
def check_saved():
    leave_prompt()
    go(f'https://ddoua.tistory.com/manage/newpost/{pid}?type=post'); tf.done(); time.sleep(2)
    leave_prompt(); wait_for(r'제목을 입력하세요', 30); time.sleep(2)
    l = next((l for l in tf.tree().splitlines() if '글 내용 입력' in l), '')
    if not l: return 'reopened in HTML mode, counts not checked'
    n = {s: l.count(s) for s in snippets()}
    need(all(v == 1 for v in n.values()), f'saved body is not the draft once: {n}')
    return 'saved body checked once each'
if LIVE:
    time.sleep(4)
    page = urllib.request.urlopen(urllib.request.Request(f'https://ddoua.tistory.com/{pid}?t={int(time.time())}',
                                                         headers={'User-Agent': 'Mozilla/5.0'})).read().decode()
    need(len(re.findall(r'margin:\s*36px auto', page)) == 2 and cta.EYEBROW in page, 'the public page does not show both buttons')
    need(all(page.count(s) == 1 for s in snippets()[:2]), 'the public page has the body more than once')
    log('SAVED live', title[:30], f'https://ddoua.tistory.com/{pid}', check_saved())
else:
    rows = tf.tree().splitlines()
    k = [n for n, l in enumerate(rows) if '[예약]' in l and title[:25] in l]
    need(k, 'no [예약] row')
    when = next((l for l in rows[k[0]:k[0] + 12] if re.search(r'Value: 2026-\d\d-\d\d \d\d:\d\d', l)), '')
    log('SAVED', title[:30], re.search(r'2026-\S+ \S+', when).group(0) if when else '?', check_saved())
