from flask import Blueprint, request, jsonify
from app.db import get_db
import json
import random

arena_bp = Blueprint('arena', __name__)

@arena_bp.route('/bosses', methods=['GET'])
def get_bosses():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, boss_name, subject, total_hp, difficulty, description, image_url FROM boss_battles')
    bosses = cursor.fetchall()
    conn.close()

    boss_list = []
    for boss in bosses:
        boss_list.append({
            'id': boss[0],
            'boss_name': boss[1],
            'subject': boss[2],
            'total_hp': boss[3],
            'difficulty': boss[4],
            'description': boss[5],
            'image_url': boss[6]
        })
    
    return jsonify(boss_list)

@arena_bp.route('/fight/start', methods=['POST'])
def start_fight():
    data = request.json
    boss_id = data.get('boss_id')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get boss details
    cursor.execute('SELECT * FROM boss_battles WHERE id = ?', (boss_id,))
    boss = cursor.fetchone()
    
    if not boss:
        return jsonify({'error': 'Boss not found'}), 404
        
    # Fetch random questions for the boss's subject
    # Assuming we have a questions table or similar. For now, we'll mock some questions if none exist.
    # Ideally, we should link this to the PYQ database.
    
    subject = boss[2]
    # Mock questions for now to ensure gameplay works immediately
    questions = [
        {
            'id': 1,
            'text': f'What is a key concept in {subject}?',
            'options': ['Option A', 'Option B', 'Option C', 'Option D'],
            'correct_index': 0
        },
        {
            'id': 2,
            'text': f'Who is a famous figure in {subject}?',
            'options': ['Person X', 'Person Y', 'Person Z', 'Person W'],
            'correct_index': 1
        },
        # Add more mock questions or fetch from DB
    ]
    
    # In a real scenario, we'd fetch from a 'questions' table:
    # cursor.execute('SELECT id, question_text, option_a, option_b, option_c, option_d, correct_option FROM questions WHERE subject = ? ORDER BY RANDOM() LIMIT ?', (subject, boss[3]))
    
    return jsonify({
        'boss': {
            'id': boss[0],
            'name': boss[1],
            'hp': boss[3],
            'image': boss[6]
        },
        'player_hp': 3, # Player has 3 lives
        'questions': questions
    })

@arena_bp.route('/fight/end', methods=['POST'])
def end_fight():
    data = request.json
    user_id = data.get('user_id', 1) # Default user ID
    boss_id = data.get('boss_id')
    damage_dealt = data.get('damage_dealt')
    damage_taken = data.get('damage_taken')
    outcome = data.get('outcome') # VICTORY or DEFEAT
    
    loot = []
    if outcome == 'VICTORY':
        loot.append('XP +100')
        if damage_taken == 0:
            loot.append('Flawless Victory Badge')
            
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO battle_history (user_id, boss_id, damage_dealt, damage_taken, outcome, loot_earned)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, boss_id, damage_dealt, damage_taken, outcome, json.dumps(loot)))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Battle recorded', 'loot': loot})
