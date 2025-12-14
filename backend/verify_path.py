import os
import sys

# Add parent dir to path to find 'app'
sys.path.append(os.getcwd())

from app.db import DATABASE
print(f"DATABASE PATH: {DATABASE}")
