import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Run migration to ensure admin column exists (Fix for Security Critical)
try:
    from migrate_add_admin_column import migrate
    print("🚀 WSGI: Running Admin Migration...")
    migrate()
except ImportError:
    print("⚠️ WSGI: Migration script not found or failed to import.")
except Exception as e:
    print(f"⚠️ WSGI: Migration failed: {e}")

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
