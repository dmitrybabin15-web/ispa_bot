#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PIDFILE="run/bot.pid"

if [[ -f "$PIDFILE" ]]; then
  PID="$(cat "$PIDFILE" || true)"
  if [[ -n "${PID:-}" ]] && kill -0 "$PID" 2>/dev/null; then
    echo "RUNNING pid=$PID"
    exit 0
  fi
  echo "NOT RUNNING (stale pidfile: ${PID:-empty})"
  exit 1
fi

echo "NOT RUNNING"
exit 1

