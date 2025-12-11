#!/bin/bash
export FLASK_APP=run_saga.py
export FLASK_ENV=production
# Run gunicorn on port 5000 with 4 workers
# We assume run_saga.py has 'app' instance or 'create_app' function
# run_saga.py calls app.run() in main. We need to expose the app object.

# Let's check run_saga.py first
if ! grep -q "app =" run_saga.py; then
    echo "Creating entry point for gunicorn..."
    echo "from app import create_app" > wsgi.py
    echo "app = create_app()" >> wsgi.py
else
    # If run_saga.py exposes 'app' globally we can use it, but usually it's better to use wsgi.py
    echo "Creating entry point for gunicorn..."
    echo "from app import create_app" > wsgi.py
    echo "app = create_app()" >> wsgi.py
fi

# Run gunicorn
cd backend
# Make sure we are in backend dir
gunicorn --bind 0.0.0.0:5000 wsgi:app --workers 4 --timeout 120 --access-logfile - --error-logfile - &
