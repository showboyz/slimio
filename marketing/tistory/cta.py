# cta.py <draft.html…> : put one big SlimIO button in a Tistory draft, so the way to the site doesn't hang on a text link.
# The post's main tool is the one it links to most (first one on a tie). The box goes at the end of the section with the
# first link to it, or before the first heading when that is near the end. Only one: the posts are short and the end of
# a post is kept for ads (owner, 2026-10-31). A draft with a second box from the first version loses it; a draft that
# already has the box is otherwise left alone. --print shows what would change without writing.
import re, sys, collections

EYEBROW = '무료 · 설치 없이 · 회원가입 없이'
EYEBROW_END = '이 글에서 직접 써 본 도구'   # the end box of the first version (2026-10-31), now removed
TOOLS = {   # page → (headline, button); wording follows each page's own h1/title
    'ko/compress-id-photo.html': ('📷 사진 규격 맞추고 용량까지 한 번에', '사진 용량 줄이러 가기 →'),
    'ko/signature-image.html': ('✍️ 서명 이미지, 투명 PNG로 규격에 딱', '서명 이미지 만들기 →'),
    'ko/': ('📄 PDF 용량 줄이기, 글자는 선명하게', 'PDF 용량 줄이러 가기 →'),
    'ko/sign-pdf.html': ('🔴 PDF에 도장·서명 넣기', 'PDF에 도장 넣으러 가기 →'),
    'ko/us-visa-photo.html': ('🇺🇸 미국 비자 사진 600×600 · 240KB 이하', '미국 비자 사진 만들기 →'),
    'ko/heic-to-jpg.html': ('📸 아이폰 HEIC 사진을 JPG로, 여러 장 한 번에', 'HEIC → JPG 변환하기 →'),
    'ko/unlock-pdf.html': ('🔓 잠긴 PDF, 비밀번호 풀고 다시 저장', 'PDF 비밀번호 풀러 가기 →'),
    'ko/merge.html': ('📎 여러 PDF를 하나로 합치기', 'PDF 합치러 가기 →'),
    'ko/jpg-to-pdf.html': ('🖼️ 사진을 PDF로, 제출 용량까지 한 번에', '사진 PDF로 바꾸러 가기 →'),
    'ko/compress-pdf-for-email.html': ('📧 메일 첨부 한도에 맞게 PDF 줄이기', '메일용 PDF 줄이러 가기 →'),
    'ko/receipt-to-pdf.html': ('🧾 사진 여러 장을 A4 PDF 하나로', '영수증 PDF 만들러 가기 →'),
    'ko/pdf-to-jpg.html': ('🖼️ PDF를 JPG 이미지로, 선명하게', 'PDF JPG로 바꾸러 가기 →'),
    'ko/compress-image.html': ('🖼️ 사진 용량 줄이기, 화질은 그대로', '사진 용량 줄이러 가기 →'),
    'ko/compress-image-to-50kb.html': ('📉 사진을 50KB 이하로', '사진 50KB로 줄이러 가기 →'),
    'ko/compress-pdf-to-2mb.html': ('📄 PDF를 2MB 이하로, 글자는 선명하게', 'PDF 2MB로 줄이러 가기 →'),
    'ko/add-page-numbers.html': ('🔢 PDF에 페이지 번호 한 번에 넣기', '페이지 번호 넣으러 가기 →'),
    'ko/organize.html': ('🗂️ PDF 페이지 순서, 보면서 바꾸기', 'PDF 순서 바꾸러 가기 →'),
    'ko/split.html': ('✂️ PDF에서 필요한 페이지만 나누기', 'PDF 나누러 가기 →'),
}

