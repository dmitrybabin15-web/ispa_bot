#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

mkdir -p logs run

SUP_PIDFILE="run/supervisor.pid"
BOT_PIDFILE="run/bot.pid"
CRASH_LOG="logs/crash.log"

ts() {
  # Beget/shared environments sometimes have limited `date` options.
  date "+%Y-%m-%dT%H:%M:%S%z" 2>/dev/null || echo "unknown-time"
}

touch "$CRASH_LOG" 2>/dev/null || true

if [[ -f "$SUP_PIDFILE" ]]; then
  PID="$(cat "$SUP_PIDFILE" || true)"
  if [[ -n "${PID:-}" ]] && [[ "$PID" != "$$" ]] && kill -0 "$PID" 2>/dev/null; then
    echo "Supervisor already running (pid=$PID)"
    exit 0
  fi
  rm -f "$SUP_PIDFILE"
fi

echo $$ > "$SUP_PIDFILE"

export PYTHONUNBUFFERED=1

backoff=2
max_backoff=60

echo "[$(ts)] supervisor started pid=$$" >> "$CRASH_LOG" 2>/dev/null || true

while true; do
  if [[ ! -x "venv/bin/python" ]]; then
    echo "[$(ts)] missing venv/bin/python; sleeping 60s" >> "$CRASH_LOG" 2>/dev/null || true
    sleep 60
    continue
  fi

  # Start bot in foreground so we can detect crashes and restart.
  # All stdout/stderr are appended to files for debugging.
  echo "[$(ts)] starting bot..." >> "$CRASH_LOG" 2>/dev/null || true
  ./venv/bin/python -u main.py >> logs/stdout.log 2>> logs/stderr.log &
  BOT_PID=$!
  echo "$BOT_PID" > "$BOT_PIDFILE"
  echo "[$(ts)] bot started pid=$BOT_PID" >> "$CRASH_LOG" 2>/dev/null || true

  # With `set -e`, a non-zero exit code would terminate the supervisor.
  # We always want to restart instead.
  exit_code=0
  wait "$BOT_PID" || exit_code=$?

  echo "[$(ts)] bot exited code=$exit_code; restarting in ${backoff}s" >> "$CRASH_LOG" 2>/dev/null || true
  sleep "$backoff"

  if (( backoff < max_backoff )); then
    backoff=$(( backoff * 2 ))
    if (( backoff > max_backoff )); then
      backoff=$max_backoff
    fi
  fi
done

