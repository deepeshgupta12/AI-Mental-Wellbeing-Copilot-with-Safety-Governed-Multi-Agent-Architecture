#!/usr/bin/env bash
set -euo pipefail

cd apps/api

if command -v python3.11 >/dev/null 2>&1; then
  PYTHON_BIN=python3.11
else
  PYTHON_BIN=python3
fi

$PYTHON_BIN -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -e ".[dev]"

echo "Backend bootstrap complete."