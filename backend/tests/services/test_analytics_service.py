import pytest
import sqlite3
import sys
import os

# Ensure the app module can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.services.analytics_service import get_streak_days

@pytest.fixture
def db_conn():
    """Create an in-memory database with the necessary schema."""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row  # To allow dict-like access as used in the service

    # Create required tables for get_streak_days
    conn.execute('''
        CREATE TABLE test_attempts (
            user_id INTEGER,
            submitted_at TEXT
        )
    ''')

    conn.execute('''
        CREATE TABLE user_answers (
            user_id INTEGER,
            submitted_at TEXT
        )
    ''')

    conn.execute('''
        CREATE TABLE review_sessions (
            user_id INTEGER,
            reviewed_at TEXT
        )
    ''')

    conn.execute('''
        CREATE TABLE pomodoro_sessions (
            user_id INTEGER,
            timestamp TEXT
        )
    ''')

    conn.execute('''
        CREATE TABLE calendar_event_metadata (
            user_id INTEGER,
            is_completed INTEGER,
            updated_at TEXT
        )
    ''')

    yield conn

    conn.close()

def test_get_streak_days_empty_history(db_conn):
    """
    Test that get_streak_days correctly returns 0 when there is no history for the user.
    """
    # Using user_id 1 with an empty database
    result = get_streak_days(db_conn, user_id=1)

    # Should be 0 streak days
    assert result == 0
