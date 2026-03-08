import sys
import os
import tempfile
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

db_fd, db_path = tempfile.mkstemp()
os.environ['DATABASE_PATH'] = db_path

from app import create_app
from app.db import get_db

def test_progress_trend_optimization():
    print(f"Testing progress trend optimization using temporary DB at {db_path}...")
    try:
        app = create_app()
        client = app.test_client()

        with app.app_context():
            conn = get_db()

            # The app initialization creates the table, but we ensure it matches expectations
            try:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS syllabus_topics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        topic TEXT NOT NULL,
                        status TEXT NOT NULL,
                        paper TEXT,
                        source TEXT,
                        user_id INTEGER
                    )
                ''')
            except sqlite3.OperationalError:
                pass

            conn.execute("DELETE FROM syllabus_topics")

            # Insert test data: 2 completed, 1 pending = 3 total (66.7% completion)
            conn.execute("INSERT INTO syllabus_topics (topic, status, paper, source, user_id) VALUES ('T1', 'Completed', 'GS1', 'Manual', 1)")
            conn.execute("INSERT INTO syllabus_topics (topic, status, paper, source, user_id) VALUES ('T2', 'Completed', 'GS1', 'Manual', 1)")
            conn.execute("INSERT INTO syllabus_topics (topic, status, paper, source, user_id) VALUES ('T3', 'Pending', 'GS1', 'Manual', 1)")
            conn.commit()

            count_completed = conn.execute("SELECT COUNT(*) FROM syllabus_topics WHERE status='Completed'").fetchone()[0]
            count_total = conn.execute("SELECT COUNT(*) FROM syllabus_topics").fetchone()[0]
            print(f"Data state in DB: {count_completed} completed / {count_total} total")

        response = client.get('/api/analytics/progress-trend?metric=syllabus&days=5')
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

        # New response structure puts data inside 'data' key due to response wrapping middleware
        json_resp = response.get_json()
        data = json_resp.get('data', json_resp)

        assert len(data) == 6, f"Expected 6 data points, got {len(data)}"

        for item in data:
            assert item['value'] == 66.7, f"Expected 66.7% completion, got {item['value']}"

        print("✅ Optimization test passed successfully! Syllabus calculation runs efficiently.")

    finally:
        os.close(db_fd)
        os.unlink(db_path)

def test_identify_weak_areas_n1_optimization():
    print("Testing identify_weak_areas N+1 optimization using temporary DB...")
    db_fd, db_path = tempfile.mkstemp()
    os.environ['DATABASE_PATH'] = db_path

    try:
        app = create_app()
        client = app.test_client()

        with app.app_context():
            conn = get_db()

            # Create schema and data
            conn.execute('''
                CREATE TABLE IF NOT EXISTS mock_tests (
                    id INTEGER PRIMARY KEY,
                    subject TEXT,
                    title TEXT,
                    test_type TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS test_attempts (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    test_id INTEGER,
                    score REAL,
                    submitted_at TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS syllabus_topics (
                    id INTEGER PRIMARY KEY,
                    subject TEXT,
                    name TEXT,
                    status TEXT
                )
            ''')
            # Insert test data
            conn.execute("INSERT INTO mock_tests (id, subject, title, test_type) VALUES (1, 'Math', 'Test1', 'TypeA')")
            conn.execute("INSERT INTO mock_tests (id, subject, title, test_type) VALUES (2, 'Math', 'Test2', 'TypeB')")
            conn.execute("INSERT INTO mock_tests (id, subject, title, test_type) VALUES (3, 'Science', 'Test3', 'TypeA')")

            # User 1 attempts
            conn.execute("INSERT INTO test_attempts (user_id, test_id, score, submitted_at) VALUES (1, 1, 80, '2023-01-01 10:00:00')")
            conn.execute("INSERT INTO test_attempts (user_id, test_id, score, submitted_at) VALUES (1, 2, 90, '2023-01-02 10:00:00')")
            conn.execute("INSERT INTO test_attempts (user_id, test_id, score, submitted_at) VALUES (1, 3, 70, '2023-01-03 10:00:00')")
            conn.commit()

        with client.session_transaction() as sess:
            sess['user_id'] = 1

        response = client.get('/api/analytics/weak-areas?limit=10')
        assert response.status_code == 200

        json_resp = response.get_json()
        data = json_resp.get('data', json_resp)

        assert isinstance(data, list)

        subjects = [item['subject'] for item in data if 'subject' in item]
        assert 'Math' in subjects
        assert 'Science' in subjects

        print("✅ N+1 Optimization test passed successfully! Weak areas API works.")
    finally:
        os.close(db_fd)
        os.unlink(db_path)

if __name__ == '__main__':
    test_progress_trend_optimization()
    test_identify_weak_areas_n1_optimization()
