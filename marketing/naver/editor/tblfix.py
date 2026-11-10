# tblfix.py <win> <draft.html> : in a post already open in the editor window <win>, give every table the
# editor's own "grid with grey header" style. Posts pasted before 2026-10-29 have bare tables (border:none).
# For each table: Chrome find (Cmd+F) on a cell text that occurs once in the post brings it on screen (usually
# mid-window; Return, since a pasted search can sit at 0/1), the find bar's own close button shuts it (Esc makes
# the editor scroll back to its old caret, and while the bar is open window clicks land relative to the bar),
# a click on the match opens the table toolbar (the click goes where hl.cjs finds Chrome's orange active-match
# highlight in a screenshot, since a match already on screen is not scrolled to the middle; it falls back to the
# column centre at MID_Y, and tries the next cell text when no toolbar opens), then the toolbar's
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
    if r.stdout.strip() != 'ok': raise SystemExit(f'key/click failed: {a} {r.stdout} {r.stderr}')
    done()  # our own input, so guard() does not take it for the owner's
def windows():   # ids of Chrome's windows as list-windows gives them
    r = sh('orca', 'computer', 'list-windows', '--app', 'com.google.Chrome', '--json')
    try: d = json.loads(r.stdout); d = d.get('result', d); return {str(w['id']) for w in d.get('windows', [])}
    except Exception: return set()
def close_find(before):
    # Since the orca update of 2026-11-10 Chrome's find bar is a window of its own: while it is open the tree of W can
    # be just the bar, and a click on its 검색 바 닫기 through W does nothing (ctaoff #28 on 11/11). So the button is
    # clicked in the bar's own window, one that is new since `before` (the windows before my Cmd+F) and so can only be
    # mine. Esc is no use: it scrolls the editor back to its old caret. Returns True when no find bar is left.
    for w in windows() - set(before) - {str(W)}:
        r = sh('orca', 'computer', 'get-app-state', '--app', 'com.google.Chrome', '--window-id', w, '--json', '--no-screenshot')
        try: t = json.loads(r.stdout)['result']['snapshot']['treeText']
        except Exception: continue
        i = idx(t, r'^버튼 검색 바 닫기$')
        if i and idx(t, r'^텍스트 필드 \(settable\) 찾기'):
            sh('orca', 'computer', 'click', '--app', 'com.google.Chrome', '--window-id', w, '--element-index', i, '--no-screenshot')
            done(); time.sleep(0.8)
            return w not in windows()
    press(r'^버튼 검색 바 닫기$')   # the bar inside W, as before 2026-11-10
    return '검색 바 닫기' not in tree()
def leave_dialog(press=False):   # see leavedlg.sh; True when the dialog is open (or, with press, was answered 나가기)
    return sh('bash', f'{T}/leavedlg.sh', 'press' if press else 'check').stdout.strip() in ('open', 'left')
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
    done(); time.sleep(0.8); return True
def shot():
    r = sh('orca', 'computer', 'get-app-state', '--app', 'com.google.Chrome', '--window-id', W, '--json')
    return json.loads(r.stdout)['result']['screenshot']['path']
def state():
    r = sh('orca', 'computer', 'get-app-state', '--app', 'com.google.Chrome', '--window-id', W, '--json')
    try: d = json.loads(r.stdout)['result']; return d['snapshot']['treeText'], d['screenshot']
    except Exception: return '', None
def match_point(s, after=None):
    # window point of the orange active find match inside the content column (Chrome does not scroll a match
    # that is already on screen, so it is not always at MID_Y); `after` = screenshot once the find bar is shut
    if not s: return None
    f = s['scale']
    a = [after['path']] if after and after.get('scale') == f else []
    out = sh('node', f'{T}/hl.cjs', s['path'], str(int(LEFT * f)), str(int((LEFT + WIDTH) * f)), str(int(200 * f)), *a).stdout.split()
    if len(out) == 3: return int(int(out[0]) / f), int(int(out[1]) / f)

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
        plan.append([(p, ci, n) for _, _, p, ci in sorted(cands)[:3]])  # up to 3 cell texts to try
    print('tables', len(tables), 'plan', plan, flush=True)
    shots = []
    for i, pl in enumerate(plan, 1):
        if pl is None: print(i, 'SKIP no unique cell text'); continue
        if not guard(): print(i, 'STOP user is back'); break
        found = False
        for p, ci, n in pl:
            if not guard(): break
            subprocess.run('pbcopy', input=p, text=True)
            k('hotkey', '--key', 'CmdOrCtrl+F'); time.sleep(0.7)
            k('hotkey', '--key', 'CmdOrCtrl+V'); time.sleep(1.2)
            k('press-key', '--key', 'Return'); time.sleep(1.0)  # a pasted search can sit at 0/1 without scrolling
            t, s = state()
            m = re.search(r'전체 결과 (\d+)개 중 (\d+)개', t)
            one = bool(m and m.group(1) == '1' and m.group(2) == '1')
            closed = press(r'^버튼 검색 바 닫기$')
            pt = match_point(s, state()[1]) if one and closed else None
            if not (one and closed): print(i, 'find miss', m.group(0) if m else None, 'closed', closed, repr(p)); continue
            x, y = pt or (int(LEFT + (ci + 0.5) * WIDTH / n), MID_Y)
            k('click', '--x', str(x), '--y', str(y)); time.sleep(0.8)
            if '표 스타일' in tree(): found = True; break
            print(i, 'no table toolbar after click', repr(p), x, y, 'highlight' if pt else 'mid')
        if not found: print(i, 'SKIP find/click'); done(); continue
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
