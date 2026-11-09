#!/bin/bash
# ctaday.sh <HH:MM> [count] : wait until the next HH:MM, then (owner said '버튼빼자' 2026-11-09) take the button out of the next
# <count> (default 4) reserved posts in ctaday/res.txt that are not in ctaday/done.txt, each checked by a second ctaoff run
# that must find 0 link badges. Before that, log the own-title search position of the 8 newest published posts. Stops at
# the first failure. Everything goes to ctaday/log.txt. Runs once; start it again for the next day.
# res.txt is listres.py's list of the reserved posts ("time<TAB>title<TAB>draft NN"); done.txt has one NN per line.
E=$(cd "$(dirname "$0")" && pwd); R=$E/ctaday; C=${TMPDIR:-/tmp}/ctaday_clip
N=${2:-4}; log() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $R/log.txt; }
now=$(date +%s); at=$(date -j -f '%Y-%m-%d %H:%M' "$(date '+%Y-%m-%d') $1" +%s); [ $at -le $now ] && at=$((at + 86400))
sleep $((at - now))
log "search check:"; python3 $E/recent.py 8 | tee -a $R/log.txt
touch $R/done.txt
soon=$(date -v+2H '+%Y.%m.%d %H:%M')
todo=$(awk -F'\t' -v soon="$soon" '$1 > soon {print $3" "$1}' $R/res.txt | while read nn d h; do grep -qx "$nn" $R/done.txt || echo "$nn $d ${h%%:*}"; done | head -$N)
[ -n "$todo" ] || { log "nothing left"; exit 0; }
mkdir -p $C && osascript -l JavaScript $E/clipsave.js $C >/dev/null 2>&1
W=$(bash $E/win_open.sh 'https://blog.naver.com/todayz777' 2>&1 | tail -1); log "window $W"
ok=1
while read nn d h; do
  r=$(cd $E && python3 ctaoff.py $W $nn $d $h 2>&1 | tail -1); log "#$nn $d $h: $r"
  case "$r" in *SAVED*) ;; *) ok=0; break;; esac
  v=$(cd $E && python3 ctaoff.py $W $nn $d $h 2>&1 | tail -1)
  case "$v" in *"0 link badges"*) echo $nn >> $R/done.txt; log "#$nn verified (0 buttons)";; *) log "#$nn CHECK: $v"; ok=0; break;; esac
done <<< "$todo"
python3 $E/listres.py $W $R/res_now.txt >/dev/null 2>&1; # the posts still ahead must be exactly the ones in res.txt (published ones drop off the list)
cut=$(date '+%Y.%m.%d %H:%M'); awk -F'\t' -v c="$cut" '$1 > c' $R/res.txt | diff -q - $R/res_now.txt >/dev/null && log "reserved list unchanged" || log "CHECK reserved list differs"
bash $E/win_close.sh $W 2>&1 | tee -a $R/log.txt
osascript -l JavaScript $E/cliprestore.js $C >/dev/null 2>&1; bash $E/guard.sh done
[ $ok = 1 ] && log "done $(wc -l < $R/done.txt | tr -d ' ') total" || log "STOPPED"
