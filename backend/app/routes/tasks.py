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
        
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        conn.execute('INSERT INTO tasks (user_id, title, xp_reward, associated_stat, due_date, start_time, end_time, isCompleted, is_quest) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0)',
                     (user_id, data['title'], data['xp_reward'], data.get('associated_stat'), data['due_date'], start_time, end_time))
        conn.commit()
        new_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        
        # Sync to Google Calendar
        if start_time and end_time:
            try:
                from app.routes.warmap import create_google_calendar_event
                
                # Construct description
                description = f"XP Reward: {data['xp_reward']}\n"
                if data.get('associated_stat'):
                    description += f"Associated Stat: {data.get('associated_stat')}\n"
                
                # Combine date and time for ISO format if needed, or assume frontend sends full ISO
                # Frontend sends 'YYYY-MM-DD' for date and 'HH:MM' for time.
                # We need to construct full ISO strings for Google Calendar
                
                date_part = data['due_date']
                start_iso = f"{date_part}T{start_time}:00"
                end_iso = f"{date_part}T{end_time}:00"
                
                create_google_calendar_event(
                    title=data['title'],
                    start_time=start_iso,
                    end_time=end_iso,
                    description=description
                )
            except Exception as e:
                print(f"Failed to sync with Google Calendar: {e}")
                
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

@bp.route('/log-study', methods=['POST'])
def log_study_session():
    """Log study hours and award XP"""
    try:
        data = request.get_json()
        user_id = 1
        minutes = data.get('minutes', 0)
        
        if minutes <= 0:
            return jsonify({'error': 'Invalid duration'}), 400
            
        # Calculate XP: 10 XP per 30 mins -> 20 XP per hour
        xp_earned = int((minutes / 60) * 20)
        if xp_earned < 1: xp_earned = 1
        
        # Use Game Engine to apply rewards (handles level up, stats, etc.)
        rewards = calculate_and_apply_rewards(user_id, xp_earned, 0, ['study', 'focus'])
        
        conn = get_db()
        # Log activity
        conn.execute('''
            INSERT INTO activity_log (user_id, activity_type, description, xp_awarded)
            VALUES (?, 'study_session', ?, ?)
        ''', (user_id, f"Studied for {minutes} minutes", xp_earned))
        
        conn.commit()
        
        return jsonify({'success': True, 'xp_earned': xp_earned, 'rewards': rewards})
        
        conn.commit()
        
        return jsonify({'success': True, 'xp_earned': xp_earned})
    except Exception as e:
        print(f"Error logging study: {e}")
        return jsonify({'error': str(e)}), 500
