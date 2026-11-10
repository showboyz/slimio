#!/bin/bash
# leavedlg.sh [press] : Chrome's '사이트에서 나가시겠습니까?' (leave site?) dialog. Since the orca update of 2026-11-10 it is
# a window of its own that `orca computer list-windows` does not show and the editor window's tree does not contain, so
# it is reached through System Events. Prints 'open' or 'none'; with 'press' it clicks the dialog's 나가기 and prints
# 'left'. Press it only right after my own window asked to leave (go() or its 닫기 버튼) and when this printed 'none'
# just before that, so the dialog can only be my window's (on 11/11 one blocked every key and click into the window).
osascript - "${1:-check}" <<'EOF'
on run argv
	set act to item 1 of argv
	tell application "System Events" to tell process "Google Chrome"
		repeat with w in windows
			try
				if subrole of w is "AXDialog" and (exists static text "사이트에서 나가시겠습니까?" of w) then
					if act is "press" then
						click button "나가기" of w
						return "left"
					end if
					return "open"
				end if
			end try
		end repeat
	end tell
	return "none"
end run
EOF
