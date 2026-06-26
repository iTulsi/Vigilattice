#!/usr/bin/env bash
set -euo pipefail

API_BASE="${1:-${VIGILATTICE_API_URL:-}}"
WEB_URL="${2:-${VIGILATTICE_WEB_URL:-}}"

if [ -z "$API_BASE" ] || [ -z "$WEB_URL" ]; then
  echo "Usage:"
  echo "  ./scripts/check_production_release.sh \\"
  echo "    https://YOUR-API.onrender.com/api/v1 \\"
  echo "    https://YOUR-WEB.onrender.com"
  exit 1
fi

API_BASE="${API_BASE%/}"
WEB_URL="${WEB_URL%/}"
HEADERS_FILE="$(mktemp)"

cleanup() {
  rm -f "$HEADERS_FILE"
}

trap cleanup EXIT

echo "Checking API health..."
curl -fsS "$API_BASE/health" >/dev/null

echo "Checking API liveness..."
curl -fsS "$API_BASE/live" >/dev/null

echo "Checking API readiness..."
curl -fsS "$API_BASE/ready" >/dev/null

echo "Checking scenario catalog..."
curl -fsS "$API_BASE/scenarios" >/dev/null

echo "Checking frontend..."
curl -fsS "$WEB_URL" | grep -qi "Vigilattice"

echo "Checking production CORS..."
curl -fsS \
  -D "$HEADERS_FILE" \
  -o /dev/null \
  -H "Origin: $WEB_URL" \
  "$API_BASE/health"

grep -Fqi \
  "access-control-allow-origin: $WEB_URL" \
  "$HEADERS_FILE"

echo
echo "Production release checks passed."
echo "Frontend: $WEB_URL"
echo "API:      $API_BASE"
