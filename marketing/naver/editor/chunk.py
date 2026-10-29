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
for i,(im,b) in enumerate(zip(imgs,bodies),1):
    b=re.sub(r'<table[^>]*>.*?</table>',style_table,b.strip(),flags=re.S)
    open(f'{out}/c{i}.html','w').write(b); open(f'{out}/c{i}.txt','w').write(txt(b))
    # h2 right before the next IMG would leak heading style
    if i<len(imgs) and re.search(r'</h2>\s*$',b): print('WARN h2 before IMG',i+1)
shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)),'setclip.js'),out)
print(out,'images:',' '.join(imgs))
