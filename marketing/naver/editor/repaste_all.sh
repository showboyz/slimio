#!/bin/bash
# repaste_all.sh [max] : paste the reserved posts in ctaday/res.txt again in chunk.py's current layout (repaste.py, owner:
# '가독성 … 정돈 해보자' 2026-11-15), earliest first, at most [max] (default all). Skips posts due within 2 h and those in
# repaste/done.txt, stops at the first failure, and starts no post between 04:30 and 05:45 so it keeps clear of
# ctaday.sh's 05:00 run. A repasted post has no SlimIO button any more, so its NN also goes into ctaday/done.txt.
# Own window, clipboard saved and restored, everything logged to repaste/log.txt.
E=$(cd "$(dirname "$0")" && pwd); R=$E/repaste; C=${TMPDIR:-/tmp}/repaste_clip
N=${1:-999}; log() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $R/log.txt; }
mkdir -p $R $C; touch $R/done.txt
osascript -l JavaScript $E/clipsave.js $C >/dev/null 2>&1
W=$(bash $E/win_open.sh 'https://blog.naver.com/todayz777' 2>&1 | tail -1); log "window $W"
count=0; ok=1
while [ $count -lt $N ]; do
  hm=$(date +%H%M)
  if [ $hm -ge 0430 ] && [ $hm -lt 0545 ]; then
    log "pause until 05:45 (ctaday)"; sleep $(( $(date -j -f '%Y-%m-%d %H:%M' "$(date '+%Y-%m-%d') 05:45" +%s) - $(date +%s) )); continue
  fi
  soon=$(date -v+2H '+%Y.%m.%d %H:%M')
  next=$(awk -F'\t' -v soon="$soon" '$1 > soon {print $3" "$1}' $E/ctaday/res.txt | while read nn d h; do grep -qx "$nn" $R/done.txt || echo "$nn $d ${h%%:*}"; done | head -1)
  [ -n "$next" ] || { log "nothing left"; break; }
  read nn d h <<< "$next"
  r=$(cd $E && python3 repaste.py $W $nn $d $h $C/nb_$nn 2>&1 | tail -1); log "#$nn $d $h: $r"
  case "$r" in *SAVED*) echo $nn >> $R/done.txt; grep -qx "$nn" $E/ctaday/done.txt || echo $nn >> $E/ctaday/done.txt;; *) ok=0; break;; esac
  count=$((count + 1))
done
python3 $E/listres.py $W $R/res_now.txt >/dev/null 2>&1   # the posts still ahead must be exactly the ones in res.txt
cut=$(date '+%Y.%m.%d %H:%M'); awk -F'\t' -v c="$cut" '$1 > c' $E/ctaday/res.txt | diff -q - $R/res_now.txt >/dev/null && log "reserved list unchanged" || log "CHECK reserved list differs"
bash $E/win_close.sh $W 2>&1 | tee -a $R/log.txt
osascript -l JavaScript $E/cliprestore.js $C >/dev/null 2>&1; bash $E/guard.sh done
[ $ok = 1 ] && log "done $(wc -l < $R/done.txt | tr -d ' ') total" || log "STOPPED"
