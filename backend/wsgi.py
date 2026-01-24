import sys
import os

# Add the directory containing this file to sys.path
# This ensures that the 'app' package (located in the same directory) can be imported
# regardless of the current working directory (e.g., if gunicorn is run from repo root)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
