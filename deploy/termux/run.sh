#!/usr/bin/env bash
# Runs the WKAI backend INSIDE Debian and restarts it the way Render used to.
#
#   exit 1  fatal startup error (see wkai-backend/src/index.js) -> restart
#   exit 0  Ctrl-C / SIGTERM -> stay down
set -uo pipefail

REPO_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
BACKEND_DIR="$REPO_DIR/wkai-backend"
LOG_DIR="${LOG_DIR:-$HOME/wkai-logs}"
LOG_FILE="$LOG_DIR/backend.log"
MAX_LOG_BYTES=$((20 * 1024 * 1024))

cd "$BACKEND_DIR"
mkdir -p "$LOG_DIR"

# Render ran in UTC; keep behaviour identical.
export TZ="${TZ:-UTC}"
export NODE_ENV=production
# A phone has less RAM than it seems once Android takes its share.
export NODE_OPTIONS="${NODE_OPTIONS:---max-old-space-size=512}"

command -v node >/dev/null || { echo "node missing - run: bash $REPO_DIR/deploy/termux/setup-debian.sh" >&2; exit 1; }
[ -f src/index.js ] || { echo "src/index.js missing - wrong checkout?" >&2; exit 1; }
[ -f .env ] || { echo ".env missing - copy .env.example and fill it in" >&2; exit 1; }

rotate_log() {
  if [ -f "$LOG_FILE" ] && [ "$(stat -c %s "$LOG_FILE")" -gt "$MAX_LOG_BYTES" ]; then
    mv -f "$LOG_FILE" "$LOG_FILE.1"
  fi
}

RESTART_FLAG="$REPO_DIR/.restart-requested"
rm -f "$RESTART_FLAG"

# Optional: follow origin/main and restart on new commits (deploy/termux/autoupdate.sh).
updater=0
if grep -Eq '^AUTO_UPDATE=true' .env 2>/dev/null; then
  LOG_FILE="$LOG_FILE" bash "$REPO_DIR/deploy/termux/autoupdate.sh" &
  updater=$!
fi

child=0
stop() {
  echo "[run.sh] stopping" | tee -a "$LOG_FILE"
  [ "$updater" -ne 0 ] && kill -TERM "$updater" 2>/dev/null
  [ "$child" -ne 0 ] && kill -TERM "$child" 2>/dev/null && wait "$child"
  exit 0
}
trap stop INT TERM

# Migrate once per invocation (picks up new migrations after a git pull).
# Migrations are idempotent; the crash loop below runs node directly so a
# restart is fast.
echo "[run.sh] running migrations" | tee -a "$LOG_FILE"
npm run db:migrate 2>&1 | tee -a "$LOG_FILE" || {
  echo "[run.sh] migration failed; not starting backend" | tee -a "$LOG_FILE"
  exit 1
}

backoff=5
while true; do
  rotate_log
  started=$(date +%s)
  echo "[run.sh] $(date -u +%FT%TZ) starting backend" | tee -a "$LOG_FILE"
  # Process substitution, not a pipe: $! must be node's pid so that `wait`
  # returns node's exit code rather than tee's.
  node src/index.js > >(tee -a "$LOG_FILE") 2>&1 &
  child=$!
  wait "$child"
  code=$?
  child=0

  if [ "$code" -eq 0 ] && [ -f "$RESTART_FLAG" ]; then
    # The auto-updater stopped the backend to load new commits.
    rm -f "$RESTART_FLAG"
    backoff=5
    continue
  fi
  if [ "$code" -eq 0 ]; then
    echo "[run.sh] backend exited cleanly (0); not restarting" | tee -a "$LOG_FILE"
    [ "$updater" -ne 0 ] && kill -TERM "$updater" 2>/dev/null
    exit 0
  fi

  # A run that lasted 10+ minutes was healthy; restart quickly again.
  if [ $(( $(date +%s) - started )) -ge 600 ]; then backoff=5; fi
  echo "[run.sh] backend exited ($code); restarting in ${backoff}s" | tee -a "$LOG_FILE"
  sleep "$backoff"
  backoff=$(( backoff * 2 > 300 ? 300 : backoff * 2 ))
done
