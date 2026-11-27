# parse.py <tree.txt>… : print the Path, Referrer, Browser and Country tables from saved Umami overview trees
import sys,re
for f in sys.argv[1:]:
    t=open(f).read()
    m=re.search(r'container, Text: (Visitors[^\n]*)',t); print('==',f.split('/')[-1], m.group(1) if m else '')
    # Orca 1.4.274 (11/26) prints static text as '<n> 텍스트 X' instead of ', Value: X'; read both
    vals=re.findall(r'(?:Value: |^\s*\d+ 텍스트 )(.*)$',t,re.M)
    # sections: after header 'Path'/'Referrer'/'Browser'/'Country' + 'Visitors', triples of name,count,pct
    for hdr in ['Path','Referrer','Browser','Country']:
        i=next((k for k in range(len(vals)-1) if vals[k]==hdr and vals[k+1]=='Visitors'),None)   # not the filter bar's 'Path'
        if i is None: continue
        out=[]; j=i+2
        while j+2<len(vals) and re.fullmatch(r'\d+',vals[j+1]) and re.fullmatch(r'\d+%',vals[j+2]):
            out.append(f'{vals[j]} {vals[j+1]}'); j+=3
        print(' ',hdr+':',' | '.join(out))
