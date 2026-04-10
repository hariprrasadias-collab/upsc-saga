from collections import defaultdict
from app.utils.session import get_current_user_id
from flask import Blueprint, jsonify
from app.db import get_db
import datetime

bp = Blueprint('seer', __name__, url_prefix='/api/seer')


@bp.route('', methods=['GET'])
def consult_the_seer():
    user_id = get_current_user_id()
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
        'strength_stat': 0,  # GS-I
        'runic_stat': 0,    # GS-II
        'vitality_stat': 0,  # GS-III
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
            "date": date_val.strftime('%d %b'),  # e.g. "22 Nov"
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


@bp.route('/weightage', methods=['GET'])
def get_subject_weightage():
    """Get subject-wise question distribution for Pie Chart"""
    conn = get_db()
    try:
        rows = conn.execute('''
            SELECT subject, COUNT(*) as count
            FROM pyq_questions
            GROUP BY subject
            ORDER BY count DESC
        ''').fetchall()

        return jsonify([dict(row) for row in rows])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/trends', methods=['GET'])
def get_year_trends():
    """Get year-wise subject distribution for Stacked Bar Chart"""
    conn = get_db()
    try:
        # Fetch all counts in a single query to avoid N+1 bottleneck
        counts = conn.execute('''
            SELECT year, subject, COUNT(*) as count
            FROM pyq_questions
            GROUP BY year, subject
        ''').fetchall()

        year_subject_counts = defaultdict(dict)
        unique_years = set()
        unique_subjects = set()

        for row in counts:
            try:
                year = row['year']
                subject = row['subject']
                count = row['count']
            except (TypeError, IndexError):
                year = row[0]
                subject = row[1]
                count = row[2]

            year_subject_counts[year][subject] = count
            unique_years.add(year)
            unique_subjects.add(subject)

        data = []
        for year in sorted(unique_years):
            year_data = {"year": year}
            for subject in sorted(unique_subjects):
                year_data[subject] = year_subject_counts[year].get(subject, 0)
            data.append(year_data)

        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
