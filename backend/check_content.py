from app import create_app
from app.db import get_db

app = create_app()

with app.app_context():
    conn = get_db()
    print("--- Checking Article Content ---")
    
    rows = conn.execute("""
        SELECT title, length(original_summary), length(upsc_summary), original_summary, upsc_summary 
        FROM current_affairs 
        WHERE published_date IS NOT NULL 
        ORDER BY published_date DESC 
        LIMIT 3
    """).fetchall()
    
    for row in rows:
        print(f"\nTitle: {row['title']}")
        print(f"Original Summary Length: {row[1]}")
        print(f"UPSC Summary Length: {row[2]}")
        print(f"Original Start: {row['original_summary'][:100]}...")
        print(f"UPSC Start: {row['upsc_summary'][:100]}...")
