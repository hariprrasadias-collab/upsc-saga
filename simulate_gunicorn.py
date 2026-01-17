import sys
import os

# Gunicorn runs from root, so root is in sys.path
sys.path.insert(0, os.getcwd())

print(f"Simulating Gunicorn from: {os.getcwd()}")
print(f"sys.path: {sys.path}")

try:
    import backend.wsgi
    print("✅ Imported backend.wsgi")
    if hasattr(backend.wsgi, 'app'):
        print("✅ Found 'app' object in backend.wsgi")
    else:
        print("❌ 'app' object MISSING in backend.wsgi")
except Exception as e:
    print(f"❌ Failed to import backend.wsgi: {e}")
    import traceback
    traceback.print_exc()
