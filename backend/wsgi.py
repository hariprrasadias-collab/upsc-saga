import os
import sys

# Ensure the current directory is in sys.path so that 'app' package can be imported
sys.path.append(os.getcwd())

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
