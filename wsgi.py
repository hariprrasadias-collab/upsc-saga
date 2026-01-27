import sys
import os

# Add backend to path so we can import app
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
