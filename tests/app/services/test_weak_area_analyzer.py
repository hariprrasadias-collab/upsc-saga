import pytest
import sqlite3
import os
import sys
from unittest.mock import patch
from datetime import datetime

# Make sure we can import app correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'backend')))

from app.services.weak_area_analyzer import (
    record_attempt,
    calculate_weakness_score,
    analyze_topic_performance,
    analyze_all_performance,
    get_weak_areas,
    get_dashboard_stats,
    generate_practice_set,
    track_improvement
)

@pytest.fixture
def mock_db():
    # Create an in-memory database
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Create performance_records table
    cursor.execute('''
        CREATE TABLE performance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            question_id INTEGER NOT NULL,
            topic TEXT,
            subject TEXT,
            is_correct BOOLEAN NOT NULL,
            time_taken INTEGER,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Create weak_areas table
    cursor.execute('''
        CREATE TABLE weak_areas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL UNIQUE,
            subject TEXT,
            total_attempts INTEGER DEFAULT 0,
            correct_attempts INTEGER DEFAULT 0,
            accuracy_rate REAL DEFAULT 0.0,
            avg_time_taken REAL DEFAULT 0.0,
            weakness_score REAL DEFAULT 0.0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Create pyq_questions table to test generate_practice_set
    cursor.execute('''
        CREATE TABLE pyq_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT,
            subject TEXT,
            topic TEXT,
            difficulty TEXT
        );
    ''')

    conn.commit()

    # Yield the connection for testing

    # We need to mock get_db differently because the original code calls conn.close()
    # If it returns the same connection every time, the first conn.close() will close it for everyone
    # Instead, we yield the conn, but when get_db is called, we return a mock that prevents close()
    # or just patch it so it returns the open connection and ignores close.

    class MockConn:
        def __init__(self, real_conn):
            self.real_conn = real_conn
            self.row_factory = real_conn.row_factory

        def cursor(self):
            return self.real_conn.cursor()

        def commit(self):
            self.real_conn.commit()

        def execute(self, *args, **kwargs):
            return self.real_conn.execute(*args, **kwargs)

        def close(self):
            # Do nothing to keep the connection alive during the test
            pass

    mock_conn = MockConn(conn)

    with patch('app.services.weak_area_analyzer.get_db', return_value=mock_conn):
        yield conn

    # Cleanup
    conn.close()

def test_mock_db_setup(mock_db):
    cursor = mock_db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row['name'] for row in cursor.fetchall()]
    assert 'performance_records' in tables
    assert 'weak_areas' in tables
    assert 'pyq_questions' in tables

@patch('app.services.weak_area_analyzer.analyze_topic_performance')
def test_record_attempt(mock_analyze, mock_db):
    # Test record attempt function
    question_id = 1
    topic = "Polity"
    subject = "Indian Polity"
    is_correct = True
    time_taken = 45

    # Call the function
    record_attempt(question_id, topic, subject, is_correct, time_taken)

    # Verify insertion in performance_records
    cursor = mock_db.cursor()
    cursor.execute("SELECT * FROM performance_records")
    records = cursor.fetchall()

    assert len(records) == 1
    record = records[0]

    assert record['question_id'] == question_id
    assert record['topic'] == topic
    assert record['subject'] == subject
    assert bool(record['is_correct']) == is_correct
    assert record['time_taken'] == time_taken
    assert record['attempted_at'] is not None

    # Verify analyze_topic_performance was called to trigger weak area analysis
    mock_analyze.assert_called_once_with(topic)

def test_calculate_weakness_score_high_accuracy():
    # Good performance: 100% accuracy, fast, 10 attempts
    topic_data = {
        'accuracy_rate': 1.0,
        'avg_time_taken': 30, # fast
        'total_attempts': 10,
        'recent_failures': 0
    }
    score = calculate_weakness_score(topic_data)

    # Expected:
    # accuracy_score = 0 * 40 = 0
    # time_score = (30 / 120.0) * 30 = 7.5
    # recency_score = 0 * 10 = 0
    # attempt_penalty = max(0, (10 - 10) / 10) * 10 = 0
    # total = 7.5
    assert 7.4 < score < 7.6

