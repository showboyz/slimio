# repaste.py <win> <NN> <YYYY.MM.DD> <HH> <chunkdir> : paste the reserved post of draft NN again in chunk.py's current
# layout (2026-11-15 readability: blank lines, short paragraphs, heading boxes) and save it with its schedule unchanged.
# With the date 'test' it pastes the draft into a NEW post first, runs the same steps and leaves without saving;
# REPASTE_DRY=1 does every step on the real reserved post except the save.
# Opens the post from the 예약 발행 list as ctaoff.py does. Emptying the body: Cmd+A selects only one block, and from the
# title no key moves the caret into the body, so Chrome find on the draft's last paragraph brings it into view, a click
# on the orange match (hl.cjs) puts the caret there, Cmd+Down takes it towards the end, and rounds of Shift+Up x60 +
# Backspace and Shift+Down x60 + Delete run until the editor shows its empty-body placeholder; Shift+Up stops at the
# top of the body, so the title stays (tested in new posts 2026-11-15). Then the body goes in as in newpost.py (post.sh
# with title '-', since Cmd+A in the title does not reliably select it), with the same checks, and it saves only if the
# 발행 panel still shows 예약 · that date and hour · :00 · 전체공개 · 10 tags. Posts reserved before 2026-11-10 lose their SlimIO button picture too, as the drafts have none.
# Anything unexpected leaves the editor without saving, so the reserved post stays as it was.
import glob, os, re, subprocess, sys, time
import tblfix as tf
from tblfix_sched import go, wait_for, leave_unsaved, log, close_bubble, NAVER, EDITOR
tf.W = W = sys.argv[1]
n, date, hh, nb = int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
test = date == 'test'
dry = os.environ.get('REPASTE_DRY') == '1'   # a real reserved post, every step but the save
draft = glob.glob(f'{NAVER}/{n:02d}-*.html')[0]
src = open(draft).read()
title = re.search(r'제목: (.*)', src).group(1).strip()
imgs = re.findall(r'<!--IMG:(.*?)-->', src)
last = tf.plain(re.findall(r'<p>(.*?)</p>', src, flags=re.S)[-1])[:40]
EMPTY = '글감과 함께 나의 일상을'   # the empty body's placeholder

def fail(why):   # the tree at the moment of failure goes to $TMPDIR/repaste_<NN>.txt
    log(n, 'FAIL', why); open(os.path.join(os.environ.get('TMPDIR', '/tmp'), f'repaste_{n}.txt'), 'w').write(tf.tree())
    leave_unsaved(); tf.done(); sys.exit(1)
def fast(*a):   # straight to orca, without k.sh's front-window check on every key (each round starts with one tf.k)
    tf.sh('orca', 'computer', *a, '--app', 'com.google.Chrome', '--window-id', W, '--no-screenshot'); time.sleep(0.12)
def copied_body():   # as in newpost.py: the tree cuts long text components, the clipboard does not
    tf.k('hotkey', '--key', 'CmdOrCtrl+A'); time.sleep(0.5); tf.k('hotkey', '--key', 'CmdOrCtrl+C'); time.sleep(0.8)
    tf.k('press-key', '--key', 'Right'); time.sleep(0.5)
    return tf.sh('pbpaste').stdout.replace('\xa0', ' ')
def click_on(probe):   # Chrome find brings the text into view; a click on the orange match (hl.cjs) puts the caret in it
    subprocess.run('pbcopy', input=probe, text=True)
    before = tf.windows()
    tf.k('hotkey', '--key', 'CmdOrCtrl+F'); time.sleep(0.7); tf.k('hotkey', '--key', 'CmdOrCtrl+V'); time.sleep(1.2)
    tf.k('press-key', '--key', 'Return'); time.sleep(1.0)
    t, s = tf.state()
    m = re.search(r'전체 결과 (\d+)개 중 (\d+)개', t)
    if not tf.close_find(before): fail('find bar did not close')
    pt = tf.match_point(s, tf.state()[1])
    if not (m and m.group(1) == '1' and pt): fail(f'find {probe!r}: {m and m.group(0)} point={pt}')
    tf.k('click', '--x', str(pt[0]), '--y', str(pt[1])); time.sleep(0.5)
def caret_at_end():
    click_on(' '.join(last.split())[:16])
    tf.k('hotkey', '--key', 'CmdOrCtrl+Down'); time.sleep(0.5)
def bold_kept():   # the caret in a bold phrase of the last part shows '굵기 해제'; True when no phrase there is usable
    body = title + '\n' + tf.plain(re.sub(r'^<!--.*?-->', '', src, flags=re.S))
    for b in reversed([tf.plain(x) for x in re.findall(r'<b>(.*?)</b>', src.split('<!--IMG:')[-1], flags=re.S)]):
        if len(b) >= 6 and body.count(b) == 1:
            click_on(b[:16]); return bool(tf.idx(tf.tree(), r'^버튼 굵기 해제$'))
    return True
def clear_body():
    # upwards first; the caret can land a line or two above the very end (2026-11-15 test: the rest of the last
    # paragraph stayed below it), so each round also selects downwards and deletes that
    for _ in range(10):
        for key, rm in (('Shift+Up', 'Backspace'), ('Shift+Down', 'Delete')):
            tf.k('hotkey', '--key', key)
            for _ in range(59): fast('hotkey', '--key', key)
            fast('press-key', '--key', rm); time.sleep(1.5); tf.done()
            if EMPTY in tf.tree(): return True
    return False

