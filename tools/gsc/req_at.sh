#!/bin/bash
# req_at.sh <YYYY-mm-dd> <HH:MM> <url>... : at that date and time (KST) open my own GSC window on the /u/0/ address (todays777 since 11/17; it was /u/1/ before — check the page shows todays777)
# (todays777), request indexing with req_u1.py (stops on Google's quota or "try again later"), then close the window.
# Never use req.py for this: importing it starts requests in a window of its own.
cd "$(dirname "$0")"; E=../../marketing/naver/editor
day=$1; at=$2; shift 2
now=$(date +%s); then=$(date -j -f "%Y-%m-%d %H:%M" "$day $at" +%s) || exit 1
[ "$then" -gt "$now" ] && sleep $((then - now))
W=$(bash $E/win_open.sh "https://search.google.com/u/0/search-console/inspect?resource_id=sc-domain%3Apdfslimio.com" | tail -1)
case "$W" in ''|*[!0-9]*) echo "no window ($W)"; exit 1;; esac
echo "window $W"
sleep 5
python3 -u req_u1.py "$W" "$@"
until bash $E/guard.sh >/dev/null 2>&1; do sleep 30; done
# win_close.sh keeps a window whose tabs are not Naver blog tabs (it would take someone else's tab with
# it), so a GSC window stayed open. Close it here only when its one tab is the Search Console page.
T=$(orca computer get-app-state --app com.google.Chrome --window-id "$W" --no-screenshot 2>/dev/null)
n=$(echo "$T" | grep -cE '^[[:space:]]*[0-9]+ 탭 \(')
c=$(echo "$T" | grep -E '^[[:space:]]*[0-9]+ 닫기 버튼$' | head -1 | sed -E 's/^[[:space:]]*([0-9]+).*/\1/')
if [ "$n" = 1 ] && echo "$T" | grep -qiE '탭 \(.*(Search Console|URL inspection|Inspect|Performance)' && [ -n "$c" ]; then
  orca computer click --app com.google.Chrome --window-id "$W" --element-index "$c" --no-screenshot >/dev/null 2>&1
  sleep 2; bash $E/leavedlg.sh >/dev/null
  case " $(orca computer list-windows --app com.google.Chrome --json | python3 -c "import sys,json; print(' '.join(str(w['id']) for w in json.load(sys.stdin)['result']['windows']))") " in
    *" $W "*) echo "CHECK window $W still open";; *) echo "window $W closed";; esac
else echo "window $W left open: $n tab(s), not only Search Console"; fi
bash $E/guard.sh done
