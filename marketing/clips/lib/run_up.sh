#!/bin/bash
# run_up.sh "<clip dir> YYYY-MM-DD HH:MM" … : when the owner is away (guard.sh), back up the clipboard, open my own
# Chrome window on Clip Creator, book each clip with upload.py, restore the clipboard. The window is left open so the
# clip list can be checked (rows '공개 예정 <date>'); close it afterwards with its 닫기 버튼 (then '버튼 나가기' if asked).
E=$(cd "$(dirname "$0")/../../naver/editor" && pwd)
C=$(cd "$(dirname "$0")/.." && pwd)
B=${TMPDIR:-/tmp}/slimio_clip_clipboard
wins() { orca computer list-windows --app com.google.Chrome --json | python3 -c "import sys,json; d=json.load(sys.stdin); r=d.get('result',d); print(' '.join(str(w['id']) for w in r.get('windows',[])))"; }
until bash $E/guard.sh >/dev/null; do sleep 30; done
echo "owner away $(date +%H:%M:%S)"
osascript -l JavaScript $E/clipsave.js $B || { echo "FAIL clipboard backup"; exit 1; }
before=" $(wins) "
open -na "Google Chrome" --args --new-window https://clipcreators.naver.com/web/dashboard
sleep 8
W=""; for w in $(wins); do case "$before" in *" $w "*) ;; *) W=$w;; esac; done
[ -n "$W" ] || { echo "FAIL no new window"; osascript -l JavaScript $E/cliprestore.js $B; exit 1; }
echo "window $W"
bash $E/guard.sh done
for q in "$@"; do
  d=${q%% *}; when=${q#* }
  echo "== $d $when"
  python3 $C/lib/upload.py $W $C/$d "$when" </dev/null || { echo "STOP at $d"; break; }
  sleep 3
done
echo "WINDOW $W left open for the list check"
osascript -l JavaScript $E/cliprestore.js $B && echo "clipboard restored"
