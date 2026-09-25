#!/usr/bin/env sh
set -eu
mkdir -p db-data
if command -v docker >/dev/null 2>&1; then
  docker compose up -d --build
else
  echo "Docker is not installed or not available in PATH." >&2
  exit 1
fi