def box(url, eyebrow, headline, button):
    # inline styles only (Tistory keeps them); site colours: --bg #0b0d12, --accent #46e0a0, button text #062a1c
    return ('<div style="margin:36px auto;max-width:620px;padding:26px 20px 22px;border-radius:18px;background:#0b0d12;text-align:center;">\n'
            f'<p style="margin:0 0 8px;font-size:13px;font-weight:bold;color:#46e0a0;">{eyebrow}</p>\n'
            f'<p style="margin:0 0 18px;font-size:20px;font-weight:bold;line-height:1.45;color:#ffffff;">{headline}</p>\n'
            f'<a href="{url}" target="_blank" rel="noopener" style="display:inline-block;padding:15px 34px;border-radius:12px;'
            f'background:#46e0a0;color:#062a1c;font-size:17px;font-weight:bold;text-decoration:none;">{button}</a>\n'
            '<p style="margin:14px 0 0;font-size:13px;color:#8a97a8;">SlimIO · pdfslimio.com</p>\n'
            '</div>')

def plan(src):
    head = re.match(r'^<!--.*?-->\s*', src, re.S); head = head.group(0) if head else ''
    rows = src[len(head):].split('\n')
    links = [(n, m.group(1)) for n, l in enumerate(rows) for m in re.finditer(r'<a href="(https://pdfslimio\.com/([^"]*))"', l)
             if '/guides/' not in m.group(1) and '/img/' not in m.group(1)]
    page = lambda u: re.split(r'[?#]', u.split('pdfslimio.com/')[1])[0]
    count = collections.Counter(page(u) for _, u in links)
    if not count: return None
    top = max(count.values()); main = next(page(u) for _, u in links if count[page(u)] == top)
    n, url = next((n, u) for n, u in links if page(u) == main)
    # step out of a summary box, list or table, then past a picture right after the block
    for opener, closer in (('<div', '</div>'), ('<blockquote', '</blockquote>'), ('<ul', '</ul>'), ('<ol', '</ol>'), ('<table', '</table>'),
                           ('<p', '</p>')):   # a <p> of several <br> lines (step lists): not between its lines (#06, 2026-11-01)
        start = max((k for k in range(n + 1) if rows[k].lstrip().startswith(opener)), default=None)
        if start is not None and not any(closer in rows[k] for k in range(start, n)):
            n = next(k for k in range(n, len(rows)) if closer in rows[k])
    k = n + 1
    while k < len(rows) and not rows[k].strip(): k += 1
    if k < len(rows) and re.match(r'\s*<p style="text-align:center;?"><img ', rows[k]): n = k
    # rather at the end of that section, so an experiment and its results stay together
    n = next((k - 1 for k in range(n + 1, len(rows)) if rows[k].lstrip().startswith('<h2')), n)
    # box 2 goes above the closing 출처 / ※ lines (Tistory '<p style="color:#888…">출처', Naver '<p>출처:')
    end = k = len(rows)
    while k > 0 and (not rows[k - 1].strip() or re.match(r'\s*<p[^>]*>\s*(출처|※)', rows[k - 1])):
        k -= 1
        if rows[k].strip(): end = k
    if end - n < 12:   # the first link is near the end: put box 1 up front instead, just before the first heading
        n = next(k for k, l in enumerate(rows) if l.lstrip().startswith('<h2')) - 1
    return head, rows, main, url, n, end

def apply(src):
    if EYEBROW_END in src:   # first version: drop the end box
        out = re.sub(r'\n?<div style="margin:36px auto[^\n]*\n<p[^\n]*>' + re.escape(EYEBROW_END) + r'</p>\n.*?</div>\n?', '\n', src, count=1, flags=re.S)
        return out, 'end box removed'
    if EYEBROW in src: return src, 'already has the box'
    p = plan(src)
    if not p: return src, 'no tool link'
    head, rows, main, url, n, end = p
    headline, button = TOOLS[main]
    out = rows[:n + 1] + [box(url, EYEBROW, headline, button)] + rows[n + 1:]
    return head + '\n'.join(out), f'{main} box after line {n + 1}/{len(rows)}'

if __name__ == '__main__':
    dry = '--print' in sys.argv
    for f in [a for a in sys.argv[1:] if a != '--print']:
        new, why = apply(open(f).read())
        print(f, '|', why)
        if not dry and new != open(f).read(): open(f, 'w').write(new)
