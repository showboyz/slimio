# tblfix.py <win> <draft.html> : in a post already open in the editor window <win>, give every table the
# editor's own "grid with grey header" style. Posts pasted before 2026-10-29 have bare tables (border:none).
# For each table: Chrome find (Cmd+F) on a cell text that occurs once in the post scrolls it to the middle of
# the window (Return, since a pasted search can sit at 0/1), the find bar's own close button shuts it (Esc makes
# the editor scroll back to its old caret, and while the bar is open window clicks land relative to the bar),
# a click on that cell opens the table toolbar, then the toolbar's
# '표 스타일 열기' popup and its '표2' button, both by accessibility name (the toolbar layout differs between a
# selected table and a caret in a cell). It reopens the menu to check '표2 선택됨', then closes it.
# The cell click uses window points for the 1875×1200 editor window (content column x 703–1397).
import html, json, re, subprocess, sys, time, os
T = os.path.dirname(os.path.abspath(__file__))
W = None
LEFT, WIDTH, MID_Y = 703, 694, 692

def plain(h): return html.unescape(re.sub(r'<[^>]+>', '', h)).strip()
def sh(*a): return subprocess.run(a, capture_output=True, text=True)
def guard(wait=3 * 3600):
    # waits (up to 3 h) while the owner is using the computer instead of giving up mid-post
    t0 = time.time()
    while sh('bash', f'{T}/guard.sh').returncode != 0:
        if time.time() - t0 > wait: return False
        time.sleep(20)
    return True
def done(): sh('bash', f'{T}/guard.sh', 'done')
def k(*a):
    r = sh('bash', f'{T}/k.sh', W, *a)
    if 'ok' not in r.stdout: raise SystemExit(f'key/click failed: {a} {r.stdout} {r.stderr}')
def tree():
    r = sh('orca', 'computer', 'get-app-state', '--app', 'com.google.Chrome', '--window-id', W, '--json', '--no-screenshot')
    try: return json.loads(r.stdout)['result']['snapshot']['treeText']
    except Exception: return ''
def idx(t, pat):
    for l in t.splitlines():
        m = re.match(r'\s*(\d+) (.*)', l)
        if m and re.search(pat, m.group(2)): return m.group(1)
def press(pat):
    i = idx(tree(), pat)
    if not i: return False
    sh('orca', 'computer', 'click', '--app', 'com.google.Chrome', '--window-id', W, '--element-index', i, '--no-screenshot')
    time.sleep(0.8); return True
def shot():
    r = sh('orca', 'computer', 'get-app-state', '--app', 'com.google.Chrome', '--window-id', W, '--json')
    return json.loads(r.stdout)['result']['screenshot']['path']

def fix(win, draft):
    """Returns (tables, styled)."""
    global W
    W = str(win)
    src = open(draft).read()
    body = re.sub(r'^<!--.*?-->\s*', '', src, flags=re.S)
    text = plain(re.sub(r'<(br|/p|/h2|/li|/td|/th|/tr)[^>]*>', '\n', body))
    title = re.search(r'제목: (.*)', src).group(1)
    tables = re.findall(r'<table[^>]*>.*?</table>', body, flags=re.S)
    plan = []
    for t in tables:
        rows = [re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, flags=re.S) for r in re.findall(r'<tr[^>]*>(.*?)</tr>', t, flags=re.S)]
        n = max(len(r) for r in rows)
        cands = []
        for r in rows:
            for ci, c in enumerate(r):
                p = plain(c)
                if len(p) >= 4 and (text + '\n' + title).count(p) == 1 and len(r) == n:
                    cands.append((ci != 0, -min(len(p), 30), p, ci))
        if not cands: plan.append(None); continue
        _, _, p, ci = sorted(cands)[0]
        plan.append((p, ci, n))
    print('tables', len(tables), 'plan', plan, flush=True)
    shots = []
    for i, pl in enumerate(plan, 1):
        if pl is None: print(i, 'SKIP no unique cell text'); continue
        p, ci, n = pl
        if not guard(): print(i, 'STOP user is back'); break
        subprocess.run('pbcopy', input=p, text=True)
        k('hotkey', '--key', 'CmdOrCtrl+F'); time.sleep(0.7)
        k('hotkey', '--key', 'CmdOrCtrl+V'); time.sleep(1.0)
        k('press-key', '--key', 'Return'); time.sleep(0.8)  # a pasted search can sit at 0/1 without scrolling
        m = re.search(r'전체 결과 (\d+)개 중 (\d+)개', sh('orca', 'computer', 'get-app-state', '--app', 'com.google.Chrome', '--window-id', W, '--json', '--no-screenshot').stdout)
        closed = press(r'^버튼 검색 바 닫기$')
        if not m or m.group(1) != '1' or m.group(2) != '1' or not closed:
            print(i, 'SKIP find', m.group(0) if m else None, 'closed', closed, repr(p)); done(); continue
        x = int(LEFT + (ci + 0.5) * WIDTH / n)
        k('click', '--x', str(x), '--y', str(MID_Y)); time.sleep(0.8)
        if '표 스타일' not in tree():
            print(i, 'SKIP no table toolbar after click', repr(p), x); done(); continue
        ok = press(r'^팝업 버튼 표 스타일 열기') and press(r'^버튼 표2( |$)')
        ok = ok and press(r'^팝업 버튼 표 스타일 열기') and bool(idx(tree(), r'^버튼 표2 선택됨'))
        press(r'표 스타일 닫기')
        done()
        path = shot(); print(i, 'styled' if ok else 'NOT VERIFIED', repr(p), 'col', ci, 'of', n, path, flush=True)
        if ok: shots.append(path)
    print('SHOTS', ' '.join(shots))
    return len(tables), len(shots)

if __name__ == '__main__':
    fix(sys.argv[1], sys.argv[2])
