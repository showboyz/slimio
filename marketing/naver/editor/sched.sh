# sched.sh <win> <YYYY-MM-DD> <HH> — schedule for that date and hour: '다음 달' as many times as the month is ahead
# of this month, then the day button by element (sched11.sh is the older next-month-only version)
W=$1; DATE=$2; HH=$3; T=$(cd "$(dirname "$0")" && pwd)
DAY=$((10#${DATE:8:2})); AHEAD=$(( (10#${DATE:0:4} - $(date +%Y)) * 12 + 10#${DATE:5:2} - 10#$(date +%m) ))
idx(){ orca computer get-app-state --app com.google.Chrome --window-id $W --json --no-screenshot | python3 -c "import json,sys,re;t=json.load(sys.stdin)['result']['snapshot']['treeText'];m=re.search(r'(\d+) $1',t,re.M);print(m.group(1) if m else '')"; }
R=$(idx '라디오 버튼 \(settable\) 예약'); python3 $T/c.py $W '-' click --element-index $R >/dev/null; sleep 1
DF=$(idx '텍스트 필드, Value: 2026'); python3 $T/c.py $W '-' click --element-index $DF >/dev/null; sleep 1
for ((a=0; a<AHEAD; a++)); do  # not seq: on macOS 'seq 1 0' counts down
  N=$(idx '버튼 다음 달'); [ -z "$N" ] && { echo "NO NEXT MONTH"; exit 1; }
  python3 $T/c.py $W '-' click --element-index $N >/dev/null; sleep 1
done
D=$(idx "버튼 $DAY\$")
if [ -n "$D" ]; then python3 $T/c.py $W '-' click --element-index $D >/dev/null; sleep 1
else
  # the panel cuts the calendar off after the 14th: Tab from '다음 달' to the day button, then Return
  focus(){ orca computer get-app-state --app com.google.Chrome --window-id $W --json --no-screenshot | python3 -c "import json,sys;t=json.load(sys.stdin)['result']['snapshot']['treeText'];print(t.split('focused UI element is')[-1].strip())"; }
  for n in $(seq 1 40); do
    F=$(focus); case "$F" in *"버튼 $DAY."*|*"버튼 $DAY") break;; esac
    bash $T/k.sh $W press-key --key Tab >/dev/null; sleep 0.3
  done
  case "$(focus)" in *"버튼 $DAY."*|*"버튼 $DAY") ;; *) echo "DAY NOT FOUND"; exit 1;; esac
  bash $T/k.sh $W press-key --key Return >/dev/null; sleep 1
fi
for pair in "시간:$HH" "분:00"; do k=${pair%%:*}; v=${pair##*:}
  I=$(idx "팝업 버튼 예약 발행 $k 선택"); python3 $T/c.py $W '-' click --element-index $I >/dev/null; sleep 0.8
  FR=$(osascript -e 'tell application "System Events" to get name of first application process whose frontmost is true')
  [ "$FR" = "Google Chrome" ] || { echo "ABORT front=$FR"; exit 1; }
  osascript -e "tell application \"System Events\" to keystroke \"$v\"" -e 'delay 0.4' -e 'tell application "System Events" to key code 36'; sleep 1
done
orca computer get-app-state --app com.google.Chrome --window-id $W --json --no-screenshot | python3 -c "import json,sys,re;t=json.load(sys.stdin)['result']['snapshot']['treeText'];print([l.strip() for l in t.split('\n') if re.search(r'Value: 2026\.|예약 발행 (시간|분) 선택',l)])"
