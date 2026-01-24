import sys
import os

# Add the current directory to sys.path so that 'app' can be imported
# This is crucial for Gunicorn to resolve the app package
sys.path.append(os.getcwd())

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
