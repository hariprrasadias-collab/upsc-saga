from app import create_app
from app.db import get_db

app = create_app()

with app.app_context():
    conn = get_db()
    try:
        count = conn.execute("SELECT count(*) FROM current_affairs").fetchone()[0]
        print(f"Total articles: {count}")
    except Exception as e:
        print(f"Error: {e}")
