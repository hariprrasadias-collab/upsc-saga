from flask import Blueprint, request, jsonify
from app.db import get_db
from app.services.game_engine import calculate_and_apply_rewards

bp = Blueprint('battles', __name__, url_prefix='/api/battles')

@bp.route('', methods=['GET', 'POST'])
def handle_battles():
    user_id = 1
    conn = get_db()
    
    if request.method == 'GET':
        battles = conn.execute('SELECT * FROM mock_tests WHERE user_id=? ORDER BY date_fought DESC', (user_id,)).fetchall()
        return jsonify([dict(b) for b in battles])
        
    elif request.method == 'POST':
        data = request.get_json()
        boss_name = data.get('boss_name')
        subject = data.get('subject')
        # Logic: Win if Score >= Cutoff
        is_victory = 1 if float(data['my_score']) >= int(data['cutoff_marks']) else 0
        
        conn.execute('''
            INSERT INTO mock_tests (user_id, boss_name, subject, total_marks, cutoff_marks, my_score, is_victory)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, boss_name, subject, data['total_marks'], data['cutoff_marks'], data['my_score'], is_victory))
        conn.commit()
        
        # --- USE THE GAME ENGINE ---
        if is_victory:
            # BIG REWARD: 500 XP, 300 Hacksilver
            rewards = calculate_and_apply_rewards(user_id, 500, 300, [subject.lower()])
        else:
            # PITY REWARD: 50 XP, 10 Hacksilver
            rewards = calculate_and_apply_rewards(user_id, 50, 10, [subject.lower()])
            
        rewards['is_victory'] = bool(is_victory)
        return jsonify(rewards), 201
