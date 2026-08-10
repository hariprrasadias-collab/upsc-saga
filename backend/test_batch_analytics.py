import sqlite3
import traceback

def get_all_subjects_performance(conn, user_id, subjects):
    """
    Batch aggregate all metrics for given subjects to eliminate N+1 queries.
    """
    results = {
        subject: {
            'subject': subject,
            'mock_avg': 0,
            'answer_avg': 0,
            'syllabus_pct': 0,
            'pyq_attempted': 0,
            'flashcard_mastered': 0
        } for subject in subjects
    }
    if not subjects:
        return []

    placeholders = ','.join(['?'] * len(subjects))

    # Mock tests
    try:
        mock_data = conn.execute(f'''
            SELECT mt.subject, AVG(score) as avg_score
            FROM test_attempts mta
            JOIN mock_tests mt ON mta.test_id = mt.id
            WHERE mta.user_id = ? AND mt.subject IN ({placeholders})
            GROUP BY mt.subject
        ''', [user_id] + subjects).fetchall()
        for row in mock_data:
            if row['avg_score']:
                results[row['subject']]['mock_avg'] = round(row['avg_score'], 1)
    except Exception as e:
        print("Mock test err:", e)

    # Answer writing
    try:
        answer_data = conn.execute(f'''
            SELECT aq.subject, AVG(ae.overall_score) as avg_score
            FROM answer_evaluations ae
            JOIN user_answers ua ON ae.answer_id = ua.id
            JOIN answer_questions aq ON ua.prompt_id = aq.id
            WHERE ua.user_id = ? AND aq.subject IN ({placeholders})
            GROUP BY aq.subject
        ''', [user_id] + subjects).fetchall()
        for row in answer_data:
            if row['avg_score']:
                results[row['subject']]['answer_avg'] = round(row['avg_score'], 1)
    except Exception as e:
        print("Answer writing err:", e)

    # Syllabus completion
    try:
        syllabus_data = conn.execute(f'''
            SELECT
                subject,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
            FROM syllabus_topics
            WHERE subject IN ({placeholders})
            GROUP BY subject
        ''', subjects).fetchall()
        for row in syllabus_data:
            if row['total'] > 0:
                results[row['subject']]['syllabus_pct'] = round((row['completed'] / row['total']) * 100, 1)
    except Exception as e:
        print("Syllabus err:", e)

    return [results[s] for s in subjects]


def test_it():
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.execute('CREATE TABLE test_attempts (id INTEGER, user_id INTEGER, test_id INTEGER, score REAL, submitted_at TEXT)')
    conn.execute('CREATE TABLE mock_tests (id INTEGER, subject TEXT)')
    conn.execute('CREATE TABLE syllabus_topics (subject TEXT, name TEXT, status TEXT)')

    conn.execute("INSERT INTO mock_tests VALUES (1, 'GS1')")
    conn.execute("INSERT INTO test_attempts VALUES (1, 1, 1, 50, '2023-01-01')")

    conn.execute("INSERT INTO syllabus_topics VALUES ('GS1', 'T1', 'Completed')")
    conn.execute("INSERT INTO syllabus_topics VALUES ('GS1', 'T2', 'Reading')")

    subjects = ['GS1', 'GS2', 'GS3']
    print(get_all_subjects_performance(conn, 1, subjects))

test_it()
