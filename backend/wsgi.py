import os
import sys

# Add the directory containing this file (backend/) to sys.path
# This ensures 'app' package can be imported directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
