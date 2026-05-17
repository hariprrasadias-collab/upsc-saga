"""
Weak Area Analyzer - Performance analysis engine
Analyzes quiz/test performance to identify weak topics and generate targeted practice
"""
import sqlite3
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'upsc_saga.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def record_attempt(question_id: int, topic: str, subject: str, is_correct: bool, time_taken: int = 0) -> None:
    """Record a question attempt for performance tracking"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO performance_records 
        (question_id, topic, subject, is_correct, time_taken, attempted_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (question_id, topic, subject, is_correct, time_taken, datetime.now()))

    conn.commit()
    conn.close()

    # Trigger weak area analysis for this topic
    analyze_topic_performance(topic)


def calculate_weakness_score(topic_data: Dict) -> float:
    """
    Calculate weakness score (0-100, higher = weaker)

    Factors:
    - Low accuracy (40%)
    - High time taken (30%)
    - Recency of failures (20%)
    - Number of attempts (10%)
    """
    accuracy = topic_data['accuracy_rate']
    avg_time = topic_data['avg_time_taken']
    attempts = topic_data['total_attempts']

    # Score components (inverted - lower is better)
    accuracy_score = (1 - accuracy) * 40  # 0-40 points

    # Time score (assuming 60s is average, >120s is slow)
    time_score = min(avg_time / 120.0, 1.0) * 30  # 0-30 points

    # Recency score (more recent failures = higher score)
    recency_score = topic_data.get('recent_failures', 0) * 10  # 0-20 points

    # Attempt score (fewer attempts = less confident in score)
    attempt_penalty = max(0, (10 - attempts) / 10) * 10  # 0-10 points

    weakness_score = accuracy_score + time_score + recency_score + attempt_penalty
    return min(100, max(0, weakness_score))


def analyze_topic_performance(topic: str) -> Dict:
    """Analyze performance for a specific topic and update weak_areas table"""
    conn = get_db()
    cursor = conn.cursor()

    # Get performance stats for this topic
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
            AVG(time_taken) as avg_time,
            subject
        FROM performance_records
        WHERE topic = ?
        GROUP BY subject
    ''', (topic,))

    result = cursor.fetchone()

    if not result or result['total'] == 0:
        conn.close()
        return {}

    total = result['total']
    correct = result['correct'] or 0
    accuracy = correct / total if total > 0 else 0
    avg_time = result['avg_time'] or 0
    subject = result['subject']

    # Check recent failures (last 7 days)
    cursor.execute('''
        SELECT COUNT(*) as recent_failures
        FROM performance_records
        WHERE topic = ? AND is_correct = 0 
        AND attempted_at >= datetime('now', '-7 days')
    ''', (topic,))

    recent_failures = cursor.fetchone()['recent_failures']

    topic_data = {
        'total_attempts': total,
        'correct_attempts': correct,
        'accuracy_rate': accuracy,
        'avg_time_taken': avg_time,
        'recent_failures': recent_failures
    }

    weakness_score = calculate_weakness_score(topic_data)

    # Update or insert into weak_areas
    cursor.execute('''
        INSERT INTO weak_areas 
        (topic, subject, total_attempts, correct_attempts, accuracy_rate, avg_time_taken, weakness_score, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(topic) DO UPDATE SET
            subject = excluded.subject,
            total_attempts = excluded.total_attempts,
            correct_attempts = excluded.correct_attempts,
            accuracy_rate = excluded.accuracy_rate,
            avg_time_taken = excluded.avg_time_taken,
            weakness_score = excluded.weakness_score,
            last_updated = excluded.last_updated
    ''', (topic, subject, total, correct, accuracy, avg_time, weakness_score, datetime.now()))

    conn.commit()
    conn.close()

    return {
        'topic': topic,
        'subject': subject,
        'weakness_score': weakness_score,
        **topic_data
    }


def analyze_all_performance() -> List[Dict]:
    """Analyze performance for all topics with attempts"""
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Get stats for ALL topics at once
    cursor.execute('''
        SELECT
            topic,
            COUNT(*) as total,
            SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
            AVG(time_taken) as avg_time,
            subject
        FROM performance_records
        WHERE topic IS NOT NULL
        GROUP BY topic
    ''')
    stats_rows = cursor.fetchall()

    # 2. Get recent failures for ALL topics at once
    cursor.execute('''
        SELECT topic, COUNT(*) as recent_failures
        FROM performance_records
        WHERE is_correct = 0
        AND attempted_at >= datetime('now', '-7 days')
        AND topic IS NOT NULL
        GROUP BY topic
    ''')
    recent_failure_map = {row['topic']: row['recent_failures']
                          for row in cursor.fetchall()}

    results = []
    updates = []
    now = datetime.now()

    for row in stats_rows:
        topic = row['topic']
        total = row['total']
        correct = row['correct'] or 0
        accuracy = correct / total if total > 0 else 0
        avg_time = row['avg_time'] or 0
        subject = row['subject']
        recent_failures = recent_failure_map.get(topic, 0)

        topic_data = {
            'total_attempts': total,
            'correct_attempts': correct,
            'accuracy_rate': accuracy,
            'avg_time_taken': avg_time,
            'recent_failures': recent_failures
        }

        weakness_score = calculate_weakness_score(topic_data)

        updates.append((
            topic, subject, total, correct, accuracy, avg_time, weakness_score, now.strftime(
                '%Y-%m-%d %H:%M:%S')
        ))

        results.append({
            'topic': topic,
            'subject': subject,
            'weakness_score': weakness_score,
            **topic_data
        })

    if updates:
        cursor.executemany('''
            INSERT INTO weak_areas
            (topic, subject, total_attempts, correct_attempts, accuracy_rate, avg_time_taken, weakness_score, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(topic) DO UPDATE SET
                subject = excluded.subject,
                total_attempts = excluded.total_attempts,
                correct_attempts = excluded.correct_attempts,
                accuracy_rate = excluded.accuracy_rate,
                avg_time_taken = excluded.avg_time_taken,
                weakness_score = excluded.weakness_score,
                last_updated = excluded.last_updated
        ''', updates)
        conn.commit()

    conn.close()

    return sorted(results, key=lambda x: x['weakness_score'], reverse=True)


def get_weak_areas(limit: int = 10) -> List[Dict]:
    """Get top weak areas sorted by weakness score"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM weak_areas
        ORDER BY weakness_score DESC
        LIMIT ?
    ''', (limit,))

    weak_areas = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return weak_areas


def get_dashboard_stats() -> Dict:
    """Get statistics for weak areas dashboard"""
    conn = get_db()
    cursor = conn.cursor()

    # Total questions attempted
    cursor.execute('SELECT COUNT(*) as total FROM performance_records')
    total_attempts = cursor.fetchone()['total']

    # Overall accuracy
    cursor.execute('''
        SELECT 
            SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as accuracy
        FROM performance_records
    ''')
    overall_accuracy = cursor.fetchone()['accuracy'] or 0

    # Subject breakdown
    cursor.execute('''
        SELECT subject, 
               COUNT(*) as attempts,
               SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as accuracy
        FROM performance_records
        WHERE subject IS NOT NULL
        GROUP BY subject
    ''')
    subject_breakdown = [dict(row) for row in cursor.fetchall()]

    # Weak topics count
    cursor.execute(
        'SELECT COUNT(*) as count FROM weak_areas WHERE weakness_score > 50')
    weak_topics_count = cursor.fetchone()['count']

    conn.close()

    return {
        'total_attempts': total_attempts,
        'overall_accuracy': round(overall_accuracy * 100, 1),
        'subject_breakdown': subject_breakdown,
        'weak_topics_count': weak_topics_count
    }


def generate_practice_set(weak_topics: List[str], count: int = 10) -> List[Dict]:
    """Generate targeted practice questions from weak topics"""
    conn = get_db()
    cursor = conn.cursor()

    # Get questions from weak topics
    placeholders = ','.join('?' * len(weak_topics))
    cursor.execute(f'''
        SELECT DISTINCT id, question_text as question, subject, topic, difficulty
        FROM pyq_questions
        WHERE topic IN ({placeholders})
        ORDER BY RANDOM()
        LIMIT ?
    ''', (*weak_topics, count))

    questions = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return questions


def track_improvement(topic: str, days: int = 30) -> List[Dict]:
    """Track performance improvement for a topic over time"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            DATE(attempted_at) as date,
            COUNT(*) as attempts,
            SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as accuracy
        FROM performance_records
        WHERE topic = ? AND attempted_at >= datetime('now', ? || ' days')
        GROUP BY DATE(attempted_at)
        ORDER BY date
    ''', (topic, -days))

    timeline = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return timeline
