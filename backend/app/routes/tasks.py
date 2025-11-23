from flask import Blueprint, request, jsonify
from app.db import get_db
from app.services.game_engine import calculate_and_apply_rewards

bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')

@bp.route('', methods=['GET', 'POST'])
def handle_tasks():
    user_id = 1
    conn = get_db()

    if request.method == 'GET':
        date_str = request.args.get('date')
        if date_str:
            tasks = conn.execute('SELECT * FROM tasks WHERE user_id=? AND due_date=? AND is_quest=0', (user_id, date_str)).fetchall()
        else:
            tasks = conn.execute('SELECT * FROM tasks WHERE user_id=? AND is_quest=0', (user_id,)).fetchall()
        return jsonify([dict(t) for t in tasks])

    elif request.method == 'POST':
        data = request.get_json()
        conn.execute('INSERT INTO tasks (user_id, title, xp_reward, associated_stat, due_date, isCompleted, is_quest) VALUES (?, ?, ?, ?, ?, 0, 0)',
                     (user_id, data['title'], data['xp_reward'], data.get('associated_stat'), data['due_date']))
        conn.commit()
        new_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        return jsonify({"id": new_id}), 201

@bp.route('/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    user_id = 1
    conn = get_db()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    
    if not task or task['isCompleted']:
        return jsonify({"message": "Already done or invalid"}), 400
        
    # Mark done
    conn.execute('UPDATE tasks SET isCompleted = 1 WHERE id = ?', (task_id,))
    conn.commit()
    
    # --- USE THE GAME ENGINE ---
    # Standard Task: Base Hacksilver = 15
    tags = task['title'].lower().split() # Simple tag extraction
    rewards = calculate_and_apply_rewards(user_id, task['xp_reward'], 15, tags)
    
    return jsonify(rewards), 200
