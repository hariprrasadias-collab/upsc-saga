import os
import sys

# Ensure the backend directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
import migrate_add_admin_column

# Run schema migration on startup to ensure 'is_admin' column exists
try:
    print("🔄 Running startup migration...")
    migrate_add_admin_column.migrate()
    print("✅ Startup migration complete.")
except Exception as e:
    print(f"⚠️ Migration failed: {e}")

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
