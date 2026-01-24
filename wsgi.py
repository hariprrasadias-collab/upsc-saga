import sys
import os

# Add the backend directory to sys.path so that 'app' package can be imported
# This assumes wsgi.py is in the repo root and backend is a subdirectory
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
