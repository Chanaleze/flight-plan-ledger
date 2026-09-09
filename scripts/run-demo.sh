#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Installing package in editable mode (if needed)…"
pip install -e . -q

echo
echo "Running end-to-end demo…"
python -m flight_plan_ledger.cli.main demo
