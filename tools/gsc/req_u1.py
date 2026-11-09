# req_u1.py <win> <url>... : request GSC indexing for each URL in MY already-open window (opened by req_at.sh on the
# /u/1/ address = todays777). Same steps as tools/gsc/req.py's loop, but req.py opens the u/0 address and is never imported.
# Only while the owner is away (guard.sh before each typing/click), stops on quota, leaves the window open (req_at.sh closes it).
import sys, time, re, json
import insp_helpers as R
win = sys.argv[1]
results = {}
for u in sys.argv[2:]:
    if not R.wait_away(3 * 3600): R.log('owner never away; stop'); break
    t = R.tree(win)
    box = R.idx(t, r'콤보 상자.*(Inspect any URL|pdfslimio\.com)')
    if not box: R.log('no inspect box', u); results[u] = 'no box'; break
    R.orca('set-value', '--app', 'com.google.Chrome', '--window-id', win, '--element-index', box, '--value', u, '--no-screenshot')
    t = R.tree(win); box = R.idx(t, r'콤보 상자.*(Inspect any URL|pdfslimio\.com)'); R.click(win, box)
    if R.front() != 'Google Chrome':
        R.orca('get-app-state', '--app', 'com.google.Chrome', '--window-id', win, '--restore-window', '--no-screenshot')
    if R.front() != 'Google Chrome' or not R.guard(): R.log('not safe to type; skip', u); results[u] = 'skipped'; R.done(); continue
    R.orca('press-key', '--app', 'com.google.Chrome', '--window-id', win, '--key', 'Return', '--no-screenshot'); R.done()
    req = None
    for _ in range(30):
        time.sleep(3); t = R.tree(win)
        if 'Retrieving data' in t: continue
        req = R.idx(t, r'^버튼 .*(REQUEST INDEXING|Request indexing)')
        if req and u.split('pdfslimio.com')[1] in t: break
    if not req: R.log('no request button', u); results[u] = 'no button'; continue
    state = 'on Google' if 'URL is on Google' in t else ('not on Google' if 'not on Google' in t else ('unknown' if 'URL is unknown' in t else '?'))
    if not R.guard(): R.log('owner is back before request; skip', u); results[u] = 'skipped'; continue
    R.click(win, req); R.done()
    res = None
    for _ in range(60):
        time.sleep(3); t = R.tree(win)
        if re.search(r'container Indexing requested', t): res = 'requested'; break
        if re.search(r'container Quota Exceeded', t): res = 'QUOTA'; break
        if re.search(r'container .*problem|problem submitting your indexing request', t, re.I): res = 'problem'; break
    results[u] = f'{res} ({state})'; R.log(u, results[u])
    b = R.idx(t, r'^버튼 (Got it|Dismiss|닫기|OK)$')
    if b and R.guard(): R.click(win, b); R.done()
    if res in ('QUOTA', 'problem'): break   # 'try again later' = Google is refusing requests for now
    time.sleep(2)
R.log('RESULTS', json.dumps(results, ensure_ascii=False, indent=1))
