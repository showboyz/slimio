# ctaoff.py <win> <NN> <YYYY.MM.DD> <HH> : take the SlimIO button picture (ctains.py) out of the reserved post of draft NN
# and save with the schedule unchanged; the text links stay. Since 2026-11-01 no post published with the button has
# shown up in Naver search (HANDOFF 2-58), so a few posts go out without it to see whether they get indexed.
# The button is the only linked picture, right before the block that follows the cta.plan spot: find the 출처 block
# (Chrome find scrolls the whole post into the editor's view), check there is exactly one link badge and it sits
# right before that block, select the picture, press its own 삭제, check no badge is left and that block now follows
# text (or, when the editor joins the text around the picture into one block, that Chrome find still sees it once).
# Anything unexpected leaves the editor without saving.
import os, re, sys, time, subprocess
import tblfix as tf
from tblfix_sched import go, wait_for, leave_unsaved, log, EDITOR, NAVER
sys.path.insert(0, os.path.join(NAVER, '../tistory'))
import cta
tf.W = W = sys.argv[1]
n, date, hh = int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
draft = [f for f in os.listdir(NAVER) if re.match(rf'{n:02d}-.*\.html$', f)][0]
src = open(os.path.join(NAVER, draft)).read()
title = re.search(r'제목: (.*)', src).group(1).strip()

def fail(why):   # the tree at the moment of failure goes to $TMPDIR/ctaoff_<NN>.txt
    log(n, 'FAIL', why); open(os.path.join(os.environ.get('TMPDIR', '/tmp'), f'ctaoff_{n}.txt'), 'w').write(tf.tree())
    leave_unsaved(); tf.done(); sys.exit(1)
def k(*a): tf.sh('bash', f'{tf.T}/k.sh', W, *a); tf.done()
flat = lambda x: re.sub(r'\s+', '', x)
head, rows, main, url, a, end = cta.plan(src)
def start_of(j):
    r = next(rows[i] for i in range(j, len(rows)) if rows[i].strip() and not rows[i].lstrip().startswith('<!--'))
    return ' '.join(tf.plain(r).split())[:24].strip()
nxt, bottom = start_of(a + 1), start_of(end)
def text_before(j):   # the last text block above the button spot, or '' when a picture comes first
    for i in range(j, -1, -1):
        r = rows[i].strip()
        if r.startswith('<!--IMG'): return ''
        if not r or r.startswith('<!--'): continue
        p = ' '.join(tf.plain(r).split())[:24].strip()
        if p: return p
    return ''
prv = text_before(a)
log(n, draft, 'button before', repr(nxt))
def find(s):   # Chrome find, which also scrolls the match into view; returns the number of matches
    subprocess.run('pbcopy', input=s, text=True)
    before = tf.windows()
    k('hotkey', '--key', 'CmdOrCtrl+F'); time.sleep(0.7); k('hotkey', '--key', 'CmdOrCtrl+V'); time.sleep(1.2)
    k('press-key', '--key', 'Return'); time.sleep(1.5)
    m = re.search(r'전체 결과 (\d+)개 중 (\d+)개', tf.tree())
    if not tf.close_find(before): fail('find bar did not close')
    time.sleep(1)
    return int(m.group(1)) if m else None

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

c = find(bottom)
if c != 1: fail(f'find {bottom!r}: {c} matches')
# then find the block after the button, so the button is on screen: a click on an element scrolled out of view lands
# on whatever is drawn there (on #50 it selected the experiment photo further down)
c = find(nxt)
if c != 1: fail(f'find {nxt!r}: {c} matches')
# near the end of a post that leaves the block after the button at the top of the editor, with the button hidden under
# the toolbar (#54 on 11/10): find the text block above the button too, so Chrome brings it and the button into view.
# Chrome only scrolls when the match is off screen, so this does nothing when both are already visible.
if prv:
    c = find(prv)
    if c != 1: log(n, f'find {prv!r}: {c} matches, not used'); find(nxt)

