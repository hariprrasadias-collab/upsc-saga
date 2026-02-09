
import sys
import os

sys.path.insert(0, os.getcwd())
import app
print(f"Imported app from: {app.__file__}")
if hasattr(app, 'create_app'):
    print("Has create_app")
else:
    print("No create_app")

if hasattr(app, 'app'):
    print("Has app instance")
else:
    print("No app instance")
