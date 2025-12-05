from flask import Blueprint, jsonify
from app.db import get_db
import datetime

bp = Blueprint('dashboard', __name__, url_prefix='/api')

def get_today_date_str():
    return datetime.date.today().isoformat()

@bp.route('/dashboard-data')
def get_dashboard_data():
    user_id = 1
    conn = get_db()
    
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user: 
        return jsonify({"error": "User not found"}), 404
    
    # Get Tasks due TODAY
    today = get_today_date_str()
    tasks = conn.execute(
        'SELECT * FROM tasks WHERE user_id = ? AND due_date = ? AND is_quest = 0 ORDER BY id DESC',
        (user_id, today)
    ).fetchall()
    
    # --- Sidebar Stats ---
    # 1. Syllabus Progress
    syllabus_progress = conn.execute(
        "SELECT COUNT(*) as count FROM syllabus_topics WHERE status = 'Completed'"
    ).fetchone()['count']
    total_topics = conn.execute("SELECT COUNT(*) as count FROM syllabus_topics").fetchone()['count']
    syllabus_progress_percent = round((syllabus_progress / total_topics) * 100) if total_topics > 0 else 0

    # 2. Active Quests
    # Note: Assuming 'tasks' table has 'is_quest' and 'isCompleted'
    # This might need adjustment based on the actual schema for quests if it's different.
    active_quests = conn.execute(
        "SELECT COUNT(*) as count FROM tasks WHERE is_quest = 1 AND isCompleted = 0"
    ).fetchone()['count']

    # 3. Mock Tests in Progress
    active_mocks = conn.execute(
        "SELECT COUNT(*) as count FROM test_attempts WHERE status = 'in_progress' AND user_id = ?",
        (user_id,)
    ).fetchone()['count']

    # Anki Check
    try:
        from anki_client import fetch_due_cards
        anki_due = fetch_due_cards()
    except Exception:
        anki_due = 0 # Default to 0 if Anki isn't running

    # Compile all stats into a single object
    sidebar_stats = {
        "syllabus_progress": syllabus_progress_percent,
        "active_quests": active_quests,
        "active_mocks": active_mocks,
        "anki_due": anki_due
    }

    return jsonify({
        "stats": dict(user),
        "tasks": [dict(t) for t in tasks],
        "sidebar_stats": sidebar_stats
    })
