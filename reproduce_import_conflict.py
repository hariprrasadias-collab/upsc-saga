import os
import sys

# Create structure
os.makedirs("test_pkg/my_app", exist_ok=True)
with open("test_pkg/my_app/__init__.py", "w") as f:
    f.write("print('Package loaded')\nval = 1")

# Create conflicting module
with open("test_pkg/my_app.py", "w") as f:
    f.write("import my_app\nprint(f'Module loaded. Pkg val: {my_app.val}')")

print("Created test structure.")
