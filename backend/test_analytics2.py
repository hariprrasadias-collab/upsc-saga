import sqlite3
from app.services.analytics_service import get_subject_performance

def main():
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row

    # Create test schemas
    conn.execute('''
        CREATE TABLE mock_tests (id INTEGER PRIMARY KEY, subject TEXT)
    ''')
    conn.execute('''
        CREATE TABLE test_attempts (user_id INTEGER, test_id INTEGER, score REAL)
    ''')
    conn.execute('''
        CREATE TABLE answer_questions (id INTEGER PRIMARY KEY, subject TEXT)
    ''')
    conn.execute('''
        CREATE TABLE user_answers (id INTEGER PRIMARY KEY, user_id INTEGER, prompt_id INTEGER)
    ''')
    conn.execute('''
        CREATE TABLE answer_evaluations (answer_id INTEGER, overall_score REAL)
    ''')
    conn.execute('''
        CREATE TABLE syllabus_topics (subject TEXT, status TEXT)
    ''')

    # Seed data for Geography
    conn.execute("INSERT INTO mock_tests (id, subject) VALUES (1, 'Geography')")
    conn.execute("INSERT INTO mock_tests (id, subject) VALUES (2, 'History')")

    conn.execute("INSERT INTO test_attempts (user_id, test_id, score) VALUES (1, 1, 80)")
    conn.execute("INSERT INTO test_attempts (user_id, test_id, score) VALUES (1, 1, 90)")
    conn.execute("INSERT INTO test_attempts (user_id, test_id, score) VALUES (1, 2, 70)")

    conn.execute("INSERT INTO syllabus_topics (subject, status) VALUES ('Geography', 'Completed')")
    conn.execute("INSERT INTO syllabus_topics (subject, status) VALUES ('Geography', 'Completed')")
    conn.execute("INSERT INTO syllabus_topics (subject, status) VALUES ('Geography', 'Not Started')")
    conn.execute("INSERT INTO syllabus_topics (subject, status) VALUES ('History', 'Completed')")

    # Answer writing
    conn.execute("INSERT INTO answer_questions (id, subject) VALUES (1, 'Geography')")
    conn.execute("INSERT INTO user_answers (id, user_id, prompt_id) VALUES (1, 1, 1)")
    conn.execute("INSERT INTO answer_evaluations (answer_id, overall_score) VALUES (1, 85.5)")

    conn.commit()

    print("Geography:")
    print(get_subject_performance(conn, 1, 'Geography'))

    print("\nHistory:")
    print(get_subject_performance(conn, 1, 'History'))

main()
