# insp_helpers.py : req.py's helpers without its u/0 window code, for req_u1.py (tree, idx, click, guard,
# wait_away, log). Importing req.py itself would open a u/0 window.
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

