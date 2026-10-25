# usage: python3 overlap.py <draft.html> [n=12]
# Share of the draft's n-word sequences that also appear in any other Naver/Tistory draft.
import re, sys, glob, html, os
def words(p):
    s = open(p).read()
    s = re.sub(r'<!--.*?-->', ' ', s, flags=re.S)
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s))
    return re.findall(r'[\w가-힣%.,·~×-]+', s)
def grams(w, n): return {tuple(w[i:i+n]) for i in range(len(w)-n+1)}
draft = os.path.abspath(sys.argv[1]); n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
root = os.path.expanduser('~/orca/projects/slimio/marketing')
g = grams(words(draft), n)
for p in sorted(glob.glob(root+'/naver/*.html') + glob.glob(root+'/tistory/*.html')):
    if os.path.abspath(p) == draft: continue
    common = g & grams(words(p), n)
    if common:
        print(f"{len(common)/max(1,len(g))*100:5.1f}%  {os.path.relpath(p, root)}")
        for c in list(common)[:3]: print('       ', ' '.join(c))
print('grams', len(g))
