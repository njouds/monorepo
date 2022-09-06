#! /usr/bin/env sh
set -e

python ./init_db.py

# Start Gunicorn
exec gunicorn -k "$WORKER_CLASS" -c "$GUNICORN_CONF" "$MODULE_NAME"