import sys, json, urllib.request, urllib.parse, time
# ac.py q1 q2 ... : print Naver autocomplete suggestions for each query
for q in sys.argv[1:]:
    u = 'https://ac.search.naver.com/nx/ac?' + urllib.parse.urlencode({'q': q, 'con': 1, 'frm': 'nv', 'ans': 2, 'r_format': 'json', 'r_enc': 'UTF-8', 'r_unicode': 0, 't_koreng': 1, 'run': 2, 'rev': 4, 'q_enc': 'UTF-8', 'st': 100})
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.naver.com/'})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=10))
        items = [i[0] if isinstance(i, list) else i for i in (d.get('items') or [[]])[0]]
        print(f'{q}: ' + ' | '.join(items[:10]))
    except Exception as e:
        print(f'{q}: ERR {e}')
    time.sleep(0.4)
