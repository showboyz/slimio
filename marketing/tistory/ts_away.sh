#!/bin/bash
# ts_away.sh "<script> <args…>" … : the whole Tistory round in one go, for when nobody has a window open for it.
# Waits until the owner is away (guard.sh), backs up the clipboard, opens my own Chrome window on the Naver blog (so
# tblfix/win_close see a tab of mine), runs the jobs with trun.sh (e.g. "tnew.py 27-stamp-background.html 2026-12-01 08"),
# then takes the tab back to the blog, closes the window with win_close.sh and restores the clipboard.
T=$(cd "$(dirname "$0")" && pwd); E=$T/../naver/editor
export PATH="$E/bin:$PATH"   # Orca prints English role names; bin/orca turns them back into Korean (axko.py)
B=${TMPDIR:-/tmp}/slimio_ts_clipboard
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
bash $T/trun.sh $W "$@"; rc=$?
(cd $E && python3 -c "
import tblfix as tf, time
from tblfix_sched import go
tf.W = '$W'
if tf.guard(): go('https://blog.naver.com/todayz777'); tf.done(); time.sleep(4)
")
bash $E/guard.sh >/dev/null && { bash $E/win_close.sh $W; bash $E/guard.sh done; } || echo "WINDOW $W left open (owner came back)"
osascript -l JavaScript $E/cliprestore.js $B
exit $rc
