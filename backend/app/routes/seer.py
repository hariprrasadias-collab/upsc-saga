from app.utils.session import get_current_user_id
from flask import Blueprint, jsonify
from app.db import get_db
import datetime
from collections import defaultdict

bp = Blueprint('seer', __name__, url_prefix='/api/seer')


@bp.route('', methods=['GET'])
def consult_the_seer():
    user_id = get_current_user_id()
    conn = get_db()

    # 1. STAT RADAR (Which subject is your strongest?)
    stats_query = '''
        SELECT associated_stat, COUNT(*) as count
        FROM tasks
        WHERE user_id = ? AND isCompleted = 1 AND associated_stat IS NOT NULL
        GROUP BY associated_stat
    '''
    stat_rows = conn.execute(stats_query, (user_id,)).fetchall()

    stat_map = {
        'strength_stat': 0,  # GS-I
        'runic_stat': 0,     # GS-II
        'vitality_stat': 0,  # GS-III
        'luck_stat': 0       # GS-IV
    }
    for row in stat_rows:
        if row['associated_stat'] in stat_map:
            stat_map[row['associated_stat']] = row['count']

    # 2. XP HISTORY (Last 7 Days)
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=6)

    # ⚡ Bolt Optimization: Replaced N+1 loop with grouped query
    # Prevents hitting DB 7 times, improving latency
    q = '''
        SELECT due_date, SUM(xp_reward) as total_xp
        FROM tasks
        WHERE user_id=? AND isCompleted=1 AND due_date>=? AND due_date<=?
        GROUP BY due_date
    '''
    xp_sums = conn.execute(
        q,
        (user_id, start_date.isoformat(), today.isoformat())
    ).fetchall()

    xp_map = {row['due_date']: row['total_xp'] for row in xp_sums}

    xp_history = []
    for i in range(6, -1, -1):
        date_val = today - datetime.timedelta(days=i)
        date_str = date_val.isoformat()
        xp_history.append({
            "date": date_val.strftime('%d %b'),  # e.g. "22 Nov"
            "xp": xp_map.get(date_str, 0) or 0
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
        # ⚡ Bolt Optimization: Replace N+1 queries with single GROUP BY
        # Fetching counts once significantly reduces DB roundtrips
        counts = conn.execute('''
            SELECT year, subject, COUNT(*) as count
            FROM pyq_questions
            GROUP BY year, subject
            ORDER BY year
        ''').fetchall()

        year_data_map = defaultdict(dict)
        subjects = set()

        for row in counts:
            year = row['year']
            subject = row['subject']
            count = row['count']

            if year is not None and subject is not None:
                year_data_map[year][subject] = count
                subjects.add(subject)

        data = []
        for year in sorted(year_data_map.keys()):
            year_data = {"year": year}
            for subject in sorted(subjects):
                year_data[subject] = year_data_map[year].get(subject, 0)
            data.append(year_data)

        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
