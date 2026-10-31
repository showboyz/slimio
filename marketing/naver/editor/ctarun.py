# ctarun.py <win> <list.txt> [script.py] [NN,NN,…] : runs ctains.py (or another per-post script with the same arguments,
# e.g. ctadel.py) for every reserved post in <list.txt> (lines as the 예약 발행 list shows them:
# '<n> 버튼 <title> <YYYY.MM.DD HH:MM>'), or only drafts NN,…, soonest first. A post that fails its checks is left unsaved
# and skipped; the run stops when the owner is busy for 3 h (exit 2). Prints one line per post and a summary.
import os, re, sys, subprocess, time
from tblfix_sched import drafts
HERE = os.path.dirname(os.path.abspath(__file__))
W, lst = sys.argv[1], sys.argv[2]
script = sys.argv[3] if len(sys.argv) > 3 else 'ctains.py'
only = {int(x) for x in sys.argv[4].split(',')} if len(sys.argv) > 4 else None
D = drafts()
jobs = []
for l in open(lst):
    m = re.match(r'\s*\d+ 버튼 (.*) (2026\.\d\d\.\d\d) (\d\d):00$', l.strip())
    if not m: continue
    f = D.get(m.group(1).strip())
    if not f: print('no draft for', m.group(1)[:40], flush=True); continue
    nn = int(os.path.basename(f)[:2])
    if only is None or nn in only: jobs.append((m.group(2), m.group(3), nn, m.group(1)[:30]))
jobs.sort()
done, failed = [], []
for date, hh, n, title in jobs:
    r = subprocess.run(['python3', f'{HERE}/{script}', W, str(n), date, hh], capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or [''])[-1]
    print(time.strftime('%H:%M:%S'), f'#{n}', date, hh, f'rc={r.returncode}', '|', last[-120:], flush=True)
    if r.returncode == 2: print('STOP owner busy', flush=True); break
    (done if 'SAVED' in last or 'already has' in last else failed).append(n)
print('saved/had', len(done), done, '| failed', failed, flush=True)
