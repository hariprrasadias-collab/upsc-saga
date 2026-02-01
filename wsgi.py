import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import the application factory
from app import create_app

# Create the application instance
app = create_app()

if __name__ == "__main__":
    app.run()
