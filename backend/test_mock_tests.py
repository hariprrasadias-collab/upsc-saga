import sys
import json
from app import create_app
from app.db import get_db

app = create_app()

with app.app_context():
    conn = get_db()

    # Temporarily disable foreign keys for the test setup if needed, or figure out the missing constraint
    conn.execute("PRAGMA foreign_keys=OFF")

    # Create test
    conn.execute("INSERT INTO mock_tests (title, test_type, subject, description, difficulty, total_questions, duration_minutes, total_marks) VALUES ('Test', 'smart_test', 'General', 'Desc', 'Medium', 1, 30, 2)")
    test_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.execute("INSERT INTO test_questions (test_id, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer) VALUES (?, 1, 'Q', 'A', 'B', 'C', 'D', 'A')", (test_id,))

    # Create attempt for user 2
    conn.execute("INSERT INTO test_attempts (user_id, test_id, status) VALUES (2, ?, 'in_progress')", (test_id,))
    attempt_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.commit()
    conn.execute("PRAGMA foreign_keys=ON")

client = app.test_client()

res = client.post(f'/api/mock-tests/{test_id}/start')
print(res.status_code, "start test")

res = client.put(f'/api/mock-tests/attempt/{attempt_id}/answer', json={'question_id': 1, 'selected_answer': 'B'})
print(res.status_code, "answer idor")

res = client.post(f'/api/mock-tests/attempt/{attempt_id}/submit')
print(res.status_code, "submit idor")

res = client.get(f'/api/mock-tests/attempt/{attempt_id}/results')
print(res.status_code, "results idor")
