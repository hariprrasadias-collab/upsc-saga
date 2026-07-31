from flask import Blueprint, jsonify
from app.db import get_db
# Remove global cache import, we will get it dynamically if needed or just remove it
from app import cache
from app.utils.session import get_current_user_id
import datetime

bp = Blueprint('dashboard', __name__, url_prefix='/api')

def get_today_date_str():
    return datetime.date.today().isoformat()

@bp.route('/dashboard-data')
def get_dashboard_data():
    try:
        user_id = get_current_user_id()
        conn = get_db()

        # Optimized User Query: Select only stats needed for UI
        user = conn.execute('''
            SELECT id, username, current_xp, level, max_xp, hacksilver,
                   strength_stat, runic_stat, vitality_stat, luck_stat
            FROM users WHERE id = ?
        ''', (user_id,)).fetchone()

        if not user:
            # Create default user if missing
            conn.execute('''
                INSERT INTO users (id, username, current_xp, level, max_xp, hacksilver, strength_stat, runic_stat, vitality_stat, luck_stat)
                VALUES (1, 'Hero', 0, 1, 100, 0, 5, 5, 5, 5)
            ''')
            conn.commit()
            user = conn.execute('SELECT * FROM users WHERE id = 1').fetchone()

        # Get Tasks due TODAY - Optimized Selection
        today = get_today_date_str()

        # Check if 'tasks' table exists, otherwise return empty
        try:
            tasks = conn.execute(
                'SELECT id, title, due_date, isCompleted, priority, xp_reward, associated_stat FROM tasks WHERE user_id = ? AND due_date = ? AND is_quest = 0 ORDER BY id DESC',
                (user_id, today)
            ).fetchall()
        except Exception as e:
            # Fallback for simpler schema or missing table
            print(f"Tasks Fetch Warning: {e}")
            tasks = []

        # Anki Check (optional)
        anki = 0
        try:
            # from anki_client import fetch_due_cards
            # anki = fetch_due_cards()
            pass
        except Exception as anki_err: # Replaced bare except
            pass

        return jsonify({
            "stats": dict(user),
            "tasks": [dict(t) for t in tasks],
            "anki_due": anki
        })
    except Exception as e:
        return jsonify({"error": str(e), "stats": None, "tasks": []}), 500
