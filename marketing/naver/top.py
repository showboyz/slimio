# top.py <query>... : first blog-tab results on Naver search (blog id, post no, title, date shown), to see who answers a query now
import re, sys, time, html, urllib.parse, urllib.request
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA, 'Accept-Language': 'ko'}), timeout=20).read().decode('utf-8', 'replace')
for q in sys.argv[1:]:
    h = get('https://search.naver.com/search.naver?ssc=tab.blog.all&query=' + urllib.parse.quote(q))
    seen, out = set(), []
    # each result: a link to blog.naver.com/<id>/<no> with the title text nearby
    for m in re.finditer(r'href="https://blog\.naver\.com/(\w+)/(\d{9,})"[^>]*>(.*?)</a>', h, re.S):
        k = m.group(1) + '/' + m.group(2)
        t = html.unescape(re.sub(r'<[^>]+>', '', m.group(3))).strip()
        if k in seen or len(t) < 8: continue
        seen.add(k); out.append(f'{m.group(1)}/{m.group(2)[-5:]}  {t[:70]}')
        if len(out) == 6: break
    print(f'== {q}'); [print('  ', o) for o in out]
    time.sleep(1.5)
