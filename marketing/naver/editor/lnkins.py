# lnkins.py <win> <NN> <logNo> <next-block-text> <para.html> : put one new paragraph (an HTML <p> with a link in it)
# into the published post <logNo> of draft NN, right before the block that starts with <next-block-text>, and save it
# with its date unchanged. Added 2026-11-02 to link the most-read post (#01) to the newer post that answers part of
# its readers' problem (owner: grow the post that does well).
# The caret is put at the start of the next block the way ctains.py does it (Chrome find, click on the orange match,
# Cmd+Left), then Return opens an empty line above and Up moves into it, and the paragraph is pasted as HTML (setclip.js,
# like post.sh). Every old text block must still be there, the new paragraph must be its own block right before the
# next one, and the public page must show the link once with the same date; anything else leaves without saving.
import os, re, sys, time, subprocess
import tblfix as tf
from tblfix_sched import go, wait_for, leave_unsaved, log, NAVER
tf.W = W = sys.argv[1]
n, logno, nxt, para = int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
draft = [f for f in os.listdir(NAVER) if re.match(rf'{n:02d}-.*\.html$', f)][0]
src = open(os.path.join(NAVER, draft)).read()
title = re.search(r'제목: (.*)', src).group(1).strip()
html = open(para).read().strip()
href = re.search(r'href="([^"]+)"', html).group(1)
new = tf.plain(html)
flat = lambda x: re.sub(r'\s+', '', x.replace('﻿', ''))   # the tree puts spaces around bold words and links

def fail(why): log(n, 'FAIL', why); leave_unsaved(); tf.done(); sys.exit(1)
def k(*a): tf.sh('bash', f'{tf.T}/k.sh', W, *a); tf.done()
UI = {'AI 활용 설정', '사진 설명을 입력하세요.', '링크', '추가할 컴포넌트를 선택하세요.', '도움말', '대표', '줄 끝', ''}
def blocks(t):
    vals = [m.group(2).replace('﻿', '').strip() for m in re.finditer(r'^\s*\d+ (container, Text: |텍스트, Value: )(.*)$', t, re.M)]
    return [v for v in vals if v not in UI and not v.startswith('사진 컴포넌트') and '사진 설명을 입력하세요' not in v]
def public():
    import urllib.request
    return urllib.request.urlopen(urllib.request.Request(f'https://blog.naver.com/PostView.naver?blogId=todayz777&logNo={logno}',
                                                         headers={'User-Agent': 'Mozilla/5.0'})).read().decode()
def find(text):
    subprocess.run('pbcopy', input=text, text=True)
    k('hotkey', '--key', 'CmdOrCtrl+F'); time.sleep(0.7)
    k('hotkey', '--key', 'CmdOrCtrl+V'); time.sleep(1.2)
    k('press-key', '--key', 'Return'); time.sleep(1.0)

page = public()
pub_date = re.search(r'se_publishDate[^>]*>([^<]*)', page).group(1)
had = page.count(href)
if had: log(n, f'the post already links {href} ({had})'); sys.exit(0)
bottom = ' '.join(tf.plain(re.findall(r'<p>(.*?)</p>', src, flags=re.S)[-1]).split())[:24]
log(n, draft, 'before', repr(nxt), 'new', repr(new[:40]), 'date', pub_date)

if not tf.guard(): log(n, 'STOP owner busy for 3 h'); sys.exit(2)
for _ in range(3):   # leftovers of a stopped run: the find bar, or Chrome's 'leave site?' over unsaved edits
    if tf.press(r'^버튼 검색 바 닫기$'): time.sleep(0.5)
    elif '사이트에서 나가시겠습니까' in tf.tree(): tf.press(r'^버튼 나가기$'); time.sleep(3)
    else: break
go(f'https://blog.naver.com/PostUpdateForm.naver?blogId=todayz777&logNo={logno}'); tf.done(); time.sleep(3)
if not wait_for(rf'텍스트, Value: {re.escape(title)}', 20): fail('post did not load')
find(bottom); time.sleep(0.5); tf.press(r'^버튼 검색 바 닫기$'); time.sleep(1)   # draws the whole post
if sum(flat(b).startswith(flat(nxt)) for b in blocks(tf.tree())) != 1: fail(f'{nxt!r} is not one block')