def plain_caret():
    # the emptied body can keep the deleted text's bold at the caret, and pasting into it then lost every bold in the post
    # (2026-11-15 test), so each text style shown as '… 해제' (on) is switched off before pasting
    tf.k('click', '--x', '823', '--y', '453'); time.sleep(0.5)
    for name in ('굵기', '기울이기', '밑줄', '취소선'):
        if tf.press(rf'^버튼 {name} 해제$'): time.sleep(0.3)
    if re.search(r'버튼 (굵기|기울이기|밑줄|취소선) 해제', tf.tree()): fail('a text style is still on at the caret')

tf.sh('python3', f'{tf.T}/chunk.py', draft, nb)
if len(glob.glob(f'{nb}/c*.html')) != len(imgs): sys.exit(f'{n}: chunks do not match images')
if not tf.guard(): log(n, 'STOP owner busy for 3 h'); sys.exit(2)
go(EDITOR); tf.done(); time.sleep(5)
t = wait_for(r'예약 발행 \d+ 건', 30) or ''
if not t: fail('editor did not open')
if '작성 중인 글이 있습니다' in t: tf.press(r'^버튼 취소$'); time.sleep(1.5)
if tf.press(r'^버튼 도움말 닫기$'): time.sleep(0.8)
close_bubble()
if test:
    tf.sh('bash', f'{tf.T}/post.sh', W, nb, title, '-', *imgs); tf.done()
    when = 'test'
else:
    hh = int(hh)
    tf.press(r'^버튼 예약 발행 \d+ 건'); time.sleep(1.5)
    when = f'{date} {hh:02d}:00'
    item = [l for l in tf.tree().splitlines() if re.search(rf'\d+ 버튼 .* {re.escape(when)}$', l)]
    if len(item) != 1: fail(f'list item {len(item)}')
    if re.match(rf'\s*\d+ 버튼 (.*) {re.escape(when)}$', item[0]).group(1).strip() != title: fail('the post at that time is not draft ' + draft)
    tf.press(rf'^버튼 .* {re.escape(when)}$'); time.sleep(5)
    if not wait_for(rf'텍스트, Value: {re.escape(title)}', 20): fail('post did not load')

if not tf.guard(): log(n, 'STOP owner busy for 3 h (post left open, not saved)'); leave_unsaved(); sys.exit(2)
caret_at_end()
t0 = time.time()
if not clear_body(): fail('body not empty after 10 rounds')
t = tf.tree().replace('\xa0', ' ')
if f'Value: {title}' not in t: fail('title changed while emptying the body')
log(n, f'body emptied in {time.time() - t0:.0f}s')
plain_caret()
r = tf.sh('bash', f'{tf.T}/post.sh', W, nb, '-', '-', *imgs); tf.done()   # the title stays as it is
print(r.stdout[-600:], r.stderr[-300:], flush=True)
t = tf.tree().replace('\xa0', ' ')
missing = [i for i in imgs if f'이미지 {i}' not in t]
if t.count(f'Value: {title}') != 1: fail(f'title {t.count(f"Value: {title}")} times')
if missing: fail(f'images missing {missing}')
if last not in t and last not in copied_body(): fail(f'last paragraph missing {last!r}')
if not bold_kept(): fail('bold text lost in the paste')
log(n, 'pasted, shot', tf.shot())
if test or dry:   # screens from the top down to $TMPDIR/repaste_<NN>_p<i>.png, then leave without saving
    for _ in range(12): tf.k('scroll', '--x', '1050', '--y', '700', '--direction', 'up', '--pages', '10'); time.sleep(0.3)
    for i in range(1, 9):
        subprocess.run(['cp', tf.shot(), os.path.join(os.environ.get('TMPDIR', '/tmp'), f'repaste_{n}_p{i}.png')])
        tf.k('scroll', '--x', '1050', '--y', '700', '--direction', 'down', '--pages', '1'); time.sleep(1)
    log(n, 'TEST OK, leaving without saving'); leave_unsaved(); tf.done(); sys.exit(0)

if not tf.guard(): log(n, 'STOP owner busy for 3 h (post left open, not saved)'); leave_unsaved(); sys.exit(2)
tf.press(r'^버튼 발행$'); time.sleep(2)
t = tf.tree(); y, mo, dd = date.split('.')
tags = re.findall(r'\d+ container (\S+)\n', t.split('태그 편집')[1].split('발행 시간')[0]) if '태그 편집' in t else []
ok = (re.search(r'라디오 버튼 \(settable\) 예약, Value: 1', t) and f'Value: {y}. {mo}. {dd}' in t
      and re.search(rf'시간 선택, Value: {hh:02d}', t) and re.search(r'분 선택, Value: 00', t)
      and re.search(r'전체공개, Value: 1', t) and len(tags) == 10)
if not ok: fail(f'panel check, tags {len(tags)}')
b = [l.split()[0] for l in t.splitlines() if re.match(r'\s*\d+ 버튼 발행$', l)]
tf.sh('orca', 'computer', 'click', '--app', 'com.google.Chrome', '--window-id', W, '--element-index', b[-1], '--no-screenshot')
tf.done(); time.sleep(5)
home = re.search(r'주소창 및 검색창, Value: blog\.naver\.com/todayz777(,|$)', tf.tree(), re.M)
log(n, 'SAVED' if home else 'CHECK: 발행 clicked but did not return to the blog home', when)
