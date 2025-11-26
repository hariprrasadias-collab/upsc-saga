from app import create_app
from app.db import get_db

app = create_app()

with app.app_context():
    conn = get_db()
    print("--- Article Date Analysis ---")
    
    # Count total
    total = conn.execute("SELECT count(*) FROM current_affairs").fetchone()[0]
    print(f"Total articles: {total}")
    
    # Count null dates
    null_dates = conn.execute("SELECT count(*) FROM current_affairs WHERE published_date IS NULL").fetchone()[0]
    print(f"Articles with NULL published_date: {null_dates}")
    
    # Group by month (for non-null)
    print("\n--- Articles by Month ---")
    rows = conn.execute("""
        SELECT substr(published_date, 1, 7) as m, count(*) 
        FROM current_affairs 
        WHERE published_date IS NOT NULL 
        GROUP BY m 
        ORDER BY m DESC
    """).fetchall()
    
    for row in rows:
        print(f"Month: {row['m']} | Count: {row[1]}")
        
    # Sample of date formats
    print("\n--- Sample Date Formats ---")
    rows = conn.execute("SELECT published_date FROM current_affairs WHERE published_date IS NOT NULL LIMIT 5").fetchall()
    for row in rows:
        print(f"Date: {row['published_date']}")
