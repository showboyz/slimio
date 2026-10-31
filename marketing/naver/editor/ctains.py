# ctains.py <win> <NN> <YYYY.MM.DD> <HH> : put the SlimIO button picture (banners.py) into the reserved post of draft NN,
# with the tool link on it, at the marketing/WRITING.md spot (tistory/cta.py plan): before the heading that ends the
# section first linking the tool (or before the first heading). One per post (owner, 2026-10-31: posts are short, keep
# room for ads). Saves with the schedule unchanged.
# How the caret gets there (2026-10-31): Chrome find (Cmd+F) for the start of the block that follows the spot, the
# orange match located in a screenshot (hl.cjs) and clicked, then Cmd+Left. Clicking a far-away element misses, closing
# the find bar doesn't move the editor's caret, and Alt+Up/Cmd+Down stop at component edges, so none of those are used.
# The picture just uploaded is clicked before its link is set (otherwise the toolbar's text link inserts the URL as
# text). The text blocks must be the same before and after; anything unexpected leaves the editor without saving.
import os, re, sys, time, json, subprocess
import tblfix as tf
from tblfix_sched import go, wait_for, leave_unsaved, log, drafts, EDITOR, NAVER
sys.path.insert(0, NAVER); sys.path.insert(0, os.path.join(NAVER, '../tistory'))
import cta, banners
tf.W = W = sys.argv[1]
n = int(sys.argv[2])
LIVE = sys.argv[3] == 'live'   # ctains.py <win> <NN> live <logNo> : a published post, edited through PostUpdateForm
date, hh = (None, None) if LIVE else (sys.argv[3], int(sys.argv[4]))
logno = sys.argv[4] if LIVE else None
draft = [f for f in os.listdir(NAVER) if re.match(rf'{n:02d}-.*\.html$', f)][0]
src = open(os.path.join(NAVER, draft)).read()
title = re.search(r'제목: (.*)', src).group(1).strip()

def fail(why): log(n, 'FAIL', why); leave_unsaved(); tf.done(); sys.exit(1)
def k(*a): tf.sh('bash', f'{tf.T}/k.sh', W, *a); tf.done()
UI = {'AI 활용 설정', '사진 설명을 입력하세요.', '링크', '추가할 컴포넌트를 선택하세요.', '도움말', '대표', ''}
def blocks(t):
    vals = [m.group(2).replace('\ufeff', '').strip() for m in re.finditer(r'^\s*\d+ (container, Text: |텍스트, Value: )(.*)$', t, re.M)]
    return [v for v in vals if v not in UI and not v.startswith('사진 컴포넌트') and '사진 설명을 입력하세요' not in v]   # picture UI

# where: the block after each spot, as the text Chrome find will look for
head, rows, main, url, a, end = cta.plan(src)
if main not in cta.TOOLS: sys.exit(f'{n}: no button copy for {main}')
first = banners.file(main)
def start_of(k):
    r = next(rows[j] for j in range(k, len(rows)) if rows[j].strip() and not rows[j].lstrip().startswith('<!--'))
    return ' '.join(tf.plain(r).split())[:24].strip()
spots = [(first, start_of(a + 1))]
bottom = start_of(end)   # the 출처 line: finding it scrolls the whole post into the editor's view
log(n, draft, main, url, [s for _, s in spots])

if not tf.guard(): log(n, 'STOP owner busy for 3 h'); sys.exit(2)
def clear_leftovers():   # a stopped run can leave the find bar open or Chrome's 'leave site?' over unsaved edits
    for _ in range(3):
        if tf.press(r'^버튼 검색 바 닫기$'): time.sleep(0.5)
        elif '사이트에서 나가시겠습니까' in tf.tree(): tf.press(r'^버튼 나가기$'); time.sleep(3)
        else: return
