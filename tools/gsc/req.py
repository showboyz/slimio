# req.py <url>... : request GSC indexing for each URL in a new Chrome window, only while the user is away.
# Waits (up to 3 h) for 120 s without keyboard/mouse, re-checks before every step, stops on quota.
import json, subprocess, sys, time, re, os
GUARD = os.path.expanduser('~/orca/projects/slimio/marketing/naver/editor/guard.sh')
GSC = 'https://search.google.com/search-console?resource_id=sc-domain%3Apdfslimio.com'
def orca(*a):
    r = subprocess.run(['orca', 'computer', *a], capture_output=True, text=True)
    return r.stdout + r.stderr
def tree(win):
    out = orca('get-app-state', '--app', 'com.google.Chrome', '--window-id', str(win), '--no-screenshot', '--json')
    try: return json.loads(out)['result']['snapshot']['treeText']
    except Exception: return ''
def idx(t, pat):
    for line in t.splitlines():
        m = re.match(r'\s*(\d+) (.*)', line)
        if m and re.search(pat, m.group(2)): return m.group(1)
def click(win, i): orca('click', '--app', 'com.google.Chrome', '--window-id', str(win), '--element-index', str(i), '--no-screenshot')
def guard():
    return subprocess.run(['bash', GUARD], capture_output=True, text=True).returncode == 0
def done(): subprocess.run(['bash', GUARD, 'done'])
def front():
    return subprocess.run(['osascript', '-e', 'tell application "System Events" to get name of first process whose frontmost is true'], capture_output=True, text=True).stdout.strip()
def wait_away(limit):
    t0 = time.time()
    while time.time() - t0 < limit:
        if guard(): return True
        time.sleep(20)
    return False
def windows():
    out = orca('list-windows', '--app', 'com.google.Chrome', '--json')
    return {w['id']: w['title'] for w in json.loads(out)['result']['windows']}
def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)

urls = sys.argv[1:]
if not wait_away(3 * 3600): log('user never away; stop'); sys.exit(1)
before = windows()
subprocess.run(['open', '-na', 'Google Chrome', '--args', '--new-window', GSC]); time.sleep(10)
new = [w for w in windows() if w not in before]
if not new: log('no new window'); sys.exit(1)
win = new[0]; done(); log('window', win)
results = {}
for u in urls:
    if not guard():
        log('user is back; waiting'); 
        if not wait_away(3 * 3600): break
    t = tree(win)
    box = idx(t, r'콤보 상자.*(Inspect any URL|pdfslimio\.com)')
    if not box: log('no inspect box', u); results[u] = 'no box'; break
    orca('set-value', '--app', 'com.google.Chrome', '--window-id', str(win), '--element-index', box, '--value', u, '--no-screenshot')
    t = tree(win); box = idx(t, r'콤보 상자.*(Inspect any URL|pdfslimio\.com)'); click(win, box)
    if front() != 'Google Chrome':
        orca('get-app-state', '--app', 'com.google.Chrome', '--window-id', str(win), '--restore-window', '--no-screenshot')
    if front() != 'Google Chrome' or not guard(): log('not safe to type; skip', u); results[u] = 'skipped'; done(); continue
    orca('press-key', '--app', 'com.google.Chrome', '--window-id', str(win), '--key', 'Return', '--no-screenshot'); done()
    req = None
    for _ in range(30):
        time.sleep(3); t = tree(win)
        if 'Retrieving data' in t: continue
        req = idx(t, r'^버튼 .*(REQUEST INDEXING|Request indexing)')
        if req and u.split('pdfslimio.com')[1] in t: break
    if not req: log('no request button', u); results[u] = 'no button'; continue
    state = 'URL is on Google' if 'URL is on Google' in t else ('not on Google' if 'not on Google' in t else '?')
    if not guard(): log('user is back before request'); results[u] = 'skipped'; continue
    click(win, req); done()
    res = None
    for _ in range(60):
        time.sleep(3); t = tree(win)
        if re.search(r'container Indexing requested', t): res = 'requested'; break
        if re.search(r'container Quota Exceeded', t): res = 'QUOTA'; break
        if re.search(r'container .*problem', t, re.I): res = 'problem'; break
    results[u] = f'{res} ({state})'; log(u, results[u])
    b = idx(t, r'^버튼 (Got it|Dismiss|닫기|OK)$')
    if b: click(win, b); done()
    if res == 'QUOTA': break
    time.sleep(2)
log('RESULTS', json.dumps(results, ensure_ascii=False, indent=1))
t = tree(win); cs = [l.split()[0] for l in t.splitlines() if l.strip().endswith('닫기 버튼') and l.strip().split(' ',1)[1] == '닫기 버튼']; c = cs[-1] if cs else None
if c and guard(): click(win, c); log('window closed')
