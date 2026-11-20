#!/usr/bin/env bash
# Monthly refresh of the Israeli store roster from Zap: fresh crawl, merge, commit, push.
# Runs on residencehome (Israeli residential IP, required by Zap) from deploy/israel-online-stores-refresh.timer.
# Safe to run by hand: bash scripts/refresh.sh [--no-push]
set -euo pipefail
cd "$(dirname "$0")/.."
PUSH=1; [[ "${1:-}" == "--no-push" ]] && PUSH=0

git pull -q --ff-only
prev=$(python3 -c 'import json;print(sum(1 for s in json.load(open("stores-index.json")) if not s.get("status")))')

rm -rf .cache/html                      # force a fresh crawl (the page cache is only for resuming)
python3 scripts/scrape_zap.py > .cache/run.log 2>&1 || { echo "scrape failed, see .cache/run.log"; tail -5 .cache/run.log; exit 1; }

# Guard: a blocked or truncated crawl would mark most stores as gone. Require >= 90% of last month's live stores.
now=$(python3 -c 'import json;print(len(json.load(open(".cache/zap_stores.json"))["stores"]))')
echo "zap stores: $now (previous live: $prev)"
if (( now * 10 < prev * 9 )); then echo "ABORT: crawl returned $now stores, under 90% of $prev; nothing committed"; exit 2; fi

python3 scripts/merge.py | tail -1
if git diff --quiet -- stores.json stores-index.json; then echo "no changes"; exit 0; fi

git add stores.json stores-index.json
git -c user.name="Daniel Rosehill" -c user.email="commits@danielrosehill.com" -c commit.gpgsign=false \
  commit -qm "Monthly Zap refresh $(date +%F): $now stores on Zap"
(( PUSH )) && git push -q && echo "pushed $(git rev-parse --short HEAD)"
