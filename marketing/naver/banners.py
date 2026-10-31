# banners.py : makes the Naver button banners in marketing/naver/cta/ from the Tistory box (tistory/cta.py), one per tool
# page: cta-<name>.png ('무료 · 설치 없이 · 회원가입 없이'). The editor can't keep our HTML box, so Naver posts get the
# same box as a picture with the tool link set on it (editor/ctains.py).
import os, re, sys, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '../tistory'))
import cta

OUT = os.path.join(HERE, 'cta')
def name(page):   # 'ko/unlock-pdf.html' → 'unlock-pdf', 'ko/' → 'compress-pdf'
    return re.sub(r'\.html$', '', page.split('/', 1)[1]) or 'compress-pdf'
def file(page): return f'{OUT}/cta-{name(page)}.png'

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    jobs = []
    for page, (headline, button) in cta.TOOLS.items():
        jobs.append({'out': file(page), 'html': cta.box('#', cta.EYEBROW, headline, button)})
    spec = os.path.join(OUT, 'jobs.json'); json.dump(jobs, open(spec, 'w'), ensure_ascii=False)
    subprocess.run(['node', os.path.join(HERE, 'editor/banner.mjs'), spec], check=True)
    os.remove(spec)
