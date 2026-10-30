# rank.py <query>... : position of blog.naver.com/todayz777 posts among blog posts in Naver's blog tab
# (ssc=tab.blog.all, first page) and in integrated search (first page), counting each post once
import re, sys, time, urllib.parse, urllib.request
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA, 'Accept-Language': 'ko'}), timeout=20).read().decode('utf-8', 'replace')
def ranks(h):
    posts = []
    for m in re.finditer(r'blog\.naver\.com/(\w+)/(\d{9,})', h):
        k = m.group(1) + '/' + m.group(2)
        if k not in posts: posts.append(k)
    return [f'{i + 1}({p[-4:]})' for i, p in enumerate(posts) if p.startswith('todayz777/')], len(posts)
for q in sys.argv[1:]:
    qq = urllib.parse.quote(q)
    b, nb = ranks(get(f'https://search.naver.com/search.naver?ssc=tab.blog.all&query={qq}')); time.sleep(1.5)
    t, nt = ranks(get(f'https://search.naver.com/search.naver?where=nexearch&query={qq}')); time.sleep(1.5)
    print(f'{q} | blog tab {" ".join(b) or "-"} /{nb} | integrated {" ".join(t) or "-"} /{nt}', flush=True)
