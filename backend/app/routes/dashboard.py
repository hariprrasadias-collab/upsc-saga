from flask import Blueprint, jsonify
from app.db import get_db
from app import cache
import datetime

bp = Blueprint('dashboard', __name__, url_prefix='/api')

def get_today_date_str():
    return datetime.date.today().isoformat()

@bp.route('/dashboard-data')
@cache.cached(timeout=60, query_string=True) # Cache for 1 minute
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
    
    # Anki Check
    try:
        from anki_client import fetch_due_cards
        anki = fetch_due_cards()
    except:
        anki = 0

    return jsonify({
        "stats": dict(user),
        "tasks": [dict(t) for t in tasks],
        "anki_due": anki
    })
