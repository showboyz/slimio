#!/bin/bash
# win_open.sh <url> : wait for the owner to be away, open my own Chrome window, print its id
E=$(cd "$(dirname "$0")" && pwd)
wins() { orca computer list-windows --app com.google.Chrome --json | python3 -c "import sys,json; d=json.load(sys.stdin); r=d.get('result',d); print(' '.join(str(w['id']) for w in r.get('windows',[])))"; }
until bash $E/guard.sh >/dev/null 2>&1; do sleep 30; done
before=" $(wins) "
open -na "Google Chrome" --args --new-window "$1"
sleep 8
for w in $(wins); do case "$before" in *" $w "*) ;; *) echo "$w";; esac; done
bash $E/guard.sh done
