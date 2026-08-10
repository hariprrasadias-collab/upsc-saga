import sqlite3
import traceback
from app.services.analytics_service import identify_weak_areas
import datetime

def test_it():
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.execute('CREATE TABLE test_attempts (id INTEGER, user_id INTEGER, test_id INTEGER, score REAL, submitted_at TEXT)')
    conn.execute('CREATE TABLE mock_tests (id INTEGER, subject TEXT)')
    conn.execute('CREATE TABLE syllabus_topics (subject TEXT, name TEXT, status TEXT)')

    conn.execute("INSERT INTO mock_tests VALUES (1, 'Math')")
    conn.execute("INSERT INTO test_attempts VALUES (1, 1, 1, 50, '2023-01-01')")

    print(identify_weak_areas(conn, 1))

test_it()
