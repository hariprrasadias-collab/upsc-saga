import sqlite3
from app.services.analytics_service_opt import get_all_subject_performances

def main():
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row

    # Create test schemas
    conn.execute('CREATE TABLE mock_tests (id INTEGER PRIMARY KEY, subject TEXT)')
    conn.execute('CREATE TABLE test_attempts (user_id INTEGER, test_id INTEGER, score REAL)')
    conn.execute('CREATE TABLE answer_questions (id INTEGER PRIMARY KEY, subject TEXT)')
    conn.execute('CREATE TABLE user_answers (id INTEGER PRIMARY KEY, user_id INTEGER, prompt_id INTEGER)')
    conn.execute('CREATE TABLE answer_evaluations (answer_id INTEGER, overall_score REAL)')
    conn.execute('CREATE TABLE syllabus_topics (subject TEXT, status TEXT)')

    subjects = ['GS1', 'GS2', 'GS3', 'GS4', 'Prelims', 'Optional']
    for idx, s in enumerate(subjects):
        conn.execute("INSERT INTO mock_tests (id, subject) VALUES (?, ?)", (idx + 1, s))
        conn.execute("INSERT INTO test_attempts (user_id, test_id, score) VALUES (?, ?, ?)", (1, idx + 1, 80 + idx))
        conn.execute("INSERT INTO syllabus_topics (subject, status) VALUES (?, 'Completed')", (s,))

        conn.execute("INSERT INTO answer_questions (id, subject) VALUES (?, ?)", (idx + 1, s))
        conn.execute("INSERT INTO user_answers (id, user_id, prompt_id) VALUES (?, ?, ?)", (idx + 1, 1, idx + 1))
        conn.execute("INSERT INTO answer_evaluations (answer_id, overall_score) VALUES (?, ?)", (idx + 1, 75 + idx))

    conn.commit()

    print("Testing bulk implementation")
    results = get_all_subject_performances(conn, 1, subjects)
    for res in results:
        print(res)
    print("Done")

main()
