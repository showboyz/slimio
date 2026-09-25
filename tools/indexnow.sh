#!/bin/sh
# Tell Bing, Naver, Yandex, Seznam and Yep (via IndexNow) about every URL in sitemap.xml.
# Run after a deploy that adds or changes pages. Google does not use IndexNow — use GSC for it.
set -e
cd "$(dirname "$0")/../public"

HOST="pdfslimio.com"
KEY_FILE=$(ls | grep -E '^[0-9a-f]{32}\.txt$' | head -1)
[ -n "$KEY_FILE" ] || { echo "no IndexNow key file in public/"; exit 1; }
KEY=${KEY_FILE%.txt}

# the key file must be live before engines will accept the submission
curl -sf "https://$HOST/$KEY_FILE" | grep -q "$KEY" || { echo "key file not live yet: https://$HOST/$KEY_FILE"; exit 1; }

URLS=$(grep -o '<loc>[^<]*</loc>' sitemap.xml | sed 's#<loc>\(.*\)</loc>#"\1"#' | paste -sd, -)
BODY="{\"host\":\"$HOST\",\"key\":\"$KEY\",\"keyLocation\":\"https://$HOST/$KEY_FILE\",\"urlList\":[$URLS]}"

CODE=$(curl -s -o /tmp/indexnow.out -w '%{http_code}' -X POST "https://api.indexnow.org/indexnow" \
  -H "Content-Type: application/json; charset=utf-8" -d "$BODY")
echo "IndexNow: HTTP $CODE ($(echo "$URLS" | tr ',' '\n' | wc -l | tr -d ' ') URLs)"
cat /tmp/indexnow.out 2>/dev/null; echo
# 200/202 = accepted. 403 = key not valid, 422 = URLs don't match host, 429 = too many requests
case "$CODE" in 200|202) exit 0 ;; *) exit 1 ;; esac
