from flask import Blueprint, request, jsonify
from app.db import get_db
from app.services.game_engine import calculate_and_apply_rewards
from datetime import datetime

bp = Blueprint('battles', __name__, url_prefix='/api/battles')

@bp.route('', methods=['GET'])
def get_battles():
    """Get all battles (Mock Tests + Answer Writing)"""
    user_id = 1
    conn = get_db()
    
    battles = []
    
    # 1. Fetch Mock Test Attempts
    test_attempts = conn.execute('''
        SELECT 
            at.id, 
            mt.title as boss_name, 
            mt.subject, 
            mt.total_marks, 
            at.score as my_score, 
            at.percentage,
            at.submitted_at as date_fought,
            'mock_test' as type
        FROM test_attempts at
        JOIN mock_tests mt ON at.test_id = mt.id
        WHERE at.user_id = ? AND at.status = 'completed'
    ''', (user_id,)).fetchall()
    
    for t in test_attempts:
        # Determine victory (e.g., > 40% is a pass/victory for now, or use cutoff if we had it)
        is_victory = t['percentage'] >= 40 
        battles.append({
            'id': f"mt_{t['id']}",
            'boss_name': t['boss_name'],
            'subject': t['subject'] or 'General Studies',
            'total_marks': t['total_marks'],
            'cutoff_marks': t['total_marks'] * 0.4, # Approx 40% cutoff
            'my_score': round(t['my_score'], 2),
            'is_victory': is_victory,
            'date_fought': t['date_fought'],
            'type': 'Mock Test'
        })

    # 2. Fetch Answer Writing Submissions
    answers = conn.execute('''
        SELECT 
            ua.id, 
            p.question as boss_name, 
            p.subject, 
            ae.overall_score,
            ua.submitted_at as date_fought
        FROM user_answers ua
        JOIN answer_writing_prompts p ON ua.prompt_id = p.id
        LEFT JOIN answer_evaluations ae ON ua.id = ae.answer_id
        WHERE ua.user_id = ?
    ''', (user_id,)).fetchall()
    
    for a in answers:
        # Answer writing is out of 10 usually (or 15/20). Let's assume 10 for normalization or use raw.
        # Our evaluator returns score out of 10.
        score = a['overall_score'] or 0
        is_victory = score >= 4.0 # 4/10 is decent
        
        battles.append({
            'id': f"aw_{a['id']}",
            'boss_name': f"Mini-Boss: {a['boss_name'][:30]}...", # Truncate long questions
            'subject': a['subject'] or 'General Studies',
            'total_marks': 10,
            'cutoff_marks': 4.0,
            'my_score': round(score, 1),
            'is_victory': is_victory,
            'date_fought': a['date_fought'],
            'type': 'Answer Writing'
        })
        
    # Sort by date descending
    battles.sort(key=lambda x: x['date_fought'] or '', reverse=True)
    
    return jsonify(battles)

@bp.route('/manual', methods=['POST'])
def manual_battle():
    """Handle manual external test entry"""
    user_id = 1
    conn = get_db()
    data = request.get_json()
    
    boss_name = data.get('boss_name')
    subject = data.get('subject')
    total_marks = float(data.get('total_marks', 200))
    cutoff_marks = float(data.get('cutoff_marks', 80))
    my_score = float(data.get('my_score', 0))
    
    # Create a "Manual" mock test entry if needed, or just insert into attempts linked to a generic "External" test.
    # For simplicity, let's create a new mock_test record for this external test so it fits our schema
    
    cursor = conn.execute('''
        INSERT INTO mock_tests (title, description, test_type, subject, total_questions, duration_minutes, total_marks, difficulty)
        VALUES (?, 'External Manual Entry', 'manual', ?, 100, 120, ?, 'Medium')
    ''', (boss_name, subject, total_marks))
    test_id = cursor.lastrowid
    
    # Create attempt
    percentage = (my_score / total_marks) * 100 if total_marks > 0 else 0
    
    conn.execute('''
        INSERT INTO test_attempts (user_id, test_id, score, percentage, status, submitted_at, total_correct, total_attempted)
        VALUES (?, ?, ?, ?, 'completed', CURRENT_TIMESTAMP, 0, 0)
    ''', (user_id, test_id, my_score, percentage))
    
    conn.commit()
    
    # Calculate Rewards
    is_victory = my_score >= cutoff_marks
    if is_victory:
        rewards = calculate_and_apply_rewards(user_id, 500, 300, [subject.lower()])
    else:
        rewards = calculate_and_apply_rewards(user_id, 50, 10, [subject.lower()])
        
    rewards['is_victory'] = is_victory
    return jsonify(rewards)

