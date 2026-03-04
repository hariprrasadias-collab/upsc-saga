import sys
import os
import time

sys.path.append(os.path.abspath('backend'))
from app import create_app
from app.db import get_db

def benchmark_seer():
    flask_app = create_app()
    with flask_app.app_context():
        # Setup data
        conn = get_db()
        conn.execute("DELETE FROM tasks")

        # Insert 10,000 tasks
        import datetime
        import random

        today = datetime.date.today()
        user_id = 1

        print("Inserting tasks...")
        for i in range(10000):
            days_ago = random.randint(0, 10)
            date_val = today - datetime.timedelta(days=days_ago)
            conn.execute('''
                INSERT INTO tasks (user_id, title, xp_reward, due_date, isCompleted, associated_stat)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, f"Task {i}", random.randint(10, 50), date_val.isoformat(), 1, "strength_stat"))
        conn.commit()
        print("Inserted tasks")

        from app.routes.seer import consult_the_seer
        import app.routes.seer
        app.routes.seer.get_current_user_id = lambda: 1

        # Create a mock request context
        with flask_app.test_request_context('/api/seer'):
            start = time.time()
            for _ in range(100):
                consult_the_seer()
            end = time.time()

            print(f"Time taken for 100 calls: {end - start:.4f} seconds")

if __name__ == "__main__":
    benchmark_seer()
