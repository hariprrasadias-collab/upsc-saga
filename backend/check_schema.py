import sqlite3

def check_schema():
    try:
        conn = sqlite3.connect('upsc_saga.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(test_attempts)")
        columns = cursor.fetchall()
        print("Columns in test_attempts:")
        for col in columns:
            print(col)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
