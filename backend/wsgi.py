import sys
import os

# Add the current directory to sys.path to ensure 'app' can be imported
sys.path.append(os.getcwd())

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