clear_leftovers()
def public():
    import urllib.request
    return urllib.request.urlopen(urllib.request.Request(f'https://blog.naver.com/PostView.naver?blogId=todayz777&logNo={logno}',
                                                         headers={'User-Agent': 'Mozilla/5.0'})).read().decode()
if LIVE:
    pub_date = re.search(r'se_publishDate[^>]*>([^<]*)', public()).group(1)
    go(f'https://blog.naver.com/PostUpdateForm.naver?blogId=todayz777&logNo={logno}'); tf.done(); time.sleep(3)
    clear_leftovers(); time.sleep(1)
    when = 'live ' + logno
else:
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
t = wait_for(rf'텍스트, Value: {re.escape(title)}', 20)
if not t: fail('post did not load')

def caret_before(text):
    subprocess.run('pbcopy', input=text, text=True)
    k('hotkey', '--key', 'CmdOrCtrl+F'); time.sleep(0.7)
    k('hotkey', '--key', 'CmdOrCtrl+V'); time.sleep(1.2)
    k('press-key', '--key', 'Return'); time.sleep(1.0)
    t, s = tf.state()
    m = re.search(r'전체 결과 (\d+)개 중 (\d+)개', t)
    closed = tf.press(r'^버튼 검색 바 닫기$'); time.sleep(0.6)
    pt = tf.match_point(s, tf.state()[1])
    if not (m and m.group(1) == '1' and closed and pt): fail(f'find {text!r}: {m and m.group(0)} closed={closed} point={pt}')
    k('click', '--x', str(pt[0]), '--y', str(pt[1])); time.sleep(0.5)
    k('hotkey', '--key', 'CmdOrCtrl+Left'); time.sleep(0.4)

# the editor draws the lower part only once it has been scrolled to: find the last spot first, then take the blocks
subprocess.run('pbcopy', input=bottom, text=True)
k('hotkey', '--key', 'CmdOrCtrl+F'); time.sleep(0.7); k('hotkey', '--key', 'CmdOrCtrl+V'); time.sleep(1.2)
k('press-key', '--key', 'Return'); time.sleep(1.5); tf.press(r'^버튼 검색 바 닫기$'); time.sleep(1)
t = tf.tree()
# after a reload the editor no longer shows picture file names; but no post had a picture link before the buttons
if re.search(r'텍스트, Value: 링크$', t, re.M): log(n, 'already has buttons'); leave_unsaved(); tf.done(); sys.exit(0)
before = blocks(t)
for path, nxt in spots:
    name = os.path.basename(path)
    if not tf.guard(): log(n, 'STOP owner busy for 3 h (post left open, not saved)'); sys.exit(2)
    caret_before(nxt)
    tf.sh('bash', f'{tf.T}/img.sh', W, path); tf.done(); time.sleep(2)
    t = tf.tree(); seq = [l.strip() for l in t.splitlines() if re.search(r'^\s*\d+ (container, Text: |텍스트, Value: |이미지 )', l)
                          and not any(l.strip().endswith(u) for u in ('AI 활용 설정', '사진 설명을 입력하세요.', ', Value: 링크'))]
    i = next((j for j, l in enumerate(seq) if l.endswith('이미지 ' + name)), None)
    flat = lambda x: re.sub(r'\s+', '', x)   # the tree puts spaces around bold words
    nb = re.sub(r'^\d+ (container, Text: |텍스트, Value: )', '', seq[i + 1]) if i is not None and i + 1 < len(seq) else ''
    if i is None or not flat(nb).startswith(flat(nxt)): fail(f'{name} is not right before {nxt!r}: {nb[:40]!r}')   # else a split
    # select the picture itself, then its own link field
    e = tf.idx(t, rf'^이미지 {re.escape(name)}$')
    tf.sh('python3', f'{tf.T}/c.py', W, '-', 'click', '--element-index', e); tf.done(); time.sleep(0.8)
    if not tf.idx(tf.tree(), r'^버튼 사진 교체$'): fail(f'{name} not selected')
    if not tf.press(r'^팝업 버튼 링크 입력 열기$'): fail('image link button')
    time.sleep(0.8)
    subprocess.run('pbcopy', input=url, text=True)
    f = tf.idx(tf.tree(), r'^url \(settable\)')
    if not f: fail('image link field')
    k('click', '--element-index', f); time.sleep(0.3); k('hotkey', '--key', 'CmdOrCtrl+V'); time.sleep(0.6)
    v = re.search(r'url \(settable\), Value: ([^,\s]+)', tf.tree())
    if not v or v.group(1) != url: fail(f'link field shows {v and v.group(1)}')
    tf.press(r'^버튼 링크 입력$'); time.sleep(1.2)
    t = tf.tree(); rs = t.splitlines(); j = next(x for x, l in enumerate(rs) if l.strip().endswith('이미지 ' + name))
    if not any(re.search(r'텍스트, Value: 링크$', l) for l in rs[j:j + 30]): fail(f'{name}: no link badge')
    log(n, name, 'in and linked')

