import pytest
from app.services.weak_area_analyzer import analyze_all_performance, get_db

def test_analyze_all_performance():
    conn = get_db()
    cursor = conn.cursor()

    # clean table before
    cursor.execute('DELETE FROM performance_records WHERE topic IN ("TestTopic1", "TestTopic2")')
    cursor.execute('DELETE FROM weak_areas WHERE topic IN ("TestTopic1", "TestTopic2")')

    # Add some dummy data to ensure we have something to test
    cursor.execute('''
        INSERT INTO performance_records
        (question_id, topic, subject, is_correct, time_taken, attempted_at)
        VALUES (1, 'TestTopic1', 'TestSubject1', 1, 60, datetime('now'))
    ''')
    cursor.execute('''
        INSERT INTO performance_records
        (question_id, topic, subject, is_correct, time_taken, attempted_at)
        VALUES (2, 'TestTopic1', 'TestSubject1', 0, 120, datetime('now'))
    ''')
    cursor.execute('''
        INSERT INTO performance_records
        (question_id, topic, subject, is_correct, time_taken, attempted_at)
        VALUES (3, 'TestTopic2', 'TestSubject2', 1, 30, datetime('now'))
    ''')
    conn.commit()

    results = analyze_all_performance()

    assert isinstance(results, list)
    assert len(results) >= 2

    topics = {r['topic'] for r in results}
    assert 'TestTopic1' in topics
    assert 'TestTopic2' in topics

    topic1_data = next(r for r in results if r['topic'] == 'TestTopic1')
    assert topic1_data['total_attempts'] == 2
    assert topic1_data['correct_attempts'] == 1
    assert topic1_data['accuracy_rate'] == 0.5
    assert topic1_data['avg_time_taken'] == 90.0
    assert topic1_data['recent_failures'] == 1

    topic2_data = next(r for r in results if r['topic'] == 'TestTopic2')
    assert topic2_data['total_attempts'] == 1
    assert topic2_data['correct_attempts'] == 1
    assert topic2_data['accuracy_rate'] == 1.0
    assert topic2_data['avg_time_taken'] == 30.0
    assert topic2_data['recent_failures'] == 0

    # check that table is updated
    weak_areas = cursor.execute('SELECT * FROM weak_areas WHERE topic IN ("TestTopic1", "TestTopic2")').fetchall()
    assert len(weak_areas) == 2

    # cleanup
    cursor.execute('DELETE FROM performance_records WHERE topic IN ("TestTopic1", "TestTopic2")')
    cursor.execute('DELETE FROM weak_areas WHERE topic IN ("TestTopic1", "TestTopic2")')
    conn.commit()
    conn.close()
