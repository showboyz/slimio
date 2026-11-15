#!/bin/bash
# win_close.sh <win> : close my own Chrome window by its 닫기 버튼, answer '나가기' if Chrome asks, then confirm it is gone.
# Since 2026-11-10 Chrome asks in a window of its own (leavedlg.sh), answered only when it was not there before the click.
W=$1; E=$(cd "$(dirname "$0")" && pwd)
wins() { orca computer list-windows --app com.google.Chrome --json | python3 -c "import sys,json; d=json.load(sys.stdin); r=d.get('result',d); print(' '.join(str(w['id']) for w in r.get('windows',[])))"; }
tree() { orca computer get-app-state --app com.google.Chrome --window-id "$1" 2>/dev/null; }
case " $(wins) " in *" $W "*) ;; *) echo "window $W already gone"; exit 0;; esac
# a tab opened elsewhere that landed in my window (tblfix.own_tab) is not mine to close: then close only my 네이버 블로그
# tab(s) with Cmd+W and leave the window (2026-11-15: closing the window took a 'LiveTrans 소개 페이지' tab with it)
others=$(cd $E && python3 -c "import sys; sys.argv=['x']; import tblfix as tf; tf.W='$W'; print(' | '.join(tf.own_tab()))")
if [ -n "$others" ]; then
  (cd $E && python3 -c "
import sys, time; sys.argv = ['x']; import tblfix as tf; tf.W = '$W'
for _ in range(5):
    mine = [x for x in tf.tabs() if tf.MINE in x[2]]
    if not mine: break
    tf.sh('orca', 'computer', 'click', '--app', 'com.google.Chrome', '--window-id', tf.W, '--element-index', mine[0][0], '--no-screenshot'); time.sleep(1)
    pre = tf.leave_dialog()
    tf.k('hotkey', '--key', 'CmdOrCtrl+W'); time.sleep(2)
    if not tf.press(r'^버튼 나가기$') and not pre: tf.leave_dialog(press=True)
    time.sleep(1.5)
")
  echo "closed my tab(s) in window $W, kept the window for: $others"; exit 0
fi
pre=$(bash $E/leavedlg.sh)
T=$(tree "$W")
c=$(echo "$T" | grep -E '^[[:space:]]*[0-9]+ .*닫기 버튼$' | head -1 | sed -E 's/^[[:space:]]*([0-9]+).*/\1/')
[ -n "$c" ] || { echo "FAIL no 닫기 버튼 in $W"; exit 1; }
orca computer click --app com.google.Chrome --window-id "$W" --element-index "$c" --no-screenshot >/dev/null 2>&1
sleep 2
case " $(wins) " in *" $W "*)
  T=$(tree "$W")
  x=$(echo "$T" | grep -E '^[[:space:]]*[0-9]+ 버튼 나가기$' | head -1 | sed -E 's/^[[:space:]]*([0-9]+).*/\1/')
  if [ -n "$x" ]; then orca computer click --app com.google.Chrome --window-id "$W" --element-index "$x" --no-screenshot >/dev/null 2>&1
  elif [ "$pre" = none ]; then bash $E/leavedlg.sh press >/dev/null; fi
  sleep 2;;
esac
case " $(wins) " in *" $W "*) echo "CHECK window $W still open";; *) echo "window $W closed";; esac
