# ctadel.py <win> <NN> <YYYY.MM.DD> <HH> : take the second (end) SlimIO button picture out of the reserved post of draft NN
# and save with the schedule unchanged. On 2026-10-31 posts got a button before the 출처 line too; the owner then chose
# one button per post (short posts, room for ads). The end picture is the linked picture right before the 출처 block:
# find that block (Chrome find scrolls it into view), check the picture just above it carries a link badge and the
# block above that is text, select the picture, press its own 삭제, check one link badge is left and the 출처 block now
# follows the closing paragraph. Anything unexpected leaves the editor without saving.
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

def fail(why): log(n, 'FAIL', why); leave_unsaved(); tf.done(); sys.exit(1)
def k(*a): tf.sh('bash', f'{tf.T}/k.sh', W, *a); tf.done()
flat = lambda x: re.sub(r'\s+', '', x)
head, rows, main, url, a, end = cta.plan(src)
bottom = ' '.join(tf.plain(rows[end]).split())[:24].strip()

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

subprocess.run('pbcopy', input=bottom, text=True)
k('hotkey', '--key', 'CmdOrCtrl+F'); time.sleep(0.7); k('hotkey', '--key', 'CmdOrCtrl+V'); time.sleep(1.2)
k('press-key', '--key', 'Return'); time.sleep(1.5)
m = re.search(r'전체 결과 (\d+)개 중 (\d+)개', tf.tree())
tf.press(r'^버튼 검색 바 닫기$'); time.sleep(1)
if not (m and m.group(1) == '1'): fail(f'find {bottom!r}: {m and m.group(0)}')

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
            val = m2.group(2).replace('\ufeff', '').strip() if m2 else ''
            if m2 and val and val not in ('AI 활용 설정', '사진 설명을 입력하세요.', '추가할 컴포넌트를 선택하세요.', '도움말', '대표') \
                    and not val.startswith('사진 컴포넌트') and '사진 설명을 입력하세요' not in val:
                out.append((i, 'text', val))
        prev = i if rest == 'container' else prev
    return out
L = layout()
links = sum(1 for x in L if x[1] == 'pic')
j = next((i for i, x in enumerate(L) if x[1] == 'text' and flat(x[2]).startswith(flat(bottom))), None)
if j is None: fail('출처 block not in the tree')
if links != 2: fail(f'{links} link badges (expected the two buttons)')
# right before the 출처 block: the linked picture (the end button), and before that a text block
if not (j >= 2 and L[j - 1][1] == 'pic' and L[j - 1][0] and L[j - 2][1] == 'text'):
    fail(f'no linked picture right before 출처: {[x[1] for x in L[max(0, j - 3):j + 1]]}')
img = L[j - 1][0]
tf.sh('python3', f'{tf.T}/c.py', W, '-', 'click', '--element-index', img); tf.done(); time.sleep(0.8)
t = tf.tree()
if not tf.idx(t, r'^버튼 사진 교체$'): fail('picture not selected')
# selecting renumbers the tree: the picture's own 삭제 sits between its 링크 badge and the 출처 line
rs = t.splitlines()
q = next((x for x, l in enumerate(rs) if re.search(r'^\s*\d+ 텍스트, Value: ', l) and flat(re.sub(r'^\s*\d+ 텍스트, Value: ', '', l)).startswith(flat(bottom))), None)
b = max((x for x, l in enumerate(rs[:q or 0]) if l.strip().endswith('텍스트, Value: 링크')), default=None)
d = next((re.match(r'\s*(\d+)', l).group(1) for l in rs[b:q] if re.search(r'\d+ 버튼 삭제$', l)), None) if q and b else None
if not d: fail('no 삭제 on the picture')
tf.sh('orca', 'computer', 'click', '--app', 'com.google.Chrome', '--window-id', W, '--element-index', d, '--no-screenshot'); tf.done(); time.sleep(1.5)
L = layout()
j = next((i for i, x in enumerate(L) if x[1] == 'text' and flat(x[2]).startswith(flat(bottom))), None)
links = sum(1 for x in L if x[1] == 'pic')
if j is None or links != 1 or L[j - 1][1] != 'text': fail(f'after 삭제: links {links}, before 출처 {[x[1] for x in L[max(0, (j or 0) - 2):(j or 0) + 1]]}')
log(n, 'end button removed')

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
