#!/bin/bash
# um_away.sh <outdir> <name> <url> [<name> <url>]… : wait until the owner is away (guard.sh), open my own Chrome window
# (on the blog, so tblfix sees a tab of mine), save each Umami page's tree with umget.py to <outdir>/<name>.txt and print
# its tables (parse.py), go back to the blog and close the window with win_close.sh. The clipboard is backed up first.
# Umami filters go in the url: &referrer=eq.pdfaid.com, &path=eq.%2Fko%2Fstamp-image.html, &country=eq.SG.
# Other sites: set PAT to a regex that shows the page has loaded, e.g. PAT='(Total impressions|Not indexed)' for GSC.
E=/Users/home/orca/projects/slimio/marketing/naver/editor
D=$(cd "$(dirname "$0")" && pwd)
export PATH="$E/bin:$PATH"   # Orca 1.4.274 prints English role names; bin/orca turns them back into Korean (axko.py)
out=$1; shift
B=${TMPDIR:-/tmp}/slimio_um_clipboard
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
while [ $# -ge 2 ]; do
  python3 $D/umget.py $W "$out/$1.txt" "$2" ${PAT:+"$PAT"} || { echo "STOP at $1"; break; }
  python3 $D/parse.py "$out/$1.txt"
  shift 2
done
(cd $E && python3 -c "
import tblfix as tf, time
from tblfix_sched import go
tf.W = '$W'
if tf.guard(): go('https://blog.naver.com/todayz777'); tf.done(); time.sleep(4)
")
bash $E/guard.sh >/dev/null && { bash $E/win_close.sh $W; bash $E/guard.sh done; } || echo "WINDOW $W left open (owner came back)"
osascript -l JavaScript $E/cliprestore.js $B