def layout():
    # (element, kind, text) for linked pictures and text blocks, in tree order. After a reload a picture is only a bare
    # 'container' line with its '텍스트, Value: 링크' badge inside, so a badge stands for its picture (the line above it).
    out, prev = [], None
    for l in tf.tree().splitlines():
        mm = re.match(r'\s*(\d+) (.*)$', l)
        if not mm: continue
        i, rest = mm.group(1), mm.group(2)
        if rest == '텍스트, Value: 링크': out.append((prev, 'pic', ''))
        else:
            m2 = re.match(r'(텍스트, Value: |container, Text: )(.*)$', rest)
            val = m2.group(2).replace('﻿', '').strip() if m2 else ''
            if m2 and val and val not in ('AI 활용 설정', '사진 설명을 입력하세요.', '추가할 컴포넌트를 선택하세요.', '도움말', '대표') \
                    and not val.startswith('사진 컴포넌트') and '사진 설명을 입력하세요' not in val:
                out.append((i, 'text', val))
        prev = i if rest == 'container' else prev
    return out
at = lambda L: next((i for i, x in enumerate(L) if x[1] == 'text' and flat(x[2]).startswith(flat(nxt))), None)
L = layout()
links = sum(1 for x in L if x[1] == 'pic')
j = at(L)
if links != 1: fail(f'{links} link badges (expected the one button)')
if j is None: fail(f'{nxt!r} not in the tree')
if not (j >= 1 and L[j - 1][1] == 'pic' and L[j - 1][0]):
    fail(f'no linked picture right before {nxt!r}: {[x[1] for x in L[max(0, j - 3):j + 1]]}')
img = L[j - 1][0]
tf.sh('python3', f'{tf.T}/c.py', W, '-', 'click', '--element-index', img); tf.done(); time.sleep(0.8)
t = tf.tree()
if not tf.idx(t, r'^버튼 사진 교체$'): fail('picture not selected')
# selecting renumbers the tree: the picture's own 삭제 sits between its 링크 badge and the next block
rs = t.splitlines()
q = next((x for x, l in enumerate(rs) if re.search(r'^\s*\d+ (텍스트, Value: |container, Text: )', l)
          and flat(re.sub(r'^\s*\d+ (텍스트, Value: |container, Text: )', '', l)).startswith(flat(nxt))), None)
b = max((x for x, l in enumerate(rs[:q or 0]) if l.strip().endswith('텍스트, Value: 링크')), default=None)
d = next((re.match(r'\s*(\d+)', l).group(1) for l in rs[b:q] if re.search(r'\d+ 버튼 삭제$', l)), None) if q and b is not None else None
if not d: fail('no 삭제 on the picture')
tf.sh('orca', 'computer', 'click', '--app', 'com.google.Chrome', '--window-id', W, '--element-index', d, '--no-screenshot'); tf.done(); time.sleep(1.5)
# the block that moves up can take a few seconds to be drawn again (#26 on 11/10: not in the tree 1.5 s after 삭제)
for _ in range(8):
    L = layout()
    j = at(L)
    links = sum(1 for x in L if x[1] == 'pic')
    if j is not None and links == 0 and L[j - 1][1] == 'text': break
    time.sleep(1)
if not (j is not None and links == 0 and L[j - 1][1] == 'text'):
    # with plain text right above and below the picture, the editor joins the two into one block and the tree then
    # lists only that block's first paragraphs (#26 on 11/10: the screenshot showed the post intact, the next block
    # right under the 3줄 요약). Accept that when no link badge is left and Chrome find sees the next block exactly once.
    if links != 0: fail(f'after 삭제: links {links}')
    c = find(nxt)
    if c != 1: fail(f'after 삭제: {nxt!r} not a block of its own, find: {c} matches')
    subprocess.run(['cp', tf.shot(), os.path.join(os.environ.get('TMPDIR', '/tmp'), f'ctaoff_{n}_joined.png')])
    log(n, 'blocks joined by the editor, next block found once')
log(n, 'button removed')

if not tf.guard(): log(n, 'STOP owner busy for 3 h (post left open, not saved)'); sys.exit(2)
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
