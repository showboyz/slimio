# k.sh <win> <orca action args...>  — restore window, verify Chrome is frontmost, then act (up to 3 tries)
W=$1; shift
for n in 1 2 3; do
  S=$(orca computer get-app-state --app com.google.Chrome --window-id $W --json --no-screenshot --restore-window)
  # a page opened elsewhere can land as a new tab in my window and take the keys (2026-11-15, #73): if a 네이버 블로그 tab
  # is there but another tab is in front, click mine first (tblfix.own_tab does the same in Python)
  t=$(printf "%s" "$S" | python3 -c 'import sys,json,re
try: s=json.load(sys.stdin)["result"]["snapshot"]["treeText"]
except Exception: sys.exit()
ts=re.findall(r"^\s*(\d+) 탭 \((selected, )?settable\) (.*?)(?: - 메모리 사용량[^,]*)?, Value: \d", s, re.M)
sel=[x for x in ts if x[1]]; mine=[x for x in ts if "네이버 블로그" in x[2]]
if sel and mine and "네이버 블로그" not in sel[0][2]: print(mine[0][0])')
  [ -n "$t" ] && { orca computer click --app com.google.Chrome --window-id $W --element-index $t --no-screenshot >/dev/null; sleep 1; }
  F=$(osascript -e 'tell application "System Events" to get name of first application process whose frontmost is true')
  if [ "$F" = "Google Chrome" ]; then orca computer "$@" --app com.google.Chrome --window-id $W --json --no-screenshot | python3 -c 'import json,sys;d=json.load(sys.stdin);print("ok" if d.get("ok",True) else "FAIL "+str((d.get("error") or {}).get("code")))'; exit 0; fi
  sleep 0.7
done
echo "ABORT front=$F"; exit 1
