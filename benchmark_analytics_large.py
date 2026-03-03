import sqlite3
import time
from collections import defaultdict

conn = sqlite3.connect(':memory:')
conn.row_factory = sqlite3.Row

# Create schema
conn.execute('''CREATE TABLE mock_tests (id INTEGER PRIMARY KEY, subject TEXT)''')
conn.execute('''CREATE TABLE test_attempts (id INTEGER PRIMARY KEY, user_id INTEGER, test_id INTEGER, score REAL, submitted_at TEXT)''')
conn.execute('''CREATE TABLE syllabus_topics (id INTEGER PRIMARY KEY, subject TEXT, name TEXT, status TEXT)''')

subjects = [f'Subject_{i}' for i in range(50)]
for i, subj in enumerate(subjects):
    conn.execute('INSERT INTO mock_tests (id, subject) VALUES (?, ?)', (i+1, subj))

import random
random.seed(42)
for user_id in [1]:
    for test_id in range(1, 51):
        for attempt in range(50):
            score = random.randint(30, 100)
            submitted_at = f'2023-01-{random.randint(10, 31)} 10:00:00'
            conn.execute('INSERT INTO test_attempts (user_id, test_id, score, submitted_at) VALUES (?, ?, ?, ?)', (user_id, test_id, score, submitted_at))

from backend.app.services.analytics_service import identify_weak_areas

start = time.time()
for _ in range(100):
    areas = identify_weak_areas(conn, 1, 15)
end = time.time()

print(f"Time taken: {end - start:.4f} seconds")
