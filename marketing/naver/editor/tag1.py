import json,subprocess,sys,re,time
W=sys.argv[2] if len(sys.argv)>2 else "90084"; tag=sys.argv[1]
def run(*a): return json.loads(subprocess.run(["orca","computer",*a,"--app","com.google.Chrome","--window-id",W,"--json","--no-screenshot"],capture_output=True,text=True).stdout)
def tree(): return run("get-app-state","--restore-window")["result"]["snapshot"]["treeText"]
def front(): return subprocess.run(["osascript","-e",'tell application "System Events" to get name of first application process whose frontmost is true'],capture_output=True,text=True).stdout.strip()
t=tree()
if re.search(r"\d+ container "+re.escape(tag)+r"\n",t): print("already",tag); sys.exit()
c=re.search(r"(\d+) 콤보 상자 \(settable\)[^\n]*Placeholder: 태그 입력",t).group(1)
run("click","--element-index",c); time.sleep(0.4)
t=run("get-app-state")["result"]["snapshot"]["treeText"]
if "콤보 상자 (settable)" not in t.split("focused UI element is")[-1]: print("FAIL focus",tag); sys.exit(1)
c=re.search(r"(\d+) 콤보 상자 \(settable\)[^\n]*Placeholder: 태그 입력",t).group(1)
r=run("set-value","--element-index",c,"--value",tag); 
for attempt in range(3):
    run("get-app-state","--restore-window")
    if front()!="Google Chrome": time.sleep(0.5); continue
    run("press-key","--key","Return"); time.sleep(0.8)
    t=run("get-app-state")["result"]["snapshot"]["treeText"]
    if re.search(r"\d+ container "+re.escape(tag)+r"\n",t):
        print("added",tag); sys.exit()
print("FAIL",tag,"front=",front()); sys.exit(1)
