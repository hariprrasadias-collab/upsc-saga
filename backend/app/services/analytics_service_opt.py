import sqlite3

def get_all_subject_performances(conn, user_id, subjects):
    """
    Fetch performance metrics for all given subjects in bulk to avoid N+1 queries.
    """
    if not subjects:
        return []

    results = {s: {
        'subject': s,
        'mock_avg': 0,
        'answer_avg': 0,
        'syllabus_pct': 0,
        'pyq_attempted': 0,
        'flashcard_mastered': 0
    } for s in subjects}

    placeholders = ','.join(['?']*len(subjects))

    try:
        # Bulk Mock tests
        mock_query = f'''
            SELECT mt.subject, AVG(mta.score) as avg_score
            FROM test_attempts mta
            JOIN mock_tests mt ON mta.test_id = mt.id
            WHERE mta.user_id = ? AND mt.subject IN ({placeholders})
            GROUP BY mt.subject
        '''
        params = [user_id] + subjects
        for row in conn.execute(mock_query, params).fetchall():
            if row['avg_score']:
                results[row['subject']]['mock_avg'] = round(row['avg_score'], 1)
    except Exception as e:
        print(f"Mock bulk error: {e}")

    try:
        # Bulk Answer writing
        answer_query = f'''
            SELECT aq.subject, AVG(ae.overall_score) as avg_score
            FROM answer_evaluations ae
            JOIN user_answers ua ON ae.answer_id = ua.id
            JOIN answer_questions aq ON ua.prompt_id = aq.id
            WHERE ua.user_id = ? AND aq.subject IN ({placeholders})
            GROUP BY aq.subject
        '''
        params = [user_id] + subjects
        for row in conn.execute(answer_query, params).fetchall():
            if row['avg_score']:
                results[row['subject']]['answer_avg'] = round(row['avg_score'], 1)
    except Exception as e:
        print(f"Answer bulk error: {e}")

    try:
        # Bulk Syllabus completion
        syllabus_query = f'''
            SELECT
                subject,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
            FROM syllabus_topics
            WHERE subject IN ({placeholders})
            GROUP BY subject
        '''
        params = subjects
        for row in conn.execute(syllabus_query, params).fetchall():
            if row['total'] > 0:
                results[row['subject']]['syllabus_pct'] = round((row['completed'] / row['total']) * 100, 1)
    except Exception as e:
        print(f"Syllabus bulk error: {e}")

    return [results[s] for s in subjects]
