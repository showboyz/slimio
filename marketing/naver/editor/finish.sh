# finish.sh <win> <YYYY-MM-DD> <HH> <tag...> : publish panel → tags → schedule that date HH:00 → verify → 발행
# (finish11.sh is the older November-08:00-only version)
W=$1; DATE=$2; HH=$3; shift 3; T=$(cd "$(dirname "$0")" && pwd)
YMD="${DATE:0:4}. ${DATE:5:2}. ${DATE:8:2}"
bash $T/k.sh $W click --x 1807 --y 68 >/dev/null; sleep 2
for t in "$@"; do python3 $T/tag1.py "$t" $W || exit 1; done
bash $T/sched.sh $W $DATE $HH | tail -1
orca computer get-app-state --app com.google.Chrome --window-id $W --json --no-screenshot | python3 -c "
import json,sys,re
t=json.load(sys.stdin)['result']['snapshot']['treeText']
tags=re.findall(r'\d+ container (\S+)\n',t.split('태그 편집')[1].split('발행 시간')[0])
ok=('IT·컴퓨터' in t and re.search(r'전체공개, Value: 1',t) and re.search(r'예약, Value: 1',t) and 'Value: $YMD' in t and re.search(r'시간 선택, Value: $HH',t) and re.search(r'분 선택, Value: 00',t) and len(tags)==$#)
print('tags',len(tags),'CHECK', 'OK' if ok else 'FAIL'); sys.exit(0 if ok else 1)" || exit 1
B=$(python3 $T/c.py $W '버튼 발행$' get-app-state | grep -o -E '^[0-9]+ 버튼 발행' | tail -1 | cut -d' ' -f1)
python3 $T/c.py $W '-' click --element-index $B >/dev/null; sleep 5
python3 $T/c.py $W '주소창' get-app-state | grep 주소창
