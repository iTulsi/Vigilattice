#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR/backend"
.venv/bin/ruff check .
.venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q src

cd "$ROOT_DIR/frontend"
npm run lint
npm run build
