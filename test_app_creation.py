import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from app import create_app

try:
    app = create_app()
    print("App created successfully!")
except Exception as e:
    print(f"Failed to create app: {e}")
