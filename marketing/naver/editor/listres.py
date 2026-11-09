# listres.py <win> <out> : open the editor's '예약 발행 N 건' list in my window, save each item as "time<TAB>title<TAB>draft NN",
# then leave the editor without saving (nothing is opened or changed)
import os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tblfix as tf
from tblfix_sched import go, wait_for, leave_unsaved, EDITOR, NAVER
tf.W = sys.argv[1]; out = sys.argv[2]
drafts = {}
for f in os.listdir(NAVER):
    m = re.match(r'(\d+)-.*\.html$', f)
    if m:
        t = re.search(r'제목: (.*)', open(os.path.join(NAVER, f)).read())
        if t: drafts[t.group(1).strip()] = m.group(1)
if not tf.guard(): print('STOP owner busy'); sys.exit(2)
go(EDITOR); tf.done(); time.sleep(3)
t = wait_for(r'예약 발행 \d+ 건', 30) or ''
if not t: print('editor did not open'); leave_unsaved(); tf.done(); sys.exit(1)
if '작성 중인 글이 있습니다' in t: tf.press(r'^버튼 취소$'); time.sleep(1.5)
tf.press(r'^버튼 예약 발행 \d+ 건'); time.sleep(2)
rows = []
for l in tf.tree().splitlines():
    m = re.match(r'\s*\d+ 버튼 (.*) (\d{4}\.\d\d\.\d\d \d\d:\d\d)$', l)
    if m: rows.append(f'{m.group(2)}\t{m.group(1).strip()}\t{drafts.get(m.group(1).strip(), "?")}')
open(out, 'w').write('\n'.join(sorted(rows)) + '\n')
print(len(rows), 'items')
leave_unsaved(); tf.done()
