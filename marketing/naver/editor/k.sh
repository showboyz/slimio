# k.sh <win> <orca action args...>  — restore window, verify Chrome is frontmost, then act (up to 3 tries)
W=$1; shift
for n in 1 2 3; do
  orca computer get-app-state --app com.google.Chrome --window-id $W --json --no-screenshot --restore-window >/dev/null
  F=$(osascript -e 'tell application "System Events" to get name of first application process whose frontmost is true')
  if [ "$F" = "Google Chrome" ]; then orca computer "$@" --app com.google.Chrome --window-id $W --json --no-screenshot | python3 -c 'import json,sys;d=json.load(sys.stdin);print("ok" if d.get("ok",True) else d)'; exit 0; fi
  sleep 0.7
done
echo "ABORT front=$F"; exit 1
