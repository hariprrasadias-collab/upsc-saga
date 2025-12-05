
from app.db import get_db

def init_indexes():
    """Create performance indexes for frequent queries"""
    conn = get_db()
    cursor = conn.cursor()

    indexes = [
        # Dashboard: Tasks due today
        'CREATE INDEX IF NOT EXISTS idx_tasks_user_due ON tasks (user_id, due_date)',

        # Analytics: Activity between dates
        'CREATE INDEX IF NOT EXISTS idx_test_attempts_user_date ON test_attempts (user_id, submitted_at)',
        'CREATE INDEX IF NOT EXISTS idx_user_answers_user_date ON user_answers (user_id, submitted_at)',
        'CREATE INDEX IF NOT EXISTS idx_review_sessions_user_date ON review_sessions (user_id, reviewed_at)',
        'CREATE INDEX IF NOT EXISTS idx_pomodoro_sessions_user_date ON pomodoro_sessions (user_id, timestamp)'
    ]

    print("Optimization: Checking indexes...")
    for idx_sql in indexes:
        try:
            cursor.execute(idx_sql)
        except Exception as e:
            print(f"Warning creating index: {e}")

    conn.commit()
