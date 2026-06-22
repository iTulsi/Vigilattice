#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Preparing Vigilattice backend"
cd "$ROOT_DIR/backend"
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[dev]'

echo "==> Preparing Vigilattice frontend"
cd "$ROOT_DIR/frontend"
npm install

echo "==> Running backend tests"
cd "$ROOT_DIR/backend"
.venv/bin/python -m pytest -q

echo "==> Building frontend"
cd "$ROOT_DIR/frontend"
npm run build

echo
printf 'Vigilattice foundation is ready.\nRun `make api` and `make web` in separate terminals.\n'
