# post.sh <win> <nbdir> <title> <small-img|-> <img1> [img2 ...]   (chunk cN follows imgN)
W=$1; D=$2; TITLE=$3; SMALL=$4; shift 4; T=$(cd "$(dirname "$0")" && pwd)
B=$(cd "$T/../../../public/img/blog" && pwd)
bash $T/k.sh $W click --x 731 --y 295 >/dev/null || exit 1
printf '%s' "$TITLE" | pbcopy; bash $T/k.sh $W hotkey --key CmdOrCtrl+V >/dev/null || exit 1; sleep 0.6
bash $T/k.sh $W click --x 823 --y 453 >/dev/null; sleep 0.5
n=0
for img in "$@"; do
  n=$((n+1))
  bash $T/img.sh $W $B/$img | grep -E '이미지|no ' || exit 1
  osascript -l JavaScript $D/setclip.js "$D/c$n.html" "$D/c$n.txt" >/dev/null
  bash $T/k.sh $W hotkey --key CmdOrCtrl+V >/dev/null || exit 1; sleep 2.5
done
[ "$SMALL" != "-" ] && bash $T/small.sh $W $SMALL
orca computer get-app-state --app com.google.Chrome --window-id $W --json | python3 -c 'import json,sys;d=json.load(sys.stdin);print(d["result"]["screenshot"]["path"])'
