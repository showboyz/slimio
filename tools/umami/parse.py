# parse.py <tree.txt>… : print the Path, Referrer, Browser and Country tables from saved Umami overview trees
import sys,re
for f in sys.argv[1:]:
    t=open(f).read()
    m=re.search(r'container, Text: (Visitors[^\n]*)',t); print('==',f.split('/')[-1], m.group(1) if m else '')
    vals=re.findall(r'Value: (.*)',t)
    # sections: after header 'Path'/'Referrer'/'Browser'/'Country' + 'Visitors', triples of name,count,pct
    for hdr in ['Path','Referrer','Browser','Country']:
        try: i=vals.index(hdr)
        except ValueError: continue
        out=[]; j=i+2
        while j+2<len(vals) and re.fullmatch(r'\d+',vals[j+1]) and re.fullmatch(r'\d+%',vals[j+2]):
            out.append(f'{vals[j]} {vals[j+1]}'); j+=3
        print(' ',hdr+':',' | '.join(out))
