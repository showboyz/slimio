# tblfix_pub.py <win> [--look] <NN:logNo>... : restyle the tables of already published posts (see tblfix.py).
# For each post: open it in the editor (PostUpdateForm), check the title against draft NN, style every table, open
# the 발행 panel and publish the edit only if every table was styled and the panel still says 전체공개 with tags.
# Otherwise it leaves the editor without saving. --look stops at the panel and saves its tree for a first look.
import glob, os, re, sys, time
import tblfix as tf
from tblfix_sched import go, leave_unsaved, log, wait_for, NAVER
tf.W = sys.argv[1]
args = sys.argv[2:]
LOOK = '--look' in args
for a in [a for a in args if a != '--look']:
    n, logno = a.split(':')
    draft = glob.glob(f'{NAVER}/{int(n):02d}-*.html')[0]
    title = re.search(r'제목: (.*)', open(draft).read()).group(1).strip()
    if not tf.guard(): log(n, 'STOP owner busy for 3 h'); break
    go(f'https://blog.naver.com/PostUpdateForm.naver?blogId=todayz777&logNo={logno}'); time.sleep(6)
    t = wait_for(r'버튼 발행', 30) or ''
    if '작성 중인 글이 있습니다' in t: tf.press(r'^버튼 취소$'); time.sleep(1.5); t = tf.tree()
    if title not in t.replace('\xa0', ' '): log(n, 'FAIL title did not load'); leave_unsaved(); continue
    log(n, os.path.basename(draft))
    try: k, ok = tf.fix(tf.W, draft)
    except SystemExit as e: log(n, 'FAIL', e); leave_unsaved(); continue
    if k == 0: log(n, 'no tables, left as it was'); leave_unsaved(); continue
    if ok != k: log(n, f'FAIL styled {ok}/{k}, left without saving'); leave_unsaved(); continue
    if not tf.guard(): log(n, 'STOP owner busy for 3 h (post left open)'); break
    tf.press(r'^버튼 발행$'); time.sleep(2)
    t = tf.tree()
    tags = re.findall(r'\d+ container (\S+)\n', t.split('태그 편집')[1].split('발행 시간')[0]) if '태그 편집' in t else []
    if LOOK: open(f'{NAVER}/../../.dev/panel-{n}.txt', 'w').write(t); log(n, 'LOOK panel saved, tags', len(tags)); tf.done(); break
    if not (re.search(r'전체공개, Value: 1', t) and tags): log(n, 'FAIL panel check, tags', len(tags)); leave_unsaved(); continue
    b = [l.split()[0] for l in t.splitlines() if re.match(r'\s*\d+ 버튼 발행$', l)]
    tf.sh('orca', 'computer', 'click', '--app', 'com.google.Chrome', '--window-id', tf.W, '--element-index', b[-1], '--no-screenshot')
    tf.done(); time.sleep(6)
    url = re.search(r'주소창 및 검색창, Value: (\S+)', tf.tree())
    log(n, f'SAVED {ok}/{k} tables, tags {len(tags)}', url.group(1) if url else '')
