# watch_live.py <deadline YYYY-MM-DDTHH:MM> <logNo|title|query>... : every 2 h until the deadline, look for each post on
# Naver's blog tab with its quoted title and with a plain query; stop early once every post is found both ways.
import re, sys, time, datetime, urllib.parse, urllib.request
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
get = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA, 'Accept-Language': 'ko'}), timeout=20).read().decode('utf-8', 'replace')
def rank(q, no):
    h = get('https://search.naver.com/search.naver?ssc=tab.blog.all&query=' + urllib.parse.quote(q))
    posts = []
    for m in re.finditer(r'blog\.naver\.com/\w+/(\d{9,})', h):
        if m.group(1) not in posts: posts.append(m.group(1))
    return posts.index(no) + 1 if no in posts else '-'
end = datetime.datetime.fromisoformat(sys.argv[1])
items = [a.split('|') for a in sys.argv[2:]]
while datetime.datetime.now() < end:
    out, found = [], 0
    for no, title, q in items:
        try: a, b = rank('"' + title[:30] + '"', no), rank(q, no)
        except Exception as e: a = b = f'error {e}'
        found += a != '-' and b != '-' and not str(a).startswith('error')
        out.append(f'{no} title {a} · "{q}" {b}'); time.sleep(2)
    print(time.strftime('%m-%d %H:%M'), ' | '.join(out), flush=True)
    if found == len(items): print('FOUND all'); break
    time.sleep(2 * 3600)
else: print('deadline')
