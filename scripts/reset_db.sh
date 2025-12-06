#!/usr/bin/env bash
set -e
echo "Reset DB (elimina data.db y recrea con init_db)"
rm -f data.db
python3 scripts/init_db.py
echo "DB reseteada."
