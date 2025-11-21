# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime
# Removed: import os (if not used elsewhere) and init_db function
# Removed: the 'with app.app_context(): init_db()' block

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

DATABASE = 'upsc_saga.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # This allows access to columns by name
    return conn

# No init_db() function here anymore

# Helper function to get today's date in YYYY-MM-DD format (local time)
def get_today_date_str():
    return datetime.date.today().isoformat()

# --- API ENDPOINTS (Rest of your API endpoints remain unchanged) ---

@app.route('/api/dashboard-data')
def get_dashboard_data():
    user_id = 1 # Hardcoded for now, assume 'hero' user
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch user stats
    user = cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        conn.close()
        return jsonify({"error": "User not found"}), 404
    
    # Fetch today's tasks (rituals) - tasks that are NOT quests and due today
    today_date_str = get_today_date_str()
    tasks_raw = cursor.execute(
        'SELECT * FROM tasks WHERE user_id = ? AND due_date = ? AND is_quest = 0 ORDER BY id DESC',
        (user_id, today_date_str)
    ).fetchall()
    
    tasks = [dict(task) for task in tasks_raw]

    # Get real Anki due count from anki_client
    try:
        from anki_client import fetch_due_cards
        anki_due = fetch_due_cards()
    except Exception as e:
        print(f"Error fetching Anki due cards: {e}")
        anki_due = 0

    conn.close()
    return jsonify({
        "stats": dict(user),
        "tasks": tasks,
        "anki_due": anki_due
    })

@app.route('/api/tasks', methods=['GET', 'POST'])
def handle_tasks():
    user_id = 1 # Hardcoded for now

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        date_str = request.args.get('date')
        if not date_str:
            # If no date, return all non-quest tasks for the user (can be modified later)
            tasks_raw = cursor.execute(
                'SELECT * FROM tasks WHERE user_id = ? AND is_quest = 0 ORDER BY due_date DESC, id DESC',
                (user_id,)
            ).fetchall()
        else:
            tasks_raw = cursor.execute(
                'SELECT * FROM tasks WHERE user_id = ? AND due_date = ? AND is_quest = 0 ORDER BY id DESC',
                (user_id, date_str)
            ).fetchall()
        
        tasks = [dict(task) for task in tasks_raw]
        conn.close()
        return jsonify(tasks)

    elif request.method == 'POST':
        data = request.get_json()
        title = data.get('title')
        xp_reward = data.get('xp_reward')
        associated_stat = data.get('associated_stat')
        due_date = data.get('due_date')
        is_completed = data.get('isCompleted', 0) # Default to 0

        if not all([title, xp_reward, due_date]):
            conn.close()
            return jsonify({"error": "Missing required task fields"}), 400

        try:
            cursor.execute('''
                INSERT INTO tasks (user_id, title, xp_reward, associated_stat, due_date, isCompleted, is_quest)
                VALUES (?, ?, ?, ?, ?, ?, 0)
            ''', (user_id, title, xp_reward, associated_stat, due_date, is_completed))
            conn.commit()
            new_task_id = cursor.lastrowid
            conn.close()
            return jsonify({"message": "Task created successfully", "id": new_task_id}), 201
        except Exception as e:
            conn.close()
            return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    user_id = 1 # Hardcoded for now
    conn = get_db_connection()
    cursor = conn.cursor()

    task = cursor.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id)).fetchone()
    if not task:
        conn.close()
        return jsonify({"error": "Task not found"}), 404
    
    if task['isCompleted'] == 1:
        conn.close()
        return jsonify({"message": "Task already completed"}), 200 # Or 409 Conflict

    # Mark task as complete
    cursor.execute('UPDATE tasks SET isCompleted = 1 WHERE id = ?', (task_id,))
    
    # Update user XP and stats
    user = cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    current_xp = user['current_xp'] + task['xp_reward']
    level = user['level']
    max_xp = user['max_xp']

    # Level up logic
    while current_xp >= max_xp:
        level += 1
        current_xp -= max_xp
        max_xp = round(max_xp * 1.2) # XP requirement increases by 20%
    
    # Update associated stat if specified
    update_stat_query = ''
    update_stat_params = []
    if task['associated_stat']:
        # Ensure the stat name is valid to prevent SQL injection
        valid_stats = ['strength_stat', 'runic_stat', 'vitality_stat', 'luck_stat']
        if task['associated_stat'] in valid_stats:
            stat_value = user[task['associated_stat']] + 1
            update_stat_query = f", {task['associated_stat']} = ?"
            update_stat_params = [stat_value]

    cursor.execute(f'''
        UPDATE users SET current_xp = ?, level = ?, max_xp = ? {update_stat_query} WHERE id = ?
    ''', (current_xp, level, max_xp, *update_stat_params, user_id))

    conn.commit()
    conn.close()
    return jsonify({"message": "Task completed successfully", "new_xp": current_xp, "new_level": level}), 200

