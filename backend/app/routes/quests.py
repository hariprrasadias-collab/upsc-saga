from app.utils.session import get_current_user_id
from flask import Blueprint, request, jsonify
from app.db import get_db
from app.services.game_engine import calculate_and_apply_rewards

bp = Blueprint('quests', __name__, url_prefix='/api/quests')

@bp.route('', methods=['GET', 'POST'])
def handle_quests():
    user_id = get_current_user_id()
    conn = get_db()
    if request.method == 'GET':
        quests = conn.execute('SELECT * FROM tasks WHERE user_id=? AND is_quest=1 ORDER BY isCompleted ASC', (user_id,)).fetchall()
        
        # If no quests, generate daily quests
        if not quests:
            try:
                from app.services.quest_service import quest_service
                new_quests = quest_service.generate_daily_quests(user_id)
                for q in new_quests:
                    conn.execute('INSERT INTO tasks (user_id, title, xp_reward, associated_stat, isCompleted, is_quest) VALUES (?, ?, ?, ?, 0, 1)',
                                 (user_id, q['title'], q['xp_reward'], q['type']))
                conn.commit()
                # Fetch again
                quests = conn.execute('SELECT * FROM tasks WHERE user_id=? AND is_quest=1 ORDER BY isCompleted ASC', (user_id,)).fetchall()
            except Exception as e:
                print(f"Failed to generate quests: {e}")

        return jsonify([dict(q) for q in quests])
    elif request.method == 'POST':
        data = request.get_json()
        conn.execute('INSERT INTO tasks (user_id, title, xp_reward, associated_stat, due_date, isCompleted, is_quest) VALUES (?, ?, ?, ?, ?, 0, 1)',
                     (user_id, data['title'], data['xp_reward'], data.get('associated_stat'), data.get('due_date')))
        conn.commit()
        return jsonify({"message": "Quest created"}), 201

@bp.route('/<int:quest_id>/complete', methods=['POST'])
def complete_quest(quest_id):
    user_id = get_current_user_id()
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
