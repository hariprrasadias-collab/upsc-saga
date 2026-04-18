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
        # ⚡ Bolt Optimization: Replaced N+1 query loop with a single grouped query
        # to fetch all year/subject distributions simultaneously. Local Python dictionary
        # grouping reduces database roundtrips from O(Years) to O(1).

        # Get all counts in one query
        counts = conn.execute('''
            SELECT year, subject, COUNT(*) as count
            FROM pyq_questions
            GROUP BY year, subject
            ORDER BY year
        ''').fetchall()

        # Aggregate data locally
        year_data_map = {}
        unique_subjects = set()

        for row in counts:
            year = row['year']
            subject = row['subject']
            count = row['count']

            unique_subjects.add(subject)

            if year not in year_data_map:
                year_data_map[year] = {"year": year}

            year_data_map[year][subject] = count

        # Ensure consistent subject ordering
        sorted_subjects = sorted(list(unique_subjects))

        # Build final data list and ensure all subjects have a value (default 0)
        data = []
        # Maintain order of years using the sorted property from the ORDER BY in query
        for year in sorted(year_data_map.keys()):
            year_dict = year_data_map[year]
            for subject in sorted_subjects:
                if subject not in year_dict:
                    year_dict[subject] = 0
            data.append(year_dict)

        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
