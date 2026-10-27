# small.sh <win> <image-file-name> : select image, set 작게 + 가운데 정렬
W=$1; N=$2; T=$(cd "$(dirname "$0")" && pwd)
I=$(orca computer get-app-state --app com.google.Chrome --window-id $W --json --no-screenshot | python3 -c "import json,sys,re;t=json.load(sys.stdin)['result']['snapshot']['treeText'];m=re.search(r'(\d+) 이미지 '+re.escape('$N'),t);print(m.group(1) if m else '')")
[ -z "$I" ] && { echo "no image $N"; exit 1; }
python3 $T/c.py $W '-' click --element-index $I >/dev/null; sleep 0.8
bash $T/k.sh $W click --x 589 --y 168 >/dev/null; sleep 0.8
bash $T/k.sh $W click --x 292 --y 168 >/dev/null; sleep 0.8
echo done
