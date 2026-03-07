import sqlite3
import json
from datetime import datetime
from collections import defaultdict
import os
import sys

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.analytics_service import identify_weak_areas, calculate_improvement_rate

def setup_test_db():
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row

    # Create tables
    conn.executescript('''
        CREATE TABLE syllabus_topics (
            id INTEGER PRIMARY KEY,
            subject TEXT,
            name TEXT,
            status TEXT
        );
        CREATE TABLE mock_tests (
            id INTEGER PRIMARY KEY,
            subject TEXT
        );
        CREATE TABLE test_attempts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            test_id INTEGER,
            score REAL,
            submitted_at TEXT
        );
    ''')

    # Insert data
    conn.executescript('''
        INSERT INTO syllabus_topics (subject, name, status) VALUES
            ('History', 'Ancient India', 'Not Started'),
            ('Geography', 'Physical Geography', 'Reading');

        INSERT INTO mock_tests (id, subject) VALUES
            (1, 'History'),
            (2, 'Geography'),
            (3, 'Polity');

        -- User 1 History Attempts
        INSERT INTO test_attempts (user_id, test_id, score, submitted_at) VALUES
            (1, 1, 30, '2023-01-01'),
            (1, 1, 35, '2023-01-02'),
            (1, 1, 40, '2023-01-03'),
            (1, 1, 38, '2023-01-04'),
            (1, 1, 45, '2023-01-05');

        -- User 1 Geography Attempts
        INSERT INTO test_attempts (user_id, test_id, score, submitted_at) VALUES
            (1, 2, 80, '2023-01-01'),
            (1, 2, 85, '2023-01-02');

        -- User 1 Polity Attempts (Empty)
    ''')
    return conn

def original_identify_weak_areas(conn, user_id, limit=10):
    weak_areas = []

    try:
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
                'subject': topic['subject'],
                'topic': f"{topic['name']}",
                'weakness_score': 80 if topic['status'] == 'Not Started' else 50,
                'source': 'Syllabus',
                'action': 'Start reading' if topic['status'] == 'Not Started' else 'Complete reading'
            })

        # Check mock test subjects with low scores (get bottom performing ones)
        low_scores = conn.execute('''
            SELECT mt.subject, AVG(mta.score) as avg_score, COUNT(*) as attempts
            FROM test_attempts mta
            JOIN mock_tests mt ON mta.test_id = mt.id
            WHERE mta.user_id = ?
            GROUP BY mt.subject
            ORDER BY avg_score ASC
            LIMIT ?
        ''', (user_id, limit)).fetchall()

        for subj in low_scores:
            # Calculate trend for this subject
            subject_scores = conn.execute('''
                SELECT mta.score, mta.submitted_at
                FROM test_attempts mta
                JOIN mock_tests mt ON mta.test_id = mt.id
                WHERE mta.user_id = ? AND mt.subject = ?
                ORDER BY mta.submitted_at ASC
            ''', (user_id, subj['subject'])).fetchall()

            scores_list = [s['score'] for s in subject_scores]
            trend_val = calculate_improvement_rate(scores_list)
            trend_direction = 'improving' if trend_val > 0 else 'declining' if trend_val < 0 else 'stable'

            # Get last 5 scores for sparkline
            recent_scores = scores_list[-5:] if scores_list else []
            last_attempt = subject_scores[-1]['submitted_at'] if subject_scores else None

            weak_areas.append({
                'subject': subj['subject'],
                'topic': f"{subj['subject']} (Mock Tests)",
                'weakness_score': max(0, 100 - (subj['avg_score'] or 0)),
                'source': 'Mock Tests',
                'action': f"Practice {subj['subject']} questions",
                'trend': trend_direction,
                'trend_value': abs(trend_val),
                'impact': 'High' if (subj['avg_score'] or 0) < 40 else 'Medium',
                'recent_scores': recent_scores,
                'last_attempt': last_attempt
            })
    except Exception as e:
        print(f"Error identifying weak areas: {e}")

    # Sort by weakness score and limit
    weak_areas.sort(key=lambda x: x['weakness_score'], reverse=True)
    return weak_areas[:limit]

def main():
    conn = setup_test_db()

    original_results = original_identify_weak_areas(conn, 1)
    optimized_results = identify_weak_areas(conn, 1)

    orig_json = json.dumps(original_results, sort_keys=True, indent=2)
    opt_json = json.dumps(optimized_results, sort_keys=True, indent=2)

    if orig_json == opt_json:
        print("✅ SUCCESS: Output matches perfectly!")
    else:
        print("❌ FAILED: Output mismatches!")
        print("--- Original ---")
        print(orig_json)
        print("--- Optimized ---")
        print(opt_json)

if __name__ == '__main__':
    main()
