import json,subprocess,sys,re
# usage: c.py <winid> <pattern|-> <orca computer args...>
W=sys.argv[1]; pat=sys.argv[2]; args=sys.argv[3:]
out=subprocess.run(["orca","computer",*args,"--app","com.google.Chrome","--window-id",W,"--json"],capture_output=True,text=True).stdout
d=json.loads(out); r=d.get("result") or {}
if not d.get("ok",True) or "snapshot" not in r:
    print(json.dumps(d,ensure_ascii=False)[:600]); 
    if "snapshot" not in r: sys.exit()
print("ok",d.get("ok"),"verif",r.get("verification"),"shot",r.get("screenshot",{}).get("path"))
for l in r["snapshot"]["treeText"].split("\n"):
    if pat!="-" and (re.search(pat,l) or "focused UI" in l): print(l.strip()[:170])
