import sys
import os

# Ensure backend directory is in sys.path so we can import 'app'
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
