# guard.sh [done] : is the user away? Fails if the screen is locked or the keyboard/mouse was used since my last step.
# Run it before each step and `guard.sh done` after it. Before the first step it needs 120 s without input.
# HIDIdleTime is no use here: a plugged-in game controller resets it several times a second, and our own
# clicks and keys reset it too. This counts keyboard and mouse events only and allows for our own last step.
L=$TMPDIR/naver_editor_last
[ "$1" = done ] && { date +%s > $L; exit 0; }
I=$(osascript -l JavaScript -e 'ObjC.import("CoreGraphics"); Math.round($.CGEventSourceSecondsSinceLastEventType(1, 4294967295))')
E=120; [ -f $L ] && [ $(( $(date +%s) - $(cat $L) )) -lt 600 ] && E=$(( $(date +%s) - $(cat $L) - 4 ))
K=$(ioreg -n Root -d1 -a | grep -A1 CGSSessionScreenIsLocked | grep -c true)
echo "keyboard/mouse idle ${I}s (need ${E}s), locked=$K"
[ "$K" -eq 0 ] && [ "$I" -ge "$E" ]
