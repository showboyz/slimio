# umget.py <win> <outfile> <url> [wait-pattern] : open url in my window (owner away), save the tree
import sys, time, re
sys.path.insert(0, '/Users/home/orca/projects/slimio/marketing/naver/editor')
import tblfix as tf
from tblfix_sched import go
tf.W = sys.argv[1]; pat = sys.argv[4] if len(sys.argv) > 4 else r'Text: Visitors \S+'
if not tf.guard(): print('STOP owner busy'); sys.exit(2)
go(sys.argv[3]); tf.done()
for _ in range(20):
    time.sleep(1.5); t = tf.tree()
    if re.search(pat, t): break
time.sleep(3); t = tf.tree(); open(sys.argv[2], 'w').write(t)
m = re.search(r'container, Text: (Visitors[^\n]*)', t); print(m.group(1)[:160] if m else 'no visitors line')
