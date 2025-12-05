from app.db import get_db

def create_indexes():
    """Create indexes for performance optimization"""
    conn = get_db()

    # Indexes for study_tasks
    conn.execute('CREATE INDEX IF NOT EXISTS idx_study_tasks_plan_date ON study_tasks (plan_id, date)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_study_tasks_status ON study_tasks (status)')

    # Indexes for study_plans
    conn.execute('CREATE INDEX IF NOT EXISTS idx_study_plans_active ON study_plans (is_active)')

    conn.commit()
