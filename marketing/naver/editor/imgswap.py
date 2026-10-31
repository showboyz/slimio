# imgswap.py <win> <YYYY.MM.DD> <HH> <old-image-name> <new-image-path> : in the scheduled post of that date and hour,
# put a new image where an old one is and save it with its schedule unchanged. The new file needs a different name
# (the tree names images by file name). Opens the post from the 예약 발행 list like tblfix_sched.py, selects the old
# image, uploads the new one (img.sh puts it after the selected component), checks it landed right after the old one,
# deletes the old one, checks the image count and the neighbouring text, then publishes only if the panel still says
# 예약 · that date · HH:00 · 전체공개 · 10 tags. Anything unexpected leaves the editor without saving.
import os, re, sys, time
import tblfix as tf
from tblfix_sched import go, wait_for, leave_unsaved, log, drafts, EDITOR
tf.W = W = sys.argv[1]
date, hh, old, new = sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5]
newname = os.path.basename(new)

def fail(why): log(date, 'FAIL', why); leave_unsaved(); tf.done(); sys.exit(1)
def images(t): return [(int(m.group(1)), m.group(2)) for m in re.finditer(r'^\s*(\d+) 이미지 (\S+)', t, re.M)]
def around(t, name):
    # the text lines just before and after the image, to see it stayed in the same place
    rows = t.splitlines(); k = next(n for n, l in enumerate(rows) if re.match(rf'\s*\d+ 이미지 {re.escape(name)}', l))
    near = lambda r: [re.sub(r'^\s*\d+ ', '', l) for l in r if re.match(r'\s*\d+ 텍스트', l)]
    return near(rows[max(0, k - 6):k])[-1:], near(rows[k + 1:k + 8])[:1]

if newname == old: sys.exit('the new file needs a different name')
if not tf.guard(): log(date, 'STOP owner busy for 3 h'); sys.exit(2)
go(EDITOR); tf.done(); time.sleep(5)
t = wait_for(r'예약 발행 \d+ 건')
if not t: fail('editor did not open')
if '작성 중인 글이 있습니다' in t: tf.press(r'^버튼 취소$'); time.sleep(1.5)
tf.press(r'^버튼 예약 발행 \d+ 건'); time.sleep(1.5)
when = f'{date} {hh:02d}:00'
item = [l for l in tf.tree().splitlines() if re.search(rf'\d+ 버튼 .* {re.escape(when)}$', l)]
if len(item) != 1: fail(f'list item {len(item)}')
title = re.match(rf'\s*\d+ 버튼 (.*) {re.escape(when)}$', item[0]).group(1).strip()
if title not in drafts(): fail('no draft for ' + title)
tf.press(rf'^버튼 .* {re.escape(when)}$'); time.sleep(4)
if not wait_for(rf'텍스트, Value: {re.escape(title)}'): fail('post did not load')
t = tf.tree(); before = images(t)
if [n for _, n in before].count(old) != 1: fail(f'old image found {[n for _, n in before].count(old)} times')
ctx = around(t, old)
log(date, title[:30], 'images', len(before), 'old', old, 'near', ctx)
i = next(k for k, n in before if n == old)
tf.sh('python3', f'{tf.T}/c.py', W, '-', 'click', '--element-index', str(i)); tf.done(); time.sleep(0.8)
r = tf.sh('bash', f'{tf.T}/img.sh', W, new); tf.done(); time.sleep(2)
t = tf.tree(); mid = [n for _, n in images(t)]
if newname not in mid or mid.index(newname) != mid.index(old) + 1: fail(f'new image not right after the old one: {mid}')
i = next(k for k, n in images(t) if n == old)
tf.sh('python3', f'{tf.T}/c.py', W, '-', 'click', '--element-index', str(i)); tf.done(); time.sleep(0.8)
tf.k('press-key', '--key', 'Delete'); time.sleep(1.5)
t = tf.tree(); after = [n for _, n in images(t)]
want = [newname if n == old else n for _, n in before]
if after != want: fail(f'images after delete {after}')
if around(t, newname) != ctx: fail(f'neighbouring text changed {around(t, newname)}')
log(date, 'swapped, images', after)
if not tf.guard(): log(date, 'STOP owner busy for 3 h (post left open)'); sys.exit(2)
tf.press(r'^버튼 발행$'); time.sleep(2)
t = tf.tree(); y, mo, d = date.split('.')
tags = re.findall(r'\d+ container (\S+)\n', t.split('태그 편집')[1].split('발행 시간')[0]) if '태그 편집' in t else []
ok = (re.search(r'라디오 버튼 \(settable\) 예약, Value: 1', t) and f'Value: {y}. {mo}. {d}' in t
      and re.search(rf'시간 선택, Value: {hh:02d}', t) and re.search(r'분 선택, Value: 00', t)
      and re.search(r'전체공개, Value: 1', t) and len(tags) == 10)
if not ok: fail(f'panel check, tags {len(tags)}')
b = [l.split()[0] for l in t.splitlines() if re.match(r'\s*\d+ 버튼 발행$', l)]
tf.sh('orca', 'computer', 'click', '--app', 'com.google.Chrome', '--window-id', W, '--element-index', b[-1], '--no-screenshot')
tf.done(); time.sleep(5)
home = re.search(r'주소창 및 검색창, Value: blog\.naver\.com/todayz777(,|$)', tf.tree(), re.M)
log(date, 'SAVED' if home else 'CHECK: publish clicked but did not return to the blog home')
