import sys
import os

# Add backend directory to sys.path so 'app' package can be imported
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
