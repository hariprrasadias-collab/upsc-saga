from app import create_app
from app.db import get_db

app = create_app()
with app.app_context():
    conn = get_db()
    res = conn.execute("PRAGMA table_info(tasks)").fetchall()
    print("Tasks table columns:")
    for row in res:
        print(dict(row))
