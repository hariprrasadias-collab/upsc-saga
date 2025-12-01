from app.db import get_db
from app import create_app

app = create_app()

with app.app_context():
    conn = get_db()
    print("Checking mock_tests table...")
    tests = conn.execute("SELECT id, title, is_active, test_type FROM mock_tests ORDER BY id DESC LIMIT 5").fetchall()
    for t in tests:
        print(dict(t))
