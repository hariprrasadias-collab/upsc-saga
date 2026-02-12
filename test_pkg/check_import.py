import sys
sys.path.insert(0, ".") # Emulate running from current dir
try:
    import my_app
    print(f"Imported: {my_app}")
    print(f"File: {my_app.__file__}")
except Exception as e:
    print(f"Error: {e}")
