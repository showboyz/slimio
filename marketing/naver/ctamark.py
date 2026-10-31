# ctamark.py <draft.html…> [--print] : marks where a Naver draft gets its two SlimIO button pictures, at the same spots as
# the Tistory boxes (tistory/cta.py): <!--IMG:cta-<tool>.png--> at the end of the section that first links the main tool
# (or before the first heading when that is near the end) and <!--IMG:cta-<tool>-end.png--> above the closing 출처 line.
# It also adds a '버튼링크: <url>' header line; newpost.py uploads the pictures and puts that link on them.
# The pictures come from banners.py. A draft that already has the marks is left alone.
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '../tistory'))
import cta, banners

def apply(src):
    if '<!--IMG:cta-' in src: return src, 'already has the marks'
    p = cta.plan(src)
    if not p: return src, 'no tool link'
    head, rows, main, url, n, end = p
    if main not in cta.TOOLS: return src, f'no button copy for {main} (add it to tistory/cta.py TOOLS, run banners.py)'
    first, last = (os.path.basename(f) for f in banners.files(main))
    if not all(os.path.exists(os.path.join(banners.OUT, f)) for f in (first, last)): return src, 'run banners.py first'
    prev = lambda k: next((rows[j] for j in range(k, -1, -1) if rows[j].strip()), '')
    for k in (n, end - 1):   # an h2 right before an IMG mark would leak the heading style into the picture's chunk
        if prev(k).lstrip().startswith('<h2'): return src, f'h2 right before a mark (line {k + 1})'
    out = rows[:n + 1] + ['', f'<!--IMG:{first}-->', ''] + rows[n + 1:end] + [f'<!--IMG:{last}-->', ''] + rows[end:]
    head = re.sub(r'\n?-->\s*$', f'\n버튼링크: {url}\n-->\n\n', head.rstrip(), count=1)
    return head + '\n'.join(out), f'{main} {first} after line {n + 1}/{len(rows)}, {last} before line {end + 1}'

if __name__ == '__main__':
    dry = '--print' in sys.argv
    for f in [a for a in sys.argv[1:] if a != '--print']:
        new, why = apply(open(f).read())
        print(os.path.basename(f), '|', why)
        if not dry and new != open(f).read(): open(f, 'w').write(new)
