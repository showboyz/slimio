# umpull.py <win> <outdir> <name start end>... : open Umami overview for each KST date range (start/end as
# YYYY-MM-DDTHH:MM) in my own window and save the accessibility tree to <outdir>/<name>.txt. Waits for the owner to be away.
import sys, os, time, re, datetime as dt
sys.path.insert(0, '/Users/home/orca/projects/slimio/marketing/naver/editor')
import tblfix as tf
from tblfix_sched import go
tf.W = sys.argv[1]; out = sys.argv[2]; a = sys.argv[3:]
U = 'https://cloud.umami.is/analytics/us/websites/ab53f00a-b92a-4d4d-aaf0-6b5329869de7'
ms = lambda s: int(dt.datetime.fromisoformat(s + '+09:00').timestamp() * 1000)
for i in range(0, len(a), 3):
    name, s, e = a[i:i + 3]
    if not tf.guard(): print('STOP owner busy'); sys.exit(2)
    go(f'{U}?date=range:{ms(s)}:{ms(e)}'); tf.done()
    t = ''
    for _ in range(20):
        time.sleep(1.5); t = tf.tree()
        if re.search(r'Text: Visitors \S+', t) and 'Loading' not in t: break
    time.sleep(3); t = tf.tree()
    open(os.path.join(out, name + '.txt'), 'w').write(t)
    m = re.search(r'container, Text: (Visitors[^\n]*)', t)
    print(name, s, e, m.group(1)[:160] if m else 'NO VISITORS')
