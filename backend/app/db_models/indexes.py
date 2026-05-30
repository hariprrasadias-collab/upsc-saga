
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
        'CREATE INDEX IF NOT EXISTS idx_review_sessions_flashcard_id_reviewed_at ON review_sessions (flashcard_id, reviewed_at DESC)',
        'CREATE INDEX IF NOT EXISTS idx_pomodoro_sessions_user_date ON pomodoro_sessions (user_id, timestamp)',

        # Study Tasks Optimization
        'CREATE INDEX IF NOT EXISTS idx_study_tasks_plan_date ON study_tasks (plan_id, date, start_time)',
        'CREATE INDEX IF NOT EXISTS idx_study_tasks_status ON study_tasks (plan_id, status)',
        'CREATE INDEX IF NOT EXISTS idx_study_tasks_subject ON study_tasks (plan_id, subject)',

        # PYQ Optimization
        'CREATE INDEX IF NOT EXISTS idx_pyq_subject_year ON pyq_questions (subject, year)',
        'CREATE INDEX IF NOT EXISTS idx_pyq_topic ON pyq_questions (topic)',

        # Activity Log History
        'CREATE INDEX IF NOT EXISTS idx_activity_log_user_time ON activity_log (user_id, timestamp)',

        # Study Sessions
        'CREATE INDEX IF NOT EXISTS idx_study_sessions_user_time ON study_sessions (user_id, start_time)',

        # Brain Action Log
        'CREATE INDEX IF NOT EXISTS idx_brain_action_log_user_time ON brain_action_log (user_id, executed_at)',

        # Syllabus Optimization (Bolt)
        'CREATE INDEX IF NOT EXISTS idx_syllabus_topics_sort ON syllabus_topics (paper, subject)',
        'CREATE INDEX IF NOT EXISTS idx_topic_revisions_topic_id ON topic_revisions (topic_id)',
        'CREATE INDEX IF NOT EXISTS idx_topic_revisions_next_date ON topic_revisions (next_revision_date)'
    ]

    print("Optimization: Checking indexes...")
    for idx_sql in indexes:
        try:
            cursor.execute(idx_sql)
        except Exception as e:
            # Silent fail for missing tables (e.g. during migration)
            print(f"Warning creating index: {e}")

    conn.commit()
