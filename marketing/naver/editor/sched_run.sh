#!/bin/bash
# sched_run.sh "NN YYYY-MM-DD HH" … : when the owner is away (guard.sh), back up the clipboard, open my own Chrome
# window, schedule each draft with newpost.py (chunks in $TMPDIR/slimio_nbNN), read the 예약 count once more, restore
# the clipboard. The window is left open on an empty editor; close it with its 닫기 버튼 (then '버튼 나가기').
E=$(cd "$(dirname "$0")" && pwd)
B=${TMPDIR:-/tmp}/slimio_sched_clipboard
wins() { orca computer list-windows --app com.google.Chrome --json | python3 -c "import sys,json; d=json.load(sys.stdin); r=d.get('result',d); print(' '.join(str(w['id']) for w in r.get('windows',[])))"; }
until bash $E/guard.sh >/dev/null; do sleep 30; done
echo "owner away $(date +%H:%M:%S)"
osascript -l JavaScript $E/clipsave.js $B || { echo "FAIL clipboard backup"; exit 1; }
before=" $(wins) "
open -na "Google Chrome" --args --new-window https://blog.naver.com/todayz777
sleep 8
W=""; for w in $(wins); do case "$before" in *" $w "*) ;; *) W=$w;; esac; done
[ -n "$W" ] || { echo "FAIL no new window"; osascript -l JavaScript $E/cliprestore.js $B; exit 1; }
echo "window $W"
bash $E/guard.sh done
for q in "$@"; do
  set -- $q; n=$1; d=$2; h=$3
  python3 $E/newpost.py $W $n $d $h ${TMPDIR:-/tmp}/slimio_nb$n </dev/null || { echo "STOP at $n"; break; }
  sleep 3
done
(cd $E && python3 -c "
import tblfix as tf, time, re
from tblfix_sched import go, wait_for, leave_unsaved, EDITOR
tf.W='$W'
if tf.guard(): go(EDITOR); tf.done(); time.sleep(5); t=wait_for(r'예약 발행 \d+ 건', 30) or ''; m=re.search(r'예약 발행 (\d+) 건', t); print('RESERVED COUNT', m.group(1) if m else '?'); leave_unsaved(); tf.done()
")
echo "WINDOW $W left open"
osascript -l JavaScript $E/cliprestore.js $B && echo "clipboard restored"
