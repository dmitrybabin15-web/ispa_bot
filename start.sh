#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

mkdir -p logs run

PIDFILE="run/bot.pid"
SUP_PIDFILE="run/supervisor.pid"
LOG_OUT="logs/stdout.log"
LOG_ERR="logs/stderr.log"

if [[ -f "$SUP_PIDFILE" ]]; then
  SUP_PID="$(cat "$SUP_PIDFILE" || true)"
  if [[ -n "${SUP_PID:-}" ]] && kill -0 "$SUP_PID" 2>/dev/null; then
    echo "Already running (supervisor pid=$SUP_PID)"
    exit 0
  fi
  rm -f "$SUP_PIDFILE"
fi

if [[ ! -x "venv/bin/python" ]]; then
  echo "Missing venv. Create it first."
  echo "Hint (shared hosting): python3 -m pip install --user -U pip virtualenv && python3 -m virtualenv --copies venv"
  exit 1
fi

export PYTHONUNBUFFERED=1

# Disable webhook so polling mode never conflicts with an old webhook URL.
BOT_TOKEN="$(grep -E '^BOT_TOKEN=' .env 2>/dev/null | cut -d= -f2- || true)"
if [[ -n "${BOT_TOKEN:-}" ]]; then
  curl -s "https://api.telegram.org/bot${BOT_TOKEN}/deleteWebhook?drop_pending_updates=true" >/dev/null 2>&1 || true
fi

# Detach fully from the SSH session (shared hosting often kills nohup-only jobs).
if command -v setsid >/dev/null 2>&1; then
  setsid /usr/bin/env bash ./run_forever.sh >>"$LOG_OUT" 2>>"$LOG_ERR" < /dev/null &
else
  nohup /usr/bin/env bash ./run_forever.sh >>"$LOG_OUT" 2>>"$LOG_ERR" < /dev/null &
fi
disown $! 2>/dev/null || true

# run_forever.sh writes its own PID to SUP_PIDFILE; wait for it.
for _ in $(seq 1 10); do
  if [[ -f "$SUP_PIDFILE" ]]; then
    SUP_PID="$(cat "$SUP_PIDFILE" || true)"
    if [[ -n "${SUP_PID:-}" ]] && kill -0 "$SUP_PID" 2>/dev/null; then
      echo "Started supervisor (pid=$SUP_PID)"
      exit 0
    fi
  fi
  sleep 0.5
done

echo "Supervisor failed to start. Check logs/stderr.log"
exit 1

