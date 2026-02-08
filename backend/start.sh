#!/bin/bash
echo "Starting backend..."
python3 migrate_add_admin_column.py
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
