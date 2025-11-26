from app import create_app
from app.db import get_db
import sqlite3

app = create_app()

with app.app_context():
    conn = get_db()
    
    print("--- Checking current_affairs table ---")
    try:
        count = conn.execute("SELECT count(*) FROM current_affairs").fetchone()[0]
        print(f"Total articles: {count}")
        
        if count > 0:
            print("\n--- Sample Articles ---")
            rows = conn.execute("SELECT id, title, published_date, fetch_date FROM current_affairs LIMIT 5").fetchall()
            for row in rows:
                print(f"ID: {row['id']} | Date: {row['published_date']} | Fetch: {row['fetch_date']} | Title: {row['title']}")
                
            print("\n--- Distinct Months ---")
            months = conn.execute("SELECT DISTINCT substr(published_date, 1, 7) FROM current_affairs").fetchall()
            for m in months:
                print(f"Month: {m[0]}")
        else:
            print("Table is empty.")
            
    except Exception as e:
        print(f"Error: {e}")
