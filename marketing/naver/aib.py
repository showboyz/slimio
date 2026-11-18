# aib.py <query>... : does Naver integrated search show an AI 브리핑, what type, and does it cite todayz777 / pdfslimio?
import re, sys, time, urllib.parse, urllib.request
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA, 'Accept-Language': 'ko'}), timeout=20).read().decode('utf-8', 'replace')
for q in sys.argv[1:]:
    h = get('https://search.naver.com/search.naver?where=nexearch&query=' + urllib.parse.quote(q))
    s = h.find('data-block-id="ai-briefing/')
    if s < 0:
        print(f'{q} | no AI 브리핑 | ours in page: blog {h.count("todayz777/")}', flush=True); time.sleep(1.5); continue
    e = h.find('data-fender-root="true"', s + 50)
    blk = h[s:e if e > 0 else s + 300000]
    kind = re.search(r'aib_(\w+?)_desk', blk); kind = kind.group(1) if kind else '?'
    src = []
    for u in re.findall(r'https?:\\?/\\?/[^"\'\s<>\\]+', blk):
        u = u.replace('\\/', '/')
        if any(x in u for x in ('pstatic', 'w3.org', 'favicon', '.ico', 'ai.search.naver', 'blogfiles', 'cafefiles', 'postfiles')): continue
        u = re.sub(r'^https?://(m\.)?', '', u).split('?')[0]
        if u not in src: src.append(u)
    ours = [u for u in src if 'todayz777' in u or 'pdfslimio' in u]
    hosts = []
    for u in src:
        hh = u.split('/')[0] + ('/' + u.split('/')[1] if u.startswith('blog.naver.com') else '')
        if hh not in hosts: hosts.append(hh)
    print(f'{q} | {kind} | cited ours: {ours or "NO"} | ours in page: {h.count("todayz777/")} | sources: {", ".join(hosts[:7])}', flush=True)
    time.sleep(1.5)
