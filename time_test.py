from app import create_app
from app.db import get_db
import time
from app.services.analytics_service import get_subject_performance

app = create_app()

def test_original():
    with app.app_context():
        conn = get_db()
        user_id = 1
        subjects = ['GS1', 'GS2', 'GS3', 'GS4', 'Prelims', 'Optional']

        start = time.time()
        for _ in range(100):
            results = []
            for subject in subjects:
                try:
                    perf = get_subject_performance(conn, user_id, subject)
                    results.append(perf)
                except Exception:
                    pass
        end = time.time()
        print(f"Original: {end - start:.4f}s")

def get_all_subject_performances(conn, user_id, subjects):
    results = {subj: {
        'subject': subj, 'mock_avg': 0, 'answer_avg': 0,
        'syllabus_pct': 0, 'pyq_attempted': 0, 'flashcard_mastered': 0
    } for subj in subjects}

    if not subjects: return results

    placeholders = ','.join(['?'] * len(subjects))

    try:
        mock_avgs = conn.execute(f'''
            SELECT mt.subject, AVG(mta.score) as avg_score
            FROM test_attempts mta
            JOIN mock_tests mt ON mta.test_id = mt.id
            WHERE mta.user_id = ? AND mt.subject IN ({placeholders})
            GROUP BY mt.subject
        ''', [user_id] + subjects).fetchall()
        for row in mock_avgs:
            if row['avg_score']:
                results[row['subject']]['mock_avg'] = round(row['avg_score'], 1)
    except Exception: pass

    try:
        answer_avgs = conn.execute(f'''
            SELECT aq.subject, AVG(ae.overall_score) as avg_score
            FROM answer_evaluations ae
            JOIN user_answers ua ON ae.answer_id = ua.id
            JOIN answer_questions aq ON ua.prompt_id = aq.id
            WHERE ua.user_id = ? AND aq.subject IN ({placeholders})
            GROUP BY aq.subject
        ''', [user_id] + subjects).fetchall()
        for row in answer_avgs:
            if row['avg_score']:
                results[row['subject']]['answer_avg'] = round(row['avg_score'], 1)
    except Exception: pass

    try:
        syllabus = conn.execute(f'''
            SELECT subject, COUNT(*) as total, SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
            FROM syllabus_topics
            WHERE subject IN ({placeholders})
            GROUP BY subject
        ''', subjects).fetchall()
        for row in syllabus:
            if row['total'] > 0:
                results[row['subject']]['syllabus_pct'] = round((row['completed'] / row['total']) * 100, 1)
    except Exception: pass

    return results

def test_optimized():
    with app.app_context():
        conn = get_db()
        user_id = 1
        subjects = ['GS1', 'GS2', 'GS3', 'GS4', 'Prelims', 'Optional']

        start = time.time()
        for _ in range(100):
            try:
                perf_dict = get_all_subject_performances(conn, user_id, subjects)
                results = [perf_dict[subj] for subj in subjects]
            except Exception:
                pass
        end = time.time()
        print(f"Optimized: {end - start:.4f}s")

if __name__ == '__main__':
    test_original()
    test_optimized()
