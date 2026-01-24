#!/usr/bin/env bash
set -euo pipefail

# PostgreSQL connection settings
DB_NAME="chitral_hive"
DB_USER="chitral"

DB_HOST="localhost"
DB_PORT="5432"

# Backup settings
BACKUP_DIR="/var/backups/chitralhive"
BACKUP_PREFIX="chitral_hive"
RECIPIENT_EMAIL="zuhooruddin055@gmail.com"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Use .pgpass for password (recommended)
# Format: hostname:port:database:username:password
PGPASSFILE="${PGPASSFILE:-$HOME/.pgpass}"
export PGPASSFILE

timestamp="$(date +%Y-%m-%d)"
backup_file="${BACKUP_DIR}/${BACKUP_PREFIX}_${timestamp}.sql.gz"

# Create compressed dump
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" | gzip > "$backup_file"

# Email backup as attachment (requires mailx)
if command -v mailx >/dev/null 2>&1; then
  echo "PostgreSQL monthly backup for ${DB_NAME} on ${timestamp}" | \
    mailx -s "Monthly DB Backup - ${DB_NAME} (${timestamp})" -a "$backup_file" "$RECIPIENT_EMAIL"
else
  echo "mailx not found. Backup created at: $backup_file"
fi

