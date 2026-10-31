#!/bin/bash
# trun.sh <win> "<script> <args…>" … : waits until the owner is away (guard.sh), then runs each Tistory job in my Chrome
# window <win>, e.g. "tnew.py 21-withholding-receipt.html 2026-11-10 08" or "tedit.py 14-pdf-unlock.html 21 2026-11-03 08"
# or "tedit.py 01-id-photo.html 7 live" (draft names are relative to this folder). Stops at the first job that doesn't
# end in RESERVED/SAVED, or when the owner comes back. Don't mark 'guard.sh done' between jobs: the scripts mark their
# own clicks, so guard.sh then sees any input since the last click as the owner's.
T=$(cd "$(dirname "$0")" && pwd); G=$T/../naver/editor/guard.sh
W=$1; shift
t0=$(date +%s)
until bash $G >/dev/null 2>&1; do
  [ $(( $(date +%s) - t0 )) -gt 21600 ] && { echo "still busy after 6h"; exit 1; }
  sleep 30
done
date "+%H:%M:%S owner away"
orca computer list-windows --app com.google.Chrome | grep -q "id:$W " || { echo "window $W is gone"; exit 1; }
for job in "$@"; do
  set -- $job; s=$1; d=$2; shift 2
  echo "== $job"
  bash $G || { echo "STOP owner"; exit 2; }
  out=$(python3 $T/$s $W $T/$d "$@" 2>&1); echo "$out" | tail -3
  echo "$out" | grep -qE 'RESERVED|SAVED' || { echo "STOP at $d"; exit 1; }
done
echo "all done $(date +%H:%M:%S)"
