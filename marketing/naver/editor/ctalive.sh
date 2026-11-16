#!/bin/bash
# ctalive.sh <NN:logNo>... : take the button picture out of these published posts (ctaoff.py live), one after another in my
# own window, stopping at the first failure. Owner, 2026-11-16: '2편 시험해봐' (HANDOFF 2-80) — the posts that went out
# with the button and dropped out of Naver search: do they come back without it? Everything goes to ctalive/log.txt.
E=$(cd "$(dirname "$0")" && pwd); R=$E/ctalive; C=${TMPDIR:-/tmp}/ctalive_clip
mkdir -p $R; log() { echo "$(date '+%m-%d %H:%M') $*" | tee -a $R/log.txt; }
mkdir -p $C && osascript -l JavaScript $E/clipsave.js $C >/dev/null 2>&1
W=$(bash $E/win_open.sh 'https://blog.naver.com/todayz777' 2>&1 | tail -1); log "window $W"
case "$W" in ''|*[!0-9]*) log "STOPPED no window of my own"; osascript -l JavaScript $E/cliprestore.js $C >/dev/null 2>&1; exit 1;; esac
ok=1
for x in "$@"; do
  nn=${x%%:*}; no=${x#*:}
  r=$(cd $E && python3 ctaoff.py $W $nn live $no 2>&1 | tee -a $R/log.txt | tail -1); log "#$nn $no: $r"
  case "$r" in *SAVED*) ;; *) ok=0; break;; esac
done
bash $E/win_close.sh $W 2>&1 | tee -a $R/log.txt
osascript -l JavaScript $E/cliprestore.js $C >/dev/null 2>&1; bash $E/guard.sh done
[ $ok = 1 ] && log "done" || log "STOPPED"