# caret at the start of the next block
find(nxt)
t, s = tf.state()
m = re.search(r'전체 결과 (\d+)개 중 (\d+)개', t)
closed = tf.press(r'^버튼 검색 바 닫기$'); time.sleep(0.6)
pt = tf.match_point(s, tf.state()[1])
if not (m and m.group(1) == '1' and closed and pt): fail(f'find {nxt!r}: {m and m.group(0)} closed={closed} point={pt}')
k('click', '--x', str(pt[0]), '--y', str(pt[1])); time.sleep(0.5)
k('hotkey', '--key', 'CmdOrCtrl+Left'); time.sleep(0.4)
# compared at this scroll spot: blocks far above it (the first table) drop out of the tree once it is scrolled away
before = blocks(tf.tree())
if not tf.guard(): log(n, 'STOP owner busy for 3 h (post left open, not saved)'); sys.exit(2)
k('press-key', '--key', 'Return'); time.sleep(0.6)
k('press-key', '--key', 'Up'); time.sleep(0.4)
d = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'lnkins'); os.makedirs(d, exist_ok=True)
open(f'{d}/p.html', 'w').write(html); open(f'{d}/p.txt', 'w').write(new)
tf.sh('osascript', '-l', 'JavaScript', f'{tf.T}/setclip.js', f'{d}/p.html', f'{d}/p.txt')
k('hotkey', '--key', 'CmdOrCtrl+V'); time.sleep(2)

after = blocks(tf.tree())
i = next((j for j, b in enumerate(after) if flat(b) == flat(new)), None)
if i is None: fail('the new paragraph is not a block of its own: ' + repr([b[:30] for b in after if flat(new)[:12] in flat(b)]))
if i + 1 >= len(after) or not flat(after[i + 1]).startswith(flat(nxt)): fail(f'next block is {after[i + 1][:30] if i + 1 < len(after) else None!r}')
# the ten blocks on each side must be the same as before (further away the tree may have dropped or added blocks
# because the paste moved the page a little)
bi = next(j for j, b in enumerate(before) if flat(b).startswith(flat(nxt)))
w1, w2 = min(10, bi, i), min(10, len(before) - bi, len(after) - i - 1)
if min(w1, w2) < 3: fail(f'too few blocks around it to compare ({w1} above, {w2} below)')
if [flat(b) for b in before[bi - w1:bi + w2]] != [flat(b) for b in after[i - w1:i] + after[i + 1:i + 1 + w2]]:
    fail(f'blocks around it changed: {[b[:20] for b in before[bi - w1:bi + w2]]} -> {[b[:20] for b in after[i - w1:i + 1 + w2]]}')
log(n, f'{w1} blocks above and {w2} below unchanged')
log(n, 'pasted', tf.shot())

if not tf.guard(): log(n, 'STOP owner busy for 3 h (post left open, not saved)'); sys.exit(2)
tf.press(r'^버튼 발행$'); time.sleep(2)
t = tf.tree()
if not (re.search(r'라디오 버튼 \(settable\) 현재, Value: 1', t) and re.search(r'전체공개, Value: 1', t)): fail('panel check')
b = [l.split()[0] for l in t.splitlines() if re.match(r'\s*\d+ 버튼 발행$', l)]
tf.sh('orca', 'computer', 'click', '--app', 'com.google.Chrome', '--window-id', W, '--element-index', b[-1], '--no-screenshot')
tf.done(); time.sleep(8)
page = public()
nd = re.search(r'se_publishDate[^>]*>([^<]*)', page).group(1)
ok = page.count(href) >= 1 and nd == pub_date and flat(new)[:20] in flat(tf.plain(page))
log(n, f'public page: link {page.count(href)}, date {nd} (was {pub_date})', 'SAVED' if ok else 'CHECK')
