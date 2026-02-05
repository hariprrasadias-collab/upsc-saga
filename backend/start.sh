#!/bin/bash
echo "🔄 Running startup migration..."
python3 migrate_add_admin_column.py

echo "🚀 Starting Gunicorn..."
# Use PORT env var if set, otherwise default to 5000
exec gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} wsgi:app
