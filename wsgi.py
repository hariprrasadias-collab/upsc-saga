import sys
import os

# Add the backend directory to the Python path
# This allows 'from app import create_app' to work
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
