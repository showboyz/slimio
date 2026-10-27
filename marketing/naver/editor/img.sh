# usage: img.sh <editor-win> <abs-path>
W=$1; P=$2; T=$(cd "$(dirname "$0")" && pwd)
oc(){ orca computer "$@" --app com.google.Chrome --json --no-screenshot; }
st(){ oc get-app-state --window-id $1 ${2:-} | python3 -c 'import json,sys;print(json.load(sys.stdin)["result"]["snapshot"]["treeText"])'; }
oc get-app-state --window-id $W --restore-window >/dev/null
oc click --window-id $W --x 275 --y 119 >/dev/null; sleep 2.5
DL=$(orca computer list-windows --app com.google.Chrome --json | python3 -c 'import json,sys;d=json.load(sys.stdin);print(([w["id"] for w in d["result"]["windows"] if w["title"]=="열기"] or [""])[0])')
[ -z "$DL" ] && { echo "no dialog"; exit 1; }
for n in 1 2; do
  st $DL --restore-window >/dev/null; sleep 1
  oc hotkey --window-id $DL --key CmdOrCtrl+Shift+G | python3 -c 'import json,sys;d=json.load(sys.stdin);print("hotkey",d.get("ok"),d.get("error",{}).get("code"))'
  sleep 1
  F=$(st $DL | grep -o -E '^\s*[0-9]+ 텍스트 필드 \(settable\), Value: /' | grep -o -E '[0-9]+' | head -1)
  [ -n "$F" ] && break
done
[ -z "$F" ] && { echo "no path field"; exit 1; }
oc set-value --window-id $DL --element-index $F --value "$P" >/dev/null
st $DL --restore-window >/dev/null
oc press-key --window-id $DL --key Return | python3 -c 'import json,sys;d=json.load(sys.stdin);print("return",d.get("ok"),d.get("error",{}).get("code"))'; sleep 1.2
B=$(st $DL | grep -o -E '^\s*[0-9]+ 버튼 열기' | grep -o -E '[0-9]+' | head -1)
[ -z "$B" ] && { echo "no open button"; exit 1; }
oc click --window-id $DL --element-index $B >/dev/null; sleep 4
st $W | grep -E "이미지 $(basename $P)|focused UI"
