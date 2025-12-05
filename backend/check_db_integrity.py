import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'upsc_saga.db')

def check_integrity():
    print(f"Checking database at: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("ERROR: Database file not found!")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        
        print("\n--- Integrity Check ---")
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        print(f"Status: {integrity}")
        
        if integrity != "ok":
            print("CRITICAL: Database is corrupted!")
            return

        print("\n--- Table Status ---")
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        for table in tables:
            name = table['name']
            try:
                count = conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
                print(f"Table '{name}': {count} rows")
            except Exception as e:
                print(f"Table '{name}': ERROR reading - {e}")
                
        conn.close()
        print("\nDatabase check completed.")
        
    except Exception as e:
        print(f"CRITICAL ERROR: Cannot connect to database - {e}")

if __name__ == "__main__":
    check_integrity()
