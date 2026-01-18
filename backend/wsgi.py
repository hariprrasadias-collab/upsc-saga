import sys
import os

# Ensure backend directory is in sys.path so we can import 'app'
# Use insert(0) to prioritize this path over others (like root if it has app.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
