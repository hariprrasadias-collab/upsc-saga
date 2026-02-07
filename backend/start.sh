#!/bin/bash
# Run migrations
python3 migrate_add_admin_column.py

# Start Gunicorn
# Use PORT env var if set, otherwise default to 5000
PORT=${PORT:-5000}
exec gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app
