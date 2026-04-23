#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ORDER_ALERT_EMAILS="you@example.com" ./scripts/send_latest_db_email.sh
#   ./scripts/send_latest_db_email.sh you@example.com

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

if [[ -n "${1:-}" ]]; then
  python manage.py email_latest_db_backup --to "$1"
else
  python manage.py email_latest_db_backup
fi
