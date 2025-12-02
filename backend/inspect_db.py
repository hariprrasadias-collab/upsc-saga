import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'upsc_saga.db')

print(f"Checking database at: {DATABASE}")

try:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    print("\n--- Tables ---")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for t in tables:
        print(t[0])
        
    print("\n--- Users Schema ---")
    try:
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        for col in columns:
            print(col)
    except Exception as e:
        print(f"Error checking users: {e}")

    print("\n--- Challenges Schema ---")
    try:
        cursor.execute("PRAGMA table_info(challenges)")
        columns = cursor.fetchall()
        for col in columns:
            print(col)
    except Exception as e:
        print(f"Error checking challenges: {e}")

    print("\n--- User Challenges Schema ---")
    try:
        cursor.execute("PRAGMA table_info(user_challenges)")
        columns = cursor.fetchall()
        for col in columns:
            print(col)
    except Exception as e:
        print(f"Error checking user_challenges: {e}")
        
    print("\n--- Inventory Schema ---")
    try:
        cursor.execute("PRAGMA table_info(inventory)")
        columns = cursor.fetchall()
        for col in columns:
            print(col)
    except Exception as e:
        print(f"Error checking inventory: {e}")

    print("\n--- User 1 Check ---")
    try:
        user = cursor.execute("SELECT * FROM users WHERE id=1").fetchone()
        print(f"User 1: {user}")
    except Exception as e:
        print(f"Error checking user 1: {e}")

    conn.close()
except Exception as e:
    print(f"Database error: {e}")
