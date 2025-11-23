"""
Analytics Service - Data aggregation and insights
Consolidates data from all modules for comprehensive analytics
"""
from datetime import datetime, timedelta
from collections import defaultdict
import sqlite3

def calculate_study_hours(conn, user_id, start_date, end_date):
    """
    Estimate study hours based on activity timestamps
    """
    # Get all activity timestamps across modules
    activities = []
    
    # Mock tests
    mock_tests = conn.execute('''
        SELECT submitted_at FROM mock_test_attempts
        WHERE user_id = ? AND submitted_at BETWEEN ? AND ?
        ORDER BY submitted_at
    ''', (user_id, start_date, end_date)).fetchall()
    activities.extend([r['submitted_at'] for r in mock_tests])
    
    # Answer writing
    answers = conn.execute('''
        SELECT submitted_at FROM answer_submissions
        WHERE user_id = ? AND submitted_at BETWEEN ? AND ?
        ORDER BY submitted_at
    ''', (user_id, start_date, end_date)).fetchall()
    activities.extend([r['submitted_at'] for r in answers])
    
    # Flashcard reviews
    reviews = conn.execute('''
        SELECT reviewed_at FROM review_sessions
        WHERE user_id = ? AND reviewed_at BETWEEN ? AND ?
        ORDER BY reviewed_at
    ''', (user_id, start_date, end_date)).fetchall()
    activities.extend([r['reviewed_at'] for r in reviews])
    
    if not activities:
        return 0
    
    # Sort all activities
    activities = sorted([datetime.fromisoformat(a) for a in activities])
    
    # Estimate: assume 30min per mock test, 20min per answer, 10min per review session
    # Or calculate gaps between activities (if < 2 hours, count as continuous)
    total_hours = 0
    
    # Count unique days with activity and estimate
    unique_days = set(a.date() for a in activities)
    # Conservative estimate: 2 hours per active day
    total_hours = len(unique_days) * 2
    
    return round(total_hours, 1)


def get_subject_performance(conn, user_id, subject):
    """
    Aggregate all metrics for a specific subject
    """
    result = {
        'subject': subject,
        'mock_avg': 0,
        'answer_avg': 0,
        'syllabus_pct': 0,
        'pyq_attempted': 0,
        'flashcard_mastered': 0
    }
    
    # Mock tests
    mock_avg = conn.execute('''
        SELECT AVG(score) as avg_score
        FROM mock_test_attempts mta
        JOIN mock_tests mt ON mta.test_id = mt.id
        WHERE mta.user_id = ? AND mt.subject = ?
    ''', (user_id, subject)).fetchone()
    if mock_avg and mock_avg['avg_score']:
        result['mock_avg'] = round(mock_avg['avg_score'], 1)
    
    # Answer writing
    answer_avg = conn.execute('''
        SELECT AVG(overall_score) as avg_score
        FROM answer_submissions ans
        JOIN answer_questions aq ON ans.question_id = aq.id
        WHERE ans.user_id = ? AND aq.subject = ?
    ''', (user_id, subject)).fetchone()
    if answer_avg and answer_avg['avg_score']:
        result['answer_avg'] = round(answer_avg['avg_score'], 1)
    
    # Syllabus completion
    syllabus = conn.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
        FROM syllabus_topics
        WHERE subject = ?
    ''', (subject,)).fetchone()
    if syllabus and syllabus['total'] > 0:
        result['syllabus_pct'] = round((syllabus['completed'] / syllabus['total']) * 100, 1)
    
    return result


def identify_weak_areas(conn, user_id, limit=10):
    """
    Identify topics needing attention based on performance
    """
    weak_areas = []
    
    # Check syllabus topics not started or in progress
    syllabus_weak = conn.execute('''
        SELECT subject, name, status
        FROM syllabus_topics
        WHERE status IN ('Not Started', 'Reading')
        ORDER BY subject, name
        LIMIT ?
    ''', (limit,)).fetchall()
    
    for topic in syllabus_weak:
        weak_areas.append({
            'topic': f"{topic['subject']}: {topic['name']}",
            'weakness_score': 80 if topic['status'] == 'Not Started' else 50,
            'source': 'Syllabus',
            'action': 'Start reading' if topic['status'] == 'Not Started' else 'Complete reading'
        })
    
    # Check mock test subjects with low scores
    low_scores = conn.execute('''
        SELECT mt.subject, AVG(mta.score) as avg_score, COUNT(*) as attempts
        FROM mock_test_attempts mta
        JOIN mock_tests mt ON mta.test_id = mt.id
        WHERE mta.user_id = ?
        GROUP BY mt.subject
        HAVING avg_score < 50
        ORDER BY avg_score ASC
        LIMIT ?
    ''', (user_id, limit)).fetchall()
    
    for subj in low_scores:
        weak_areas.append({
            'topic': f"{subj['subject']} (Mock Tests)",
            'weakness_score': max(0, 100 - subj['avg_score']),
            'source': 'Mock Tests',
            'action': f"Practice more {subj['subject']} questions"
        })
    
    # Sort by weakness score and limit
    weak_areas.sort(key=lambda x: x['weakness_score'], reverse=True)
    return weak_areas[:limit]


def calculate_improvement_rate(scores):
    """
    Calculate improvement rate percentage
    """
    if len(scores) < 2:
        return 0
    
    first_half = scores[:len(scores)//2]
    second_half = scores[len(scores)//2:]
    
    avg_first = sum(first_half) / len(first_half) if first_half else 0
    avg_second = sum(second_half) / len(second_half) if second_half else 0
    
    if avg_first == 0:
        return 0
    
    improvement = ((avg_second - avg_first) / avg_first) * 100
    return round(improvement, 1)


def get_streak_days(conn, user_id):
    """
    Calculate consecutive days with activity
    """
    # Get all activity dates
    dates = set()
    
    # Mock tests
    mock_dates = conn.execute('''
        SELECT DATE(submitted_at) as date FROM mock_test_attempts
        WHERE user_id = ?
    ''', (user_id,)).fetchall()
    dates.update([r['date'] for r in mock_dates])
    
    # Answer writing
    answer_dates = conn.execute('''
        SELECT DATE(submitted_at) as date FROM answer_submissions
        WHERE user_id = ?
    ''', (user_id,)).fetchall()
    dates.update([r['date'] for r in answer_dates])
    
    # Flashcards
    review_dates = conn.execute('''
        SELECT DATE(reviewed_at) as date FROM review_sessions
        WHERE user_id = ?
    ''', (user_id,)).fetchall()
    dates.update([r['date'] for r in review_dates])
    
    if not dates:
        return 0
    
    # Sort dates
    sorted_dates = sorted([datetime.fromisoformat(d).date() for d in dates], reverse=True)
    
    # Count consecutive days from today
    today = datetime.now().date()
    streak = 0
    
    for i, date in enumerate(sorted_dates):
        expected_date = today - timedelta(days=i)
        if date == expected_date:
            streak += 1
        else:
            break
    
    return streak
