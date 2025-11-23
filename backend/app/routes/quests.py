from flask import Blueprint, request, jsonify
from app.db import get_db
from app.services.game_engine import calculate_and_apply_rewards

bp = Blueprint('quests', __name__, url_prefix='/api/quests')

@bp.route('', methods=['GET', 'POST'])
def handle_quests():
    user_id = 1
    conn = get_db()
    if request.method == 'GET':
        quests = conn.execute('SELECT * FROM tasks WHERE user_id=? AND is_quest=1 ORDER BY isCompleted ASC', (user_id,)).fetchall()
        return jsonify([dict(q) for q in quests])
    elif request.method == 'POST':
        data = request.get_json()
        conn.execute('INSERT INTO tasks (user_id, title, xp_reward, associated_stat, due_date, isCompleted, is_quest) VALUES (?, ?, ?, ?, ?, 0, 1)',
                     (user_id, data['title'], data['xp_reward'], data.get('associated_stat'), data.get('due_date')))
        conn.commit()
        return jsonify({"message": "Quest created"}), 201

@bp.route('/<int:quest_id>/complete', methods=['POST'])
def complete_quest(quest_id):
    user_id = 1
    conn = get_db()
    quest = conn.execute('SELECT * FROM tasks WHERE id = ?', (quest_id,)).fetchone()
    
    if not quest or quest['isCompleted']:
        return jsonify({"message": "Done"}), 400

    conn.execute('UPDATE tasks SET isCompleted = 1 WHERE id = ?', (quest_id,))
    conn.commit()

    # --- USE THE GAME ENGINE ---
    # Quest: Base Hacksilver = 100 (Much higher than tasks)
    tags = quest['title'].lower().split()
    rewards = calculate_and_apply_rewards(user_id, quest['xp_reward'], 100, tags)
    
    return jsonify(rewards), 200