def test_calculate_weakness_score_low_accuracy():
    # Poor performance: 0% accuracy, slow, 10 attempts
    topic_data = {
        'accuracy_rate': 0.0,
        'avg_time_taken': 150, # slow (capped at 1.0)
        'total_attempts': 10,
        'recent_failures': 5
    }
    score = calculate_weakness_score(topic_data)

    # Expected:
    # accuracy_score = 1 * 40 = 40
    # time_score = min(150 / 120.0, 1.0) * 30 = 1.0 * 30 = 30
    # recency_score = 5 * 10 = 50
    # attempt_penalty = 0
    # total = 40 + 30 + 50 + 0 = 120 -> capped at 100
    assert score == 100

def test_calculate_weakness_score_few_attempts():
    # Penalty for few attempts: 100% accuracy, fast, 2 attempts
    topic_data = {
        'accuracy_rate': 1.0,
        'avg_time_taken': 60,
        'total_attempts': 2,
        'recent_failures': 0
    }
    score = calculate_weakness_score(topic_data)

    # Expected:
    # accuracy_score = 0
    # time_score = (60 / 120.0) * 30 = 15
    # recency_score = 0
    # attempt_penalty = max(0, (10 - 2) / 10) * 10 = 8
    # total = 15 + 8 = 23
    assert score == 23

def test_calculate_weakness_score_average():
    # Average performance: 60% accuracy, 60s, 5 attempts
    topic_data = {
        'accuracy_rate': 0.6,
        'avg_time_taken': 60,
        'total_attempts': 5,
        'recent_failures': 1
    }
    score = calculate_weakness_score(topic_data)

    # Expected:
    # accuracy_score = (1 - 0.6) * 40 = 16
    # time_score = (60 / 120.0) * 30 = 15
    # recency_score = 1 * 10 = 10
    # attempt_penalty = max(0, (10 - 5) / 10) * 10 = 5
    # total = 16 + 15 + 10 + 5 = 46
    assert score == 46

def test_analyze_topic_performance(mock_db):
    cursor = mock_db.cursor()

    # Insert dummy performance records for a topic
    # 3 attempts, 1 correct, 2 incorrect, avg time 60s
    now = datetime.now()
    records = [
        (1, 101, 'Economy', 'Macroeconomics', 1, 30, now),
        (1, 102, 'Economy', 'Macroeconomics', 0, 90, now),
        (1, 103, 'Economy', 'Macroeconomics', 0, 60, now)
    ]

    cursor.executemany('''
        INSERT INTO performance_records
        (user_id, question_id, topic, subject, is_correct, time_taken, attempted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', records)
    mock_db.commit()

    # Analyze topic
    result = analyze_topic_performance('Economy')

    # Verify return dictionary
    assert result['topic'] == 'Economy'
    assert result['subject'] == 'Macroeconomics'
    assert result['total_attempts'] == 3
    assert result['correct_attempts'] == 1
    assert abs(result['accuracy_rate'] - 0.333) < 0.01
    assert result['avg_time_taken'] == 60
    assert result['recent_failures'] == 2

    # Verify database update in weak_areas
    cursor.execute("SELECT * FROM weak_areas WHERE topic = 'Economy'")
    weak_area = cursor.fetchone()

    assert weak_area is not None
    assert weak_area['subject'] == 'Macroeconomics'
    assert weak_area['total_attempts'] == 3
    assert weak_area['correct_attempts'] == 1
    assert abs(weak_area['accuracy_rate'] - 0.333) < 0.01
    assert weak_area['avg_time_taken'] == 60
    assert weak_area['weakness_score'] == result['weakness_score']

def test_analyze_topic_performance_no_data(mock_db):
    # Should return empty dict when no data is found
    result = analyze_topic_performance('NonExistentTopic')
    assert result == {}
