# preview.py <win> <NN|draft.html> <chunkdir> <outdir> [screens] : paste draft NN (or a test draft) into a new post the
# way newpost.py does (chunk.py, post.sh), scroll the editor from the top one page at a time saving [screens] (default 6)
# screenshots to <outdir>, then leave the editor without saving. For checking a paste format before it goes into real
# posts; nothing is published.
import glob, os, re, shutil, sys, time
import tblfix as tf
from tblfix_sched import go, wait_for, leave_unsaved, log, close_bubble, NAVER, EDITOR
tf.W = W = sys.argv[1]
n, nb, outdir = sys.argv[2:5]; screens = int(sys.argv[5]) if len(sys.argv) > 5 else 6
draft = n if n.endswith('.html') else glob.glob(f'{NAVER}/{int(n):02d}-*.html')[0]   # or a test draft's path
src = open(draft).read()
title = re.search(r'제목: (.*)', src).group(1).strip()
imgs = re.findall(r'<!--IMG:(.*?)-->', src)
tf.sh('python3', f'{tf.T}/chunk.py', draft, nb)
os.makedirs(outdir, exist_ok=True)
if not tf.guard(): log(n, 'STOP owner busy for 3 h'); sys.exit(2)
go(EDITOR); tf.done(); time.sleep(5)
t = wait_for(r'예약 발행 \d+ 건', 30) or ''
if '작성 중인 글이 있습니다' in t: tf.press(r'^버튼 취소$'); time.sleep(1.5)
if tf.press(r'^버튼 도움말 닫기$'): time.sleep(0.8)
close_bubble()
t = tf.tree()
if not re.search(r'제목', t) or re.search(r'이미지 \S+\.jpg', t): log(n, 'FAIL editor is not an empty new post'); leave_unsaved(); sys.exit(1)
if not tf.guard(): log(n, 'STOP owner busy for 3 h (empty editor left open)'); leave_unsaved(); sys.exit(2)
r = tf.sh('bash', f'{tf.T}/post.sh', W, nb, title, '-', *imgs); tf.done()
print(r.stdout[-300:], r.stderr[-300:], flush=True)
for _ in range(12): tf.k('scroll', '--x', '1050', '--y', '700', '--direction', 'up', '--pages', '10'); time.sleep(0.3)
time.sleep(1)
for i in range(1, screens + 1):
    shutil.copy(tf.shot(), f'{outdir}/p{i}.png')
    tf.k('scroll', '--x', '1050', '--y', '700', '--direction', 'down', '--pages', '1'); time.sleep(1)
log(n, 'preview saved', outdir)
leave_unsaved(); tf.done()
