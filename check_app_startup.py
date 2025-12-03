import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

print("🚀 Attempting to create Flask app...")
try:
    from app import create_app
    app = create_app()
    print("✅ App created successfully.")
except Exception as e:
    print(f"❌ App creation failed: {e}")
    import traceback
    traceback.print_exc()
