# pick.sh <chrome-win> <abs-path> : press '파일 선택' (any label after it) and pick the file in the 열기 dialog; on Tistory the dialog is a sheet whose 열기 button tnew.py presses if this can't
# (Cmd+Shift+G path field, as editor/img.sh does for the Naver editor).
# Since 2026-11-26 (Orca 1.4.274) the 열기 sheet shows up in the tree of the Chrome window <win>, and input sent to the 열기
# window fails ('window_not_focused') while a background key to <win> goes to Chrome (Cmd+Shift+G opened its find bar).
# So every key and click here goes to <win> in the foreground (--restore-window); the owner is away whenever this runs
# (trun.sh / guard.sh). If a sheet or its path field is already open (a run that stopped here), it is used as it is.
W=$1; P=$2
oc(){ orca computer "$@" --app com.google.Chrome --json --no-screenshot; }
st(){ oc get-app-state --window-id $1 ${2:-} | python3 -c 'import json,sys;print(json.load(sys.stdin)["result"]["snapshot"]["treeText"])'; }
dlg(){ orca computer list-windows --app com.google.Chrome --json | python3 -c 'import json,sys;d=json.load(sys.stdin);print(([w["id"] for w in d["result"]["windows"] if w["title"]=="열기"] or [""])[0])'; }
field(){ st $W | grep -v -E '주소창|찾기' | grep -o -E '^\s*[0-9]+ (텍스트 필드|콤보 상자) \(settable\)[^,]*, Value: [/~]' | grep -o -E '[0-9]+' | head -1; }
if [ -z "$(dlg)" ]; then
  I=$(st $W --restore-window | grep -o -E '^\s*[0-9]+ 버튼 파일 선택(: .*)?$' | grep -o -E '[0-9]+' | head -1)
  [ -z "$I" ] && { echo "no 파일 선택 button"; exit 1; }
  oc click --window-id $W --element-index $I >/dev/null; sleep 2.5
  [ -z "$(dlg)" ] && { echo "no dialog"; exit 1; }
fi
F=$(field)
for n in 1 2; do
  [ -n "$F" ] && break
  oc hotkey --window-id $W --key CmdOrCtrl+Shift+G --restore-window >/dev/null; sleep 1.5
  F=$(field)
done
[ -z "$F" ] && { echo "no path field"; exit 1; }
oc set-value --window-id $W --element-index $F --value "$P" >/dev/null; sleep 0.5
oc press-key --window-id $W --key Return --restore-window >/dev/null; sleep 1.5
[ -z "$(dlg)" ] && { sleep 3; echo picked; exit 0; }   # Return on a file path can choose it and close the sheet at once
B=$(st $W | grep -o -E '^\s*[0-9]+ 버튼 열기$' | grep -o -E '[0-9]+' | tail -1)
[ -z "$B" ] && { echo "no open button"; exit 1; }
oc click --window-id $W --element-index $B --restore-window >/dev/null; sleep 5
[ -n "$(dlg)" ] && { echo "dialog still open"; exit 1; }
echo picked
