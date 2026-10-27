import json,subprocess,sys,re,time
W=sys.argv[1]; url=sys.argv[2]
def run(*a): return json.loads(subprocess.run(["orca","computer",*a,"--app","com.google.Chrome","--window-id",W,"--json","--no-screenshot"],capture_output=True,text=True).stdout)
t=run("get-app-state")["result"]["snapshot"]["treeText"]
i=re.search(r"(\d+) 텍스트 필드 \(settable\) 주소창",t).group(1)
print(run("set-value","--element-index",i,"--value",url).get("ok"))
print(run("click","--element-index",i).get("ok"))
print(run("press-key","--key","Return").get("ok"))
