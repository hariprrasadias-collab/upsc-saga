import sqlite3

def check_tables_detailed():
    try:
        conn = sqlite3.connect('upsc_saga.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"Total tables: {len(tables)}")
        for table in sorted(tables):
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table}: {count} rows")
            except Exception as e:
                print(f"{table}: Error getting count ({e})")
                
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    check_tables_detailed()
