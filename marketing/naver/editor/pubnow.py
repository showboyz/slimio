# pubnow.py <win> <NN> <YYYY.MM.DD> <HH> [--dry] : publish the reserved post of draft NN now instead of at its slot
# (owner, 2026-11-02: one more 운전면허 post today). Opens it from the 예약 발행 list, checks its title against the draft
# and that it carries the one button picture, opens the 발행 panel and checks 예약 · that date and hour · 전체공개 ·
# 10 tags, then switches 발행 시간 to 현재 and publishes. --dry stops at the panel, prints its lines and leaves unsaved.
import os, re, sys, time
import tblfix as tf
from tblfix_sched import go, wait_for, leave_unsaved, log, EDITOR, NAVER
tf.W = W = sys.argv[1]
n, date, hh = int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
dry = '--dry' in sys.argv
draft = [f for f in os.listdir(NAVER) if re.match(rf'{n:02d}-.*\.html$', f)][0]
title = re.search(r'제목: (.*)', open(os.path.join(NAVER, draft)).read()).group(1).strip()

def fail(why): log(n, 'FAIL', why); leave_unsaved(); tf.done(); sys.exit(1)
def click(i): tf.sh('orca', 'computer', 'click', '--app', 'com.google.Chrome', '--window-id', W, '--element-index', i, '--no-screenshot'); tf.done()
def clear_leftovers():
    for _ in range(3):
        if tf.press(r'^버튼 검색 바 닫기$'): time.sleep(0.5)
        elif '사이트에서 나가시겠습니까' in tf.tree(): tf.press(r'^버튼 나가기$'); time.sleep(3)
        else: return

if not tf.guard(): log(n, 'STOP owner busy for 3 h'); sys.exit(2)
clear_leftovers()
go(EDITOR); tf.done(); time.sleep(3)
clear_leftovers(); time.sleep(1)
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
links = sum(1 for l in tf.tree().splitlines() if re.match(r'\s*\d+ 텍스트, Value: 링크$', l))
if links != 1: fail(f'{links} link badges (expected the one button picture)')

if not tf.guard(): log(n, 'STOP owner busy for 3 h (post left open, not saved)'); sys.exit(2)
tf.press(r'^버튼 발행$'); time.sleep(2)
t = tf.tree(); y, mo, dd = date.split('.')
tags = re.findall(r'\d+ container (\S+)\n', t.split('태그 편집')[1].split('발행 시간')[0]) if '태그 편집' in t else []
ok = (re.search(r'라디오 버튼 \(settable\) 예약, Value: 1', t) and f'Value: {y}. {mo}. {dd}' in t
      and re.search(rf'시간 선택, Value: {hh:02d}', t) and re.search(r'분 선택, Value: 00', t)
      and re.search(r'전체공개, Value: 1', t) and len(tags) == 10)
if dry:
    for l in t.splitlines():
        if re.search(r'라디오|발행|Value: 20\d\d\.', l): print(l.strip())
    log(n, 'DRY panel ok' if ok else f'DRY panel check failed, tags {len(tags)}'); leave_unsaved(); tf.done(); sys.exit(0)
if not ok: fail(f'panel check, tags {len(tags)}')
r = tf.idx(t, r'^라디오 버튼 \(settable\) 현재')
if not r: fail('no 현재 radio')
click(r); time.sleep(1)
t = tf.tree()
if not re.search(r'라디오 버튼 \(settable\) 현재, Value: 1', t): fail('현재 not selected')
b = [l.split()[0] for l in t.splitlines() if re.match(r'\s*\d+ 버튼 발행$', l)]
click(b[-1]); time.sleep(6)
u = re.search(r'주소창 및 검색창, Value: (\S+)', tf.tree())
log(n, 'PUBLISHED' if u and re.search(r'todayz777/\d+|logNo=\d+', u.group(1)) else 'CHECK: 발행 clicked, address', u and u.group(1))