after = blocks(tf.tree())
# the tree groups the same paragraphs differently once a picture is in (one container or three, long ones cut with
# '...'), so blocks can't be compared one to one. What can go wrong is a split paragraph (checked above, at each
# picture) or the link pasted as text: the text must mention pdfslimio as often as before, and no block may be a URL.
jb, ja = ''.join(before), ''.join(after)
if ja.count('pdfslimio') != jb.count('pdfslimio') or any(b.startswith('http') for b in after):
    fail(f"link text appeared in the post: pdfslimio {jb.count('pdfslimio')} -> {ja.count('pdfslimio')}")
if not tf.guard(): log(n, 'STOP owner busy for 3 h (post left open, not saved)'); sys.exit(2)
tf.press(r'^버튼 발행$'); time.sleep(2)
t = tf.tree()
tags = re.findall(r'\d+ container (\S+)\n', t.split('태그 편집')[1].split('발행 시간')[0]) if '태그 편집' in t else []
if LIVE:   # a published post offers only '현재' and keeps its date
    ok = re.search(r'라디오 버튼 \(settable\) 현재, Value: 1', t) and re.search(r'전체공개, Value: 1', t) and len(tags) >= 1   # #01 has 11
else:
    y, mo, d = date.split('.')
    ok = (re.search(r'라디오 버튼 \(settable\) 예약, Value: 1', t) and f'Value: {y}. {mo}. {d}' in t
          and re.search(rf'시간 선택, Value: {hh:02d}', t) and re.search(r'분 선택, Value: 00', t)
          and re.search(r'전체공개, Value: 1', t) and len(tags) == 10)
if not ok: fail(f'panel check, tags {len(tags)}')
b = [l.split()[0] for l in t.splitlines() if re.match(r'\s*\d+ 버튼 발행$', l)]
tf.sh('orca', 'computer', 'click', '--app', 'com.google.Chrome', '--window-id', W, '--element-index', b[-1], '--no-screenshot')
tf.done(); time.sleep(5)
home = re.search(r'주소창 및 검색창, Value: blog\.naver\.com/todayz777' + (rf'/{logno}' if LIVE else '') + r'(,|$|\?)', tf.tree(), re.M)
if LIVE:   # the public post: one picture link to the tool, same date
    time.sleep(3); page = public()
    imgl = len(re.findall(r'data-linktype="img"[^>]*pdfslimio|pdfslimio[^"]*"[^>]*data-linktype="img"', page))
    nd = re.search(r'se_publishDate[^>]*>([^<]*)', page).group(1)
    log(n, f'public page: picture links {imgl}, date {nd} (was {pub_date})' + ('' if imgl == 1 and nd == pub_date else '  CHECK'))
    home = imgl == 1 and nd == pub_date   # after an edit Naver shows PostView, not the blog home
log(n, 'SAVED' if home else 'CHECK: 발행 clicked but did not return to the blog home', when)
