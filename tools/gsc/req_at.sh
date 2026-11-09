#!/bin/bash
# req_at.sh <YYYY-mm-dd> <HH:MM> <url>... : at that date and time (KST) open my own GSC window on the /u/1/ address
# (todays777), request indexing with req_u1.py (stops on Google's quota or "try again later"), then close the window.
# Never use req.py for this: it opens the u/0 address.
cd "$(dirname "$0")"; E=../../marketing/naver/editor
day=$1; at=$2; shift 2
now=$(date +%s); then=$(date -j -f "%Y-%m-%d %H:%M" "$day $at" +%s) || exit 1
[ "$then" -gt "$now" ] && sleep $((then - now))
W=$(bash $E/win_open.sh "https://search.google.com/u/1/search-console/inspect?resource_id=sc-domain%3Apdfslimio.com" | tail -1)
case "$W" in ''|*[!0-9]*) echo "no window ($W)"; exit 1;; esac
echo "window $W"
sleep 5
python3 -u req_u1.py "$W" "$@"
until bash $E/guard.sh >/dev/null 2>&1; do sleep 30; done
bash $E/win_close.sh "$W"
bash $E/guard.sh done
