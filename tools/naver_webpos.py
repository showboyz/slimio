# naver_webpos.py <query>... : where pdfslimio.com and todayz777 show in Naver integrated search and the web-doc tab
import re, sys, time, urllib.parse, urllib.request
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA, 'Accept-Language': 'ko'}), timeout=20).read().decode('utf-8', 'replace')
def order(h):
    out = []
    for m in re.finditer(r'href="(https?://[^"]+)"', h):
        u = m.group(1)
        if re.search(r'(search\.naver|naver\.com/(?!todayz777)|pstatic|navercorp|help\.naver|nid\.naver|keep\.naver|policy\.naver|naver\.me)', u) and 'blog.naver.com/' not in u: continue
        if 'blog.naver.com/' in u and not re.search(r'blog\.naver\.com/\w+/\d{9,}', u): continue
        k = re.sub(r'^https?://(www\.|m\.)?', '', u).split('?')[0].rstrip('/')
        k = re.match(r'blog\.naver\.com/\w+/\d+', k).group(0) if k.startswith('blog.naver.com/') else k
        if k not in out: out.append(k)
    return out
for q in sys.argv[1:]:
    qq = urllib.parse.quote(q)
    for name, u in (('통합', f'https://search.naver.com/search.naver?where=nexearch&query={qq}'),):
        o = order(get(u)); time.sleep(1.5)
        me = [f'{i+1}:{k[:60]}' for i, k in enumerate(o) if 'pdfslimio' in k or 'todayz777' in k]
        print(f'{q} | {name} /{len(o)} | {" ".join(me) or "-"} | top3 {", ".join(x[:40] for x in o[:3])}', flush=True)
