#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

mkdir -p logs run

KEEPALIVE_LOG="logs/keepalive.log"
ts() { date "+%Y-%m-%dT%H:%M:%S%z" 2>/dev/null || echo "unknown-time"; }

log() {
  echo "[$(ts)] $*" >> "$KEEPALIVE_LOG" 2>/dev/null || true
}

# Prevent concurrent runs if flock exists.
if command -v flock >/dev/null 2>&1; then
  exec 9>"run/keepalive.lock"
  flock -n 9 || exit 0
fi

SUP_PIDFILE="run/supervisor.pid"

is_running() {
  if [[ -f "$SUP_PIDFILE" ]]; then
    local pid
    pid="$(cat "$SUP_PIDFILE" 2>/dev/null || true)"
    if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
      return 0
    fi
  fi
  if pgrep -f "run_forever.sh" >/dev/null 2>&1; then
    return 0
  fi
  if pgrep -f "venv/bin/python.*main.py" >/dev/null 2>&1; then
    return 0
  fi
  return 1
}

if is_running; then
  exit 0
fi

log "bot not running, starting via start.sh"
rm -f "$SUP_PIDFILE" run/bot.pid
./start.sh >> "$KEEPALIVE_LOG" 2>&1 || log "start.sh failed"
