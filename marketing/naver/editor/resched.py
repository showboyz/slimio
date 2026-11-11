# resched.py <win> <NN> <YYYY.MM.DD> <HH> <YYYY-MM-DD> <HH> : move the reserved post of draft NN from the first date and
# hour to the second, nothing else changed. Opens the post from the editor's 예약 발행 list (title checked against the
# draft), opens the 발행 panel and checks it still says 예약 · old date · old hour · 전체공개 with 10 tags, sets the new
# date and hour with sched.sh, checks the panel again with the new values and only then presses 발행. Written 2026-11-12
# to give the 11/18–11/21 slots to the score-report posts #78–#81 (owner: '앞으로 땡기고'). Anything unexpected leaves
# the editor without saving.
import os, re, sys, time
import tblfix as tf
from tblfix_sched import go, wait_for, leave_unsaved, log, EDITOR, NAVER
tf.W = W = sys.argv[1]
n, date, hh, new, nh = int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), sys.argv[5], int(sys.argv[6])
draft = [f for f in os.listdir(NAVER) if re.match(rf'{n:02d}-.*\.html$', f)][0]
title = re.search(r'제목: (.*)', open(os.path.join(NAVER, draft)).read()).group(1).strip()

def fail(why):   # the tree at the moment of failure goes to $TMPDIR/resched_<NN>.txt
    log(n, 'FAIL', why); open(os.path.join(os.environ.get('TMPDIR', '/tmp'), f'resched_{n}.txt'), 'w').write(tf.tree())
    leave_unsaved(); tf.done(); sys.exit(1)
def panel(d, h):   # (the 발행 panel says 예약 · date d · h:00 · 전체공개 with 10 tags, number of tags)
    t = tf.tree(); y, mo, dd = d.replace('-', '.').split('.')
    tags = re.findall(r'\d+ container (\S+)\n', t.split('태그 편집')[1].split('발행 시간')[0]) if '태그 편집' in t else []
    ok = (re.search(r'라디오 버튼 \(settable\) 예약, Value: 1', t) and f'Value: {y}. {mo}. {dd}' in t
          and re.search(rf'시간 선택, Value: {h:02d}', t) and re.search(r'분 선택, Value: 00', t)
          and re.search(r'전체공개, Value: 1', t) and len(tags) == 10)
    return bool(ok), len(tags)

if not tf.guard(): log(n, 'STOP owner busy for 3 h'); sys.exit(2)
go(EDITOR); tf.done(); time.sleep(3)
t = wait_for(r'예약 발행 \d+ 건', 30) or ''
if not t: fail('editor did not open')
if '작성 중인 글이 있습니다' in t: tf.press(r'^버튼 취소$'); time.sleep(1.5)
tf.press(r'^버튼 예약 발행 \d+ 건'); time.sleep(1.5)
when = f'{date} {hh:02d}:00'
item = [l for l in tf.tree().splitlines() if re.search(rf'\d+ 버튼 .* {re.escape(when)}$', l)]
if len(item) != 1: fail(f'list item {len(item)}')
if re.match(rf'\s*\d+ 버튼 (.*) {re.escape(when)}$', item[0]).group(1).strip() != title: fail('the post at that time is not draft ' + draft)
tf.press(rf'^버튼 .* {re.escape(when)}$'); time.sleep(5)
if not wait_for(rf'텍스트, Value: {re.escape(title)}', 20): fail('post did not load')
log(n, draft, 'loaded')

if not tf.guard(): log(n, 'STOP owner busy for 3 h (post left open, not saved)'); sys.exit(2)
tf.press(r'^버튼 발행$'); time.sleep(2)
ok, k = panel(date, hh)
if not ok: fail(f'panel before the change, tags {k}')
r = tf.sh('bash', f'{tf.T}/sched.sh', W, new, f'{nh:02d}'); tf.done()
log(n, 'sched.sh', r.stdout.strip().splitlines()[-1][-160:] if r.stdout.strip() else r.stderr[-160:])
ok, k = panel(new, nh)
if not ok: fail(f'panel after the change, tags {k}')
b = [l.split()[0] for l in tf.tree().splitlines() if re.match(r'\s*\d+ 버튼 발행$', l)]
tf.sh('orca', 'computer', 'click', '--app', 'com.google.Chrome', '--window-id', W, '--element-index', b[-1], '--no-screenshot')
tf.done(); time.sleep(5)
home = re.search(r'주소창 및 검색창, Value: blog\.naver\.com/todayz777(,|$)', tf.tree(), re.M)
log(n, f'MOVED {when} -> {new} {nh:02d}:00' if home else 'CHECK: 발행 clicked but did not return to the blog home')
