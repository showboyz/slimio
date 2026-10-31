# tnew.py <win> <draft.html> <YYYY-MM-DD> <HH> : one Tistory post, reserved for that date at HH:00, in my own window.
# New post → category 문서·사진 꿀팁 → HTML mode (confirm) → title → tags (while the editor is empty, so the tag
# field is on screen) → body → 완료 → 공개 → 예약 date/hour/minute → 대표이미지 (file dialog) → 공개 발행 →
# check the post list row '[예약] <title>' with the date. Stops on the first thing that doesn't look right.
import os, sys, re, time, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../naver/editor'))
import tblfix as tf
from tblfix_sched import go
W, draft, date, hh = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
FROM_BODY = len(sys.argv) > 5 and sys.argv[5] in ('from-body', 'from-panel')   # title and tags already in
FROM_PANEL = len(sys.argv) > 5 and sys.argv[5] == 'from-panel'   # body in, publish panel open
tf.W = W
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.normpath(os.path.join(HERE, '../../public/img/blog')) + '/'   # the 폴더로 이동 field won't take '..'
src = open(draft).read()
title = re.search(r'제목: (.*)', src).group(1).strip()
tags = [t.strip() for t in re.search(r'태그: (.*)', src).group(1).split(',') if t.strip()]
hero = re.search(r'대표이미지: (\S+)', src).group(1)
body = re.sub(r'^<!--.*?-->\s*', '', src, flags=re.S).strip() + '\n'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import cta
if body.count(cta.EYEBROW) != 1 or cta.EYEBROW_END in body:   # marketing/WRITING.md: one button per post
    sys.exit(f'{draft}: not exactly one SlimIO button box - run python3 marketing/tistory/cta.py {draft} first')
y, mo, d = (int(x) for x in date.split('-'))

def need(ok, why):
    if not ok: print('FAIL', why, flush=True); sys.exit(1)
def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)
def paste_into(pat, text):
    subprocess.run('pbcopy', input=text, text=True)
    i = tf.idx(tf.tree(), pat); need(i, 'field ' + pat)
    tf.k('click', '--element-index', i); time.sleep(0.4)
    tf.k('hotkey', '--key', 'CmdOrCtrl+V'); time.sleep(0.8)

if not FROM_BODY:
  go('https://ddoua.tistory.com/manage/newpost/'); tf.done(); time.sleep(6)
  t = tf.tree()
  if '작성 중인 글' in t or '이어서 작성' in t:   # resume-draft prompt: start fresh
      tf.press(r'^버튼 취소$'); time.sleep(1.5)
  need(tf.idx(tf.tree(), r'^콤보 상자 \(settable\) 카테고리 선택'), 'editor not open')
  tf.press(r'^콤보 상자 \(settable\) 카테고리 선택'); time.sleep(1)
  need(tf.press(r'^텍스트, Value: 문서·사진 꿀팁$'), 'category'); time.sleep(0.8)
  need(tf.press(r'^팝업 버튼 기본모드$'), 'mode menu'); time.sleep(1)
  need(tf.press(r'^메뉴 항목 HTML$'), 'HTML item'); time.sleep(1.2)
  tf.press(r'^버튼 확인$'); time.sleep(1.5)
  paste_into(r'^텍스트 엔트리 영역 \(settable\) Placeholder: 제목을 입력하세요', title)
  for tg in tags:
      paste_into(r'^텍스트 필드 \(settable\) 태그', tg)
      tf.k('press-key', '--key', 'Return'); time.sleep(0.5)
  t = tf.tree()
  tagbox = next((l for l in t.splitlines() if '태그 수정' in l), '')
  got = sum(1 for g in tags if g in tagbox)
  log('tags typed', len(tags), '(the tree shows', got, '- its text is cut short; check the screenshot)')
def open_panel():
    # pressing the 완료 element doesn't always open the panel; a click at its spot (1875×1200 window) does
    for _ in range(3):
        if tf.idx(tf.tree(), r'^라디오 버튼 \(settable\) 공개,'): return True
        tf.sh('bash', f'{tf.T}/k.sh', W, 'click', '--x', '1772', '--y', '1166'); tf.done(); time.sleep(2.5)
    return bool(tf.idx(tf.tree(), r'^라디오 버튼 \(settable\) 공개,'))
if not FROM_PANEL:
    paste_into(r'^텍스트 엔트리 영역 \(settable\)$', body); time.sleep(2)
    log('title, tags, body in')
need(open_panel(), 'publish panel')
need(tf.press(r'^라디오 버튼 \(settable\) 공개, Value: 0$') or tf.idx(tf.tree(), r'^라디오 버튼 \(settable\) 공개, Value: 1$'), 'public radio')
time.sleep(0.8)
need(tf.press(r'^버튼 예약$'), 'reserve button'); time.sleep(1)
need(tf.press(r'^버튼 2026-\d\d-\d\d$'), 'date button'); time.sleep(1)
for _ in range(3):
    if f'2026년 {mo}월' in tf.tree(): break
    tf.press(r'^버튼 다음날짜$'); time.sleep(0.8)
need(f'{y}년 {mo}월' in tf.tree(), 'month')
need(tf.press(rf'^버튼 {d}$'), 'day'); time.sleep(0.8)
def val(name):
    l = [x for x in tf.tree().splitlines() if f'증감자 {name}' in x][0]
    return int(re.search(r'Value: (\d+)', l).group(1)), l.split()[0]
def step(name, target):
    for _ in range(70):
        v, i = val(name)
        if v == target: return True
        tf.sh('orca', 'computer', 'perform-secondary-action', '--app', 'com.google.Chrome', '--window-id', W, '--element-index', i,
              '--action', 'increment' if v < target else 'decrement', '--no-screenshot'); time.sleep(0.15)
    return False
need(step('시간', hh) and step('분', 0), 'time')
need(tf.idx(tf.tree(), rf'^버튼 {date}$'), 'date not set')
r = tf.sh('bash', f'{HERE}/pick.sh', W, IMG + hero); time.sleep(1)
if 'picked' not in r.stdout:   # the dialog is a sheet: its 열기 button is in this window's tree
    need(tf.press(r'^버튼 열기$'), 'open button ' + r.stdout); time.sleep(4)
tf.done()
need(tf.idx(tf.tree(), r'^버튼 공개 발행$'), 'publish button')
need(tf.idx(tf.tree(), rf'^버튼 {date}$'), 'date lost')
tf.press(r'^버튼 공개 발행$'); time.sleep(6)
t = tf.tree()
rows = t.splitlines()
k = [n for n, l in enumerate(rows) if '[예약]' in l and title[:25] in l]
need(k, 'no [예약] row')
when = next((l for l in rows[k[0]:k[0] + 12] if re.search(r'Value: 2026-\d\d-\d\d \d\d:\d\d', l)), '')
log('RESERVED', title[:30], re.search(r'2026-\S+ \S+', when).group(0) if when else '?')
