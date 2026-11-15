import re,sys,html,os,shutil
src,out=sys.argv[1],sys.argv[2]
s=open(src).read()
s=re.sub(r'^<!--.*?-->\s*','',s,flags=re.S)
parts=re.split(r'<!--IMG:([^>]+?)-->',s)
assert parts[0].strip()=='', 'text before first image'
os.makedirs(out,exist_ok=True)
imgs=parts[1::2]; bodies=parts[2::2]
def txt(h):
    h=re.sub(r'<br\s*/?>','\n',h)
    h=re.sub(r'</(p|h2|li|tr|table|ul)>','\n',h)
    h=re.sub(r'</t[dh]>','\t',h)
    h=re.sub(r'<[^>]+>','',h)
    h=html.unescape(h)
    return re.sub(r'\n{3,}','\n\n',re.sub(r'[ \t]+\n','\n',h)).strip()+'\n'
# Naver's editor drops a bare table's look (every cell gets border:none, equal widths), so tables
# are pasted with inline borders, a tinted header row and column widths that follow the text length.
# The editor keeps these (tested 2026-10-29: border, background-color, color, width %, text-align).
LINE='1px solid #c9d3df'
def style_table(m):
    t=m.group(0)
    rows=re.findall(r'<tr[^>]*>(.*?)</tr>',t,flags=re.S)
    cells=[re.findall(r'<t([dh])[^>]*>(.*?)</t[dh]>',r,flags=re.S) for r in rows]
    n=max((len(c) for c in cells),default=0)
    plain=lambda h: html.unescape(re.sub(r'<[^>]+>','',h)).strip()
    if n<2: return t
    longest=[max((len(plain(c[k][1])) for c in cells if len(c)==n),default=1) or 1 for k in range(n)]
    w=[min(max(x/sum(longest),0.2),0.6) for x in longest]; w=[round(100*x/sum(w)) for x in w]
    def cell(k,tag,body,head):
        st=f'width:{w[k]}%;border:{LINE};padding:8px;'+('background-color:#eef4fb;color:#1f3a5f;text-align:center;' if head else '')
        return f'<t{tag} style="{st}">{body}</t{tag}>'
    out=[]
    for c in cells:
        head=all(tag=='h' for tag,_ in c)
        out.append('<tr>'+''.join(cell(k,tag,body.strip(),head) for k,(tag,body) in enumerate(c))+'</tr>')
    return f'<table style="border-collapse:collapse;width:100%;border:{LINE}">'+''.join(out)+'</table>'
# Readability (2026-11-15, owner: '가독성이 좀 떨어지는거 같네 벤치마킹해서 정돈'): next to the top blog-tab posts for our
# queries, ours had no blank line between paragraphs (they average ~28), paragraphs 2-3x longer (avg 55-94 chars, top
# ~36) and h2s that came out as plain bold text glued to the paragraph above. The top posts set headings apart with a
# one-cell table (left bar, tinted cell), which the editor keeps like our other tables. So paragraphs are cut into
# groups of at most 2 sentences (~70 chars, 3 phone lines), blocks get an empty paragraph between them, an h2 becomes
# that heading box and the '⏱ 3줄 요약' paragraph a bordered cell. Drafts stay as written; only the pasted copy changes.
GAP='<p><br></p>'
def visible(h): return html.unescape(re.sub(r'<[^>]+>','',h))
def sentences(h):
    # cut at a space after . ! ? (and any emoji right after it), outside quotes, brackets and inline tags
    out,cur,depth,quote,tags=[],'',0,set(),0
    for tok in re.findall(r'<[^>]+>|[^<]',h):
        if tok.startswith('<'):
            if not tok.startswith('<br'): tags+=-1 if tok.startswith('</') else 1
            cur+=tok; continue
        if tok==' ' and not depth and not quote and tags<=0 and \
           re.search(r"[^\d\s][.!?][\"'”’]*[\s\U0001F000-\U0001FFFF\u2600-\u27BF\uFE0F\u200d]*$",visible(cur)):
            out.append(cur.strip()); cur=''; continue
        if tok in '([': depth+=1
        elif tok in ')]': depth=max(0,depth-1)
        elif tok=='"' or tok=="'" and (tok in quote or not re.search(r'[A-Za-z]$',cur)): quote^={tok}   # not Driver's
        elif tok in '“‘': quote|={tok}
        elif tok in '”’': quote-={'“' if tok=='”' else '‘'}
        cur+=tok
    res=[]
    for s in out+[cur.strip()]:   # an emoji left alone after the full stop ('봤어요. 📝') stays with its sentence
        if res and s and not re.search(r'[\w가-힣]',visible(s)): res[-1]+=' '+s
        elif s: res.append(s)
    return res
def short_paras(inner):
    groups,cur=[],[]
    for s in sentences(inner):
        if cur and (len(cur)==2 or len(visible(' '.join(cur+[s])))>70): groups.append(' '.join(cur)); cur=[]
        cur.append(s)
    return [f'<p>{g}</p>' for g in groups+[' '.join(cur)] if g]
def box(inner,head):
    st=('border:none;border-left:5px solid #1f3a5f;background-color:#eef4fb;padding:12px 14px;' if head else
        f'border:{LINE};background-color:#f7f9fc;padding:14px 16px;')
    return f'<table style="border-collapse:collapse;width:100%;border:none"><tr><td style="width:100%;{st}">{inner}</td></tr></table>'
BLOCK=r'<(p|h2|ul|ol|table)\b[^>]*>(.*?)</\1>'
def tidy(b):
    left=visible(re.sub(r'<!--.*?-->','',re.sub(BLOCK,'',b,flags=re.S),flags=re.S)).strip()
    assert not left, f'text outside p/h2/ul/ol/table would be lost: {left[:60]!r}'
    out=[]
    for m in re.finditer(BLOCK,b,flags=re.S):
        tag,inner=m.group(1),m.group(2).strip()
        if tag=='h2': out.append(box(f'<p><b><span style="font-size:19px;color:#1f3a5f">{inner}</span></b></p>',True))
        elif tag=='p' and '3줄 요약' in visible(inner)[:12]:
            out.append(box(''.join(f'<p>{l.strip()}</p>' for l in re.split(r'<br\s*/?>',inner) if l.strip()),False))
        elif tag=='p' and visible(inner).startswith('출처'):   # the long source list in small grey type
            out.append(f'<p><span style="font-size:13px;color:#8a94a3">{inner}</span></p>')
        elif tag=='p':   # a <br> line (a step '1️⃣ …', a '① …' lead-in) becomes its own paragraph
            out.append(GAP.join(p for l in re.split(r'<br\s*/?>',inner) if l.strip() for p in short_paras(l.strip())))
        else: out.append(m.group(0).strip())
    # no empty paragraph right after a table: the editor's own gap below a table component is enough, and a heading
    # reads as part of the text under it. A chunk still ends in one, so the next picture never goes in after a table.
    s=''.join(o+('' if o.startswith('<table') else GAP) for o in out)
    return s if s.endswith(GAP) else s+GAP
for i,(im,b) in enumerate(zip(imgs,bodies),1):
    b=re.sub(r'<table[^>]*>.*?</table>',style_table,b.strip(),flags=re.S)
    # h2 right before the next IMG would leak heading style
    if i<len(imgs) and re.search(r'</h2>\s*$',b): print('WARN h2 before IMG',i+1)
    b=tidy(b)
    open(f'{out}/c{i}.html','w').write(b); open(f'{out}/c{i}.txt','w').write(txt(b))
shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)),'setclip.js'),out)
print(out,'images:',' '.join(imgs))
