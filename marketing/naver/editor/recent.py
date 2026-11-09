# recent.py <n> : own-title search (blog tab, in quotes) position of the n newest posts in the blog RSS
import re, sys, time, html, urllib.parse, urllib.request
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
get = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA, 'Accept-Language': 'ko'}), timeout=20).read().decode('utf-8', 'replace')
rss = get('https://rss.blog.naver.com/todayz777.xml')
for t, l, d in re.findall(r'<item>.*?<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>.*?<link>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</link>.*?<pubDate>(.*?)</pubDate>', rss, re.S)[:int(sys.argv[1])]:
    t = html.unescape(t).strip(); no = re.search(r'(\d{9,})', l).group(1)
    h = get('https://search.naver.com/search.naver?ssc=tab.blog.all&query=' + urllib.parse.quote('"' + t[:30] + '"'))
    posts = []
    for m in re.finditer(r'blog\.naver\.com/\w+/(\d{9,})', h):
        if m.group(1) not in posts: posts.append(m.group(1))
    print(f'  {d[5:22]} {no} pos {posts.index(no) + 1 if no in posts else "-"} | {t[:30]}', flush=True)
    time.sleep(1.5)
