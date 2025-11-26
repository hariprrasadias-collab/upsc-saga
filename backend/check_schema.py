import sqlite3

def check_tables():
    conn = sqlite3.connect('upsc_saga.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:")
    for table in tables:
        print(table[0])
        
    # Check mock_tests schema
    print("\nmock_tests columns:")
    cursor.execute("PRAGMA table_info(mock_tests)")
    for col in cursor.fetchall():
        print(col)

    # Check syllabus_topics schema
    print("\nsyllabus_topics columns:")
    cursor.execute("PRAGMA table_info(syllabus_topics)")
    for col in cursor.fetchall():
        print(col)
        
    conn.close()

if __name__ == "__main__":
    check_tables()
