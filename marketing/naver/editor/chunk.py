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
for i,(im,b) in enumerate(zip(imgs,bodies),1):
    b=b.strip()
    open(f'{out}/c{i}.html','w').write(b); open(f'{out}/c{i}.txt','w').write(txt(b))
    # h2 right before the next IMG would leak heading style
    if i<len(imgs) and re.search(r'</h2>\s*$',b): print('WARN h2 before IMG',i+1)
shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)),'setclip.js'),out)
print(out,'images:',' '.join(imgs))
