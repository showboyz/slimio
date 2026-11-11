# usage: img.sh <editor-win> <abs-path> : put one picture into the post at the caret.
# Since the orca update of 2026-11-10 the 사진 button's file dialog is a sheet orca cannot focus, so its Cmd+Shift+G
# went to the page instead (Chrome's 'find previous'). The file is now put on the clipboard as Finder's Copy does
# (fileclip.js) and pasted; the editor uploads it under its own file name, so the '이미지 <name>' check stays the same
# (tested 2026-11-12 with opic-score-hero.jpg). The caller backs up and restores the clipboard.
W=$1; P=$2; T=$(cd "$(dirname "$0")" && pwd)
st(){ orca computer get-app-state --app com.google.Chrome --window-id $W --json --no-screenshot | python3 -c 'import json,sys;print(json.load(sys.stdin)["result"]["snapshot"]["treeText"])'; }
osascript -l JavaScript $T/fileclip.js "$P" >/dev/null || { echo "no clipboard file"; exit 1; }
r=$(bash $T/k.sh $W hotkey --key CmdOrCtrl+V); [ "$r" = ok ] || { echo "no paste $r"; exit 1; }
for n in 1 2 3 4 5 6 7 8 9 10; do
  sleep 1.5; L=$(st | grep -E "이미지 $(basename "$P")") && break
done
[ -n "$L" ] && echo "$L" || echo "no picture $(basename "$P")"
