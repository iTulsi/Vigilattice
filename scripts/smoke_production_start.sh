#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"
PORT="${PORT:-18080}"
TMP_DIR="$(mktemp -d)"
LOG_FILE="$TMP_DIR/vigilattice-production.log"
PID=""

cleanup() {
  if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
    kill "$PID" 2>/dev/null || true
    wait "$PID" 2>/dev/null || true
  fi
  rm -rf "$TMP_DIR"
}

trap cleanup EXIT INT TERM

cd "$BACKEND"

VIGILATTICE_ENVIRONMENT=production \
VIGILATTICE_CORS_ORIGINS='["http://localhost:5173"]' \
VIGILATTICE_RUN_DATABASE_PATH="$TMP_DIR/vigilattice.db" \
  .venv/bin/fastapi run src/vigilattice/main.py \
    --host 127.0.0.1 \
    --port "$PORT" \
    >"$LOG_FILE" 2>&1 &

PID=$!

for _ in $(seq 1 40); do
  if curl -fsS \
    "http://127.0.0.1:$PORT/api/v1/ready" \
    >/dev/null 2>&1; then
    break
  fi

  if ! kill -0 "$PID" 2>/dev/null; then
    cat "$LOG_FILE"
    echo "ERROR: Production server exited early."
    exit 1
  fi

  sleep 0.25
done

curl -fsS "http://127.0.0.1:$PORT/api/v1/health" \
  >/dev/null
curl -fsS "http://127.0.0.1:$PORT/api/v1/live" \
  >/dev/null
curl -fsS "http://127.0.0.1:$PORT/api/v1/ready" \
  >/dev/null
curl -fsS "http://127.0.0.1:$PORT/api/v1/scenarios" \
  >/dev/null

echo "Production startup smoke test passed on port $PORT."
