#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

PIDFILE="run/bot.pid"
SUP_PIDFILE="run/supervisor.pid"

if [[ -f "$SUP_PIDFILE" ]]; then
  SUP_PID="$(cat "$SUP_PIDFILE" || true)"
  if [[ -n "${SUP_PID:-}" ]] && kill -0 "$SUP_PID" 2>/dev/null; then
    kill "$SUP_PID" || true
    sleep 1
    if kill -0 "$SUP_PID" 2>/dev/null; then
      kill -9 "$SUP_PID" || true
    fi
    echo "Stopped supervisor (pid=$SUP_PID)"
  else
    echo "Supervisor not running (stale pid=${SUP_PID:-empty})"
  fi
  rm -f "$SUP_PIDFILE"
fi

if [[ ! -f "$PIDFILE" ]]; then
  echo "Not running (no bot pidfile)"
  exit 0
fi

PID="$(cat "$PIDFILE" || true)"
if [[ -z "${PID:-}" ]]; then
  rm -f "$PIDFILE"
  echo "Not running (empty pidfile)"
  exit 0
fi

if kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  sleep 1
  if kill -0 "$PID" 2>/dev/null; then
    kill -9 "$PID" || true
  fi
  echo "Stopped (pid=$PID)"
else
  echo "Not running (stale pid=$PID)"
fi

rm -f "$PIDFILE"