# --- QUESTS ENDPOINTS ---
@app.route('/api/quests', methods=['GET', 'POST'])
def handle_quests():
    user_id = 1 # Hardcoded for now

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        quests_raw = cursor.execute(
            'SELECT * FROM tasks WHERE user_id = ? AND is_quest = 1 ORDER BY due_date ASC, id DESC',
            (user_id,)
        ).fetchall()
        
        quests = [dict(quest) for quest in quests_raw]
        conn.close()
        return jsonify(quests)

    elif request.method == 'POST':
        data = request.get_json()
        title = data.get('title')
        xp_reward = data.get('xp_reward')
        associated_stat = data.get('associated_stat')
        due_date = data.get('due_date') # Can be null for quests
        is_completed = data.get('isCompleted', 0) # Default to 0

        if not all([title, xp_reward is not None]): # XP reward can be 0 but not missing
            conn.close()
            return jsonify({"error": "Missing required quest fields (title or xp_reward)"}), 400

        try:
            cursor.execute('''
                INSERT INTO tasks (user_id, title, xp_reward, associated_stat, due_date, isCompleted, is_quest)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            ''', (user_id, title, xp_reward, associated_stat, due_date, is_completed))
            conn.commit()
            new_quest_id = cursor.lastrowid
            conn.close()
            return jsonify({"message": "Quest created successfully", "id": new_quest_id}), 201
        except Exception as e:
            conn.close()
            return jsonify({"error": str(e)}), 500

@app.route('/api/quests/<int:quest_id>/complete', methods=['POST'])
def complete_quest(quest_id):
    user_id = 1 # Hardcoded for now
    conn = get_db_connection()
    cursor = conn.cursor()

    quest = cursor.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ? AND is_quest = 1', (quest_id, user_id)).fetchone()
    if not quest:
        conn.close()
        return jsonify({"error": "Quest not found"}), 404
    
    if quest['isCompleted'] == 1:
        conn.close()
        return jsonify({"message": "Quest already completed"}), 200 # Or 409 Conflict

    # Mark quest as complete
    cursor.execute('UPDATE tasks SET isCompleted = 1 WHERE id = ?', (quest_id,))
    
    # Update user XP and stats (same logic as tasks)
    user = cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    current_xp = user['current_xp'] + quest['xp_reward']
    level = user['level']
    max_xp = user['max_xp']

    while current_xp >= max_xp:
        level += 1
        current_xp -= max_xp
        max_xp = round(max_xp * 1.2) 
    
    update_stat_query = ''
    update_stat_params = []
    if quest['associated_stat']:
        valid_stats = ['strength_stat', 'runic_stat', 'vitality_stat', 'luck_stat']
        if quest['associated_stat'] in valid_stats:
            stat_value = user[quest['associated_stat']] + 1
            update_stat_query = f", {quest['associated_stat']} = ?"
            update_stat_params = [stat_value]

    cursor.execute(f'''
        UPDATE users SET current_xp = ?, level = ?, max_xp = ? {update_stat_query} WHERE id = ?
    ''', (current_xp, level, max_xp, *update_stat_params, user_id))

    conn.commit()
    conn.close()
    return jsonify({"message": "Quest completed successfully", "new_xp": current_xp, "new_level": level}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)