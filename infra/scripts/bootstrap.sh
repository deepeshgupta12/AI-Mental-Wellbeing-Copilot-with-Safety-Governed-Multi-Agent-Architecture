#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "Bootstrapping backend..."
cd "$ROOT_DIR/apps/api"

if command -v python3.11 >/dev/null 2>&1; then
  PYTHON_BIN=python3.11
else
  PYTHON_BIN=python3
fi

$PYTHON_BIN -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"

echo "Bootstrapping frontend..."
cd "$ROOT_DIR/apps/web"
npm install

echo "Bootstrap complete."
echo "Backend venv: $ROOT_DIR/apps/api/.venv"
echo "Frontend deps installed in: $ROOT_DIR/apps/web/node_modules"