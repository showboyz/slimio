# newpost.py <win> <NN> <YYYY-MM-DD> <HH> <chunkdir> : post draft NN as a new post scheduled for that date at HH:00.
# Reads the title, tags and images from the draft, builds the paste chunks (chunk.py), opens a new post in the editor,
# pastes it (post.sh), sets tall or '작게' images small (small.sh), checks that the title, every image and the last
# paragraph made it in, then schedules it with the tags (finish.sh, which checks the panel before 발행).
# Anything that fails leaves the editor without saving.
import glob, os, re, subprocess, sys, time
import tblfix as tf
from tblfix_sched import go, wait_for, leave_unsaved, log, NAVER, EDITOR
tf.W = W = sys.argv[1]
n, date, hh, nb = sys.argv[2:6]
draft = glob.glob(f'{NAVER}/{int(n):02d}-*.html')[0]
src = open(draft).read()
title = re.search(r'제목: (.*)', src).group(1).strip()
tags = [t.strip() for t in re.search(r'태그: (.*)', src).group(1).split(',')]
imgs = re.findall(r'<!--IMG:(.*?)-->', src)
desc = re.search(r'이미지: (.*)', src).group(1)
IMG = os.path.normpath(f'{NAVER}/../../public/img/blog')
def tall(i):
    o = tf.sh('sips', '-g', 'pixelWidth', '-g', 'pixelHeight', f'{IMG}/{i}').stdout
    w, h = (int(x) for x in re.findall(r'pixel\w+: (\d+)', o))
    return h / w >= 2
small = [i for i in imgs[1:] if re.search(re.escape(i) + r"\([^)]*작게", desc) or tall(i)]
last = tf.plain(re.findall(r'<p>(.*?)</p>', src, flags=re.S)[-1])[:40]

def fail(why): log(n, 'FAIL', why); leave_unsaved(); tf.done(); sys.exit(1)
if len(tags) != 10: sys.exit(f'{n}: {len(tags)} tags')
tf.sh('python3', f'{tf.T}/chunk.py', draft, nb)
if len(glob.glob(f'{nb}/c*.html')) != len(imgs): sys.exit(f'{n}: chunks do not match images')
if not tf.guard(): log(n, 'STOP owner busy for 3 h'); sys.exit(2)
go(EDITOR); tf.done(); time.sleep(5)
t = wait_for(r'예약 발행 \d+ 건', 30) or ''
if '작성 중인 글이 있습니다' in t: tf.press(r'^버튼 취소$'); time.sleep(1.5)
if tf.press(r'^버튼 도움말 닫기$'): time.sleep(0.8)
t = tf.tree()
if not re.search(r'제목', t) or re.search(r'이미지 \S+\.jpg', t): fail('editor is not an empty new post')
log(n, os.path.basename(draft), 'small', small)
if not tf.guard(): log(n, 'STOP owner busy for 3 h (empty editor left open)'); sys.exit(2)
r = tf.sh('bash', f'{tf.T}/post.sh', W, nb, title, small[0] if small else '-', *imgs); tf.done()
print(r.stdout[-600:], r.stderr[-300:], flush=True)
for i in small[1:]: tf.sh('bash', f'{tf.T}/small.sh', W, i); tf.done()
t = tf.tree().replace('\xa0', ' ')
missing = [i for i in imgs if f'이미지 {i}' not in t]
if title not in t: fail('title missing')
if missing: fail(f'images missing {missing}')
if last not in t: fail(f'last paragraph missing {last!r}')
log(n, 'pasted, shot', tf.shot())
if not tf.guard(): log(n, 'STOP owner busy for 3 h (post left open, not saved)'); sys.exit(2)
r = tf.sh('bash', f'{tf.T}/finish.sh', W, date, hh, *tags); tf.done()
print(r.stdout[-800:], r.stderr[-300:], flush=True)
if 'CHECK OK' not in r.stdout: fail('finish.sh panel check')
home = re.search(r'주소창 및 검색창, Value: blog\.naver\.com/todayz777(,|$)', tf.tree(), re.M)
log(n, f'SCHEDULED {date} {hh}:00' if home else 'CHECK: 발행 clicked but did not return to the blog home')
