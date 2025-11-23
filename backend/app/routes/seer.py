from flask import Blueprint, jsonify
from app.db import get_db
import datetime

bp = Blueprint('seer', __name__, url_prefix='/api/seer')

@bp.route('', methods=['GET'])
def consult_the_seer():
    user_id = 1
    conn = get_db()
    
    # 1. STAT RADAR (Which subject is your strongest?)
    # We count completed tasks per associated_stat
    stats_query = '''
        SELECT associated_stat, COUNT(*) as count 
        FROM tasks 
        WHERE user_id = ? AND isCompleted = 1 AND associated_stat IS NOT NULL 
        GROUP BY associated_stat
    '''
    stat_rows = conn.execute(stats_query, (user_id,)).fetchall()
    
    # Default map
    stat_map = {
        'strength_stat': 0, # GS-I
        'runic_stat': 0,    # GS-II
        'vitality_stat': 0, # GS-III
        'luck_stat': 0      # GS-IV
    }
    for row in stat_rows:
        if row['associated_stat'] in stat_map:
            stat_map[row['associated_stat']] = row['count']

    # 2. XP HISTORY (Last 7 Days)
    # We look at tasks completed in the last 7 days
    today = datetime.date.today()
    xp_history = []
    
    for i in range(6, -1, -1):
        date_val = today - datetime.timedelta(days=i)
        date_str = date_val.isoformat()
        
        # Sum XP of tasks completed on this due_date (Approximation)
        # Note: ideally we track 'completed_at' timestamp, but using due_date for now is a safe fallback
        xp_sum = conn.execute('''
            SELECT SUM(xp_reward) FROM tasks 
            WHERE user_id = ? AND due_date = ? AND isCompleted = 1
        ''', (user_id, date_str)).fetchone()[0]
        
        xp_history.append({
            "date": date_val.strftime('%d %b'), # e.g. "22 Nov"
            "xp": xp_sum if xp_sum else 0
        })

    return jsonify({
        "radar_data": [
            {"subject": "Strength (GS-I)", "A": stat_map['strength_stat'], "fullMark": 20},
            {"subject": "Runic (GS-II)", "A": stat_map['runic_stat'], "fullMark": 20},
            {"subject": "Vitality (GS-III)", "A": stat_map['vitality_stat'], "fullMark": 20},
            {"subject": "Luck (GS-IV)", "A": stat_map['luck_stat'], "fullMark": 20},
        ],
        "xp_history": xp_history
    })
