from flask import Blueprint, request, jsonify
from app.db import get_db
import random
import json
from app.services.xp_service import award_xp

arena_bp = Blueprint('arena', __name__)

def get_boss_stats(boss_type, boss_id):
    """Generate boss stats dynamically based on DB content"""
    conn = get_db()
    
    if boss_type == 'YEAR':
        # Boss ID is the Year (e.g., 2024)
        count = conn.execute("SELECT COUNT(*) FROM pyq_questions WHERE year = ?", (boss_id,)).fetchone()[0]
        name = f"The {boss_id} Titan"
        loot = ["Time Capsule", "Ancient Scroll"]
    elif boss_type == 'SUBJECT':
        # Boss ID is the Subject Name (e.g., Geography)
        count = conn.execute("SELECT COUNT(*) FROM pyq_questions WHERE subject = ?", (boss_id,)).fetchone()[0]
        name = f"The {boss_id} Golem"
        loot = ["Subject Mastery Token", "Skill Point"]
    else:
        # Default/Random Boss
        count = 10
        name = "Training Dummy"
        loot = ["Wooden Sword"]
        
    # Scale HP based on question count (max 20 for a session)
    hp = min(count, 20) 
    xp_reward = hp * 50 # 50 XP per question
    
    return {
        "id": boss_id,
        "type": boss_type,
        "name": name,
        "hp": hp,
        "max_hp": count, # Total available questions
        "xp_reward": xp_reward,
        "loot": loot
    }

@arena_bp.route('/bosses', methods=['GET'])
def get_available_bosses():
    """Get list of available bosses (Years and Subjects)"""
    conn = get_db()
    
    # Year Bosses
    years = conn.execute("SELECT DISTINCT year FROM pyq_questions ORDER BY year DESC").fetchall()
    year_bosses = [get_boss_stats('YEAR', row['year']) for row in years]
    
    # Subject Bosses
    subjects = conn.execute("SELECT DISTINCT subject FROM pyq_questions ORDER BY subject").fetchall()
    subject_bosses = [get_boss_stats('SUBJECT', row['subject']) for row in subjects]
    
    return jsonify({
        "year_bosses": year_bosses,
        "subject_bosses": subject_bosses
    })

@arena_bp.route('/fight/start', methods=['POST'])
def start_fight():
    try:
        data = request.json
        boss_type = data.get('boss_type', 'YEAR')
        boss_id = data.get('boss_id', 2024)
        
        # Get Boss Stats
        boss = get_boss_stats(boss_type, boss_id)
        
        conn = get_db()
        questions = []
        
        if boss_type == 'YEAR':
            rows = conn.execute("SELECT * FROM pyq_questions WHERE year = ? ORDER BY RANDOM() LIMIT ?", (boss_id, boss['hp'])).fetchall()
        elif boss_type == 'SUBJECT':
            rows = conn.execute("SELECT * FROM pyq_questions WHERE subject = ? ORDER BY RANDOM() LIMIT ?", (boss_id, boss['hp'])).fetchall()
            
        # Format questions for frontend
        for row in rows:
            questions.append({
                "id": row['id'],
                "text": row['question_text'],
                "options": [row['option_a'], row['option_b'], row['option_c'], row['option_d']],
                "correct_option": row['correct_option'], # Send correct option (A/B/C/D)
                "explanation": row['explanation']
            })
        
        return jsonify({
            "boss": boss,
            "player_hp": 3, # 3 Strikes rule
            "questions": questions
        })
        
    except Exception as e:
        print(f"Error starting fight: {e}")
        return jsonify({'error': str(e)}), 500

@arena_bp.route('/fight/end', methods=['POST'])
def end_fight():
    try:
        data = request.json
        boss_type = data.get('boss_type')
        boss_id = data.get('boss_id')
        outcome = data.get('outcome') # 'VICTORY' or 'DEFEAT'
        damage_dealt = data.get('damage_dealt', 0)
        
        user_id = 1 # TODO: Session
        
        boss = get_boss_stats(boss_type, boss_id)
        
        # Calculate Rewards
        xp_earned = 0
        loot_earned = []
        
        if outcome == 'VICTORY':
            xp_earned = boss['xp_reward']
            loot_earned = boss['loot']
            
            # Award XP
            award_xp(user_id, xp_earned, 0)
        
        # Record Battle History
        conn = get_db()
        conn.execute('''
            INSERT INTO battles (user_id, boss_name, subject, total_marks, cutoff_marks, my_score, is_victory, type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, 
            boss['name'],
            str(boss_id) if boss_type == 'SUBJECT' else 'General Studies',
            boss['hp'], # Total marks = Boss HP (Questions)
            boss['hp'], # Cutoff = Boss HP (must kill)
            damage_dealt,
            1 if outcome == 'VICTORY' else 0,
            'Boss Fight'
        ))
        conn.commit()
        
        return jsonify({
            "xp_earned": xp_earned,
            "loot": loot_earned,
            "message": "Battle recorded"
        })
        
    except Exception as e:
        print(f"Error ending fight: {e}")
        return jsonify({'error': str(e)}), 500
