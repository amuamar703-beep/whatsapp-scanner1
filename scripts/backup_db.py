#!/bin/bash

set -e

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/whatsapp_scanner_${TIMESTAMP}.sql"

mkdir -p $BACKUP_DIR

echo "Creating database backup..."

docker exec -t whatsapp_scanner_db pg_dump -U scanner whatsapp_scanner > $BACKUP_FILE

gzip $BACKUP_FILE

echo "Backup created: ${BACKUP_FILE}.gz"

# Delete backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -type f -mtime +30 -delete

echo "Old backups cleaned up"