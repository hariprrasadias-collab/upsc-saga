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

    start_date = (today - datetime.timedelta(days=6)).isoformat()
    end_date = today.isoformat()

    # Note: ideally we track 'completed_at' timestamp, but using due_date for now is a safe fallback
    xp_rows = conn.execute('''
        SELECT due_date, SUM(xp_reward) as total_xp FROM tasks
        WHERE user_id = ? AND due_date >= ? AND due_date <= ? AND isCompleted = 1
        GROUP BY due_date
    ''', (user_id, start_date, end_date)).fetchall()

    # Handle tuple vs dict-like row depending on connection type
    xp_map = {}
    for row in xp_rows:
        try:
            val = row['total_xp']
            key = row['due_date']
        except (TypeError, IndexError):
            val = row[1]
            key = row[0]
        xp_map[key] = val

    xp_history = []
    for i in range(6, -1, -1):
        date_val = today - datetime.timedelta(days=i)
        date_str = date_val.isoformat()
        xp_history.append({
            "date": date_val.strftime('%d %b'),  # e.g. "22 Nov"
            "xp": xp_map.get(date_str, 0)
        })

    return jsonify({
        "radar_data": [
            {"subject": "Strength (GS-I)",
             "A": stat_map['strength_stat'], "fullMark": 20},
            {"subject": "Runic (GS-II)",
             "A": stat_map['runic_stat'], "fullMark": 20},
            {"subject": "Vitality (GS-III)",
             "A": stat_map['vitality_stat'], "fullMark": 20},
            {"subject": "Luck (GS-IV)",
             "A": stat_map['luck_stat'], "fullMark": 20},
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
        # Get all years and subjects
        years = conn.execute(
            "SELECT DISTINCT year FROM pyq_questions ORDER BY year").fetchall()
        subjects = conn.execute(
            "SELECT DISTINCT subject FROM pyq_questions ORDER BY subject").fetchall()

        all_counts = conn.execute('''
            SELECT year, subject, COUNT(*) as count
            FROM pyq_questions
            GROUP BY year, subject
        ''').fetchall()

        count_map = {}
        for row in all_counts:
            try:
                y = row['year']
                s = row['subject']
                c = row['count']
            except (TypeError, IndexError):
                y = row[0]
                s = row[1]
                c = row[2]

            if y not in count_map:
                count_map[y] = {}
            count_map[y][s] = c

        data = []
        for year_row in years:
            try:
                year = year_row['year']
            except (TypeError, IndexError):
                year = year_row[0]

            year_data = {"year": year}

            for sub_row in subjects:
                try:
                    subject = sub_row['subject']
                except (TypeError, IndexError):
                    subject = sub_row[0]

                year_data[subject] = count_map.get(year, {}).get(subject, 0)

            data.append(year_data)

        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
