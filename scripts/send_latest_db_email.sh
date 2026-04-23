#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ORDER_ALERT_EMAILS="you@example.com" ./scripts/send_latest_db_email.sh
#   ./scripts/send_latest_db_email.sh you@example.com

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

if [[ -x "$PROJECT_DIR/venv/bin/python" ]]; then
  PYTHON_BIN="$PROJECT_DIR/venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "Error: python not found. Activate venv or install python3."
  exit 1
fi

if [[ -n "${1:-}" ]]; then
  "$PYTHON_BIN" manage.py email_latest_db_backup --to "$1"
else
  "$PYTHON_BIN" manage.py email_latest_db_backup
fi
