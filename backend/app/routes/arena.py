from flask import Blueprint, request, jsonify
from app.db import get_db
import random
import json
from app.services.xp_service import award_xp

arena_bp = Blueprint('arena', __name__)

# Mock Questions Database (In a real app, this would be in the DB)
MOCK_QUESTIONS = [
    {
        "id": 1,
        "text": "Which Article of the Constitution deals with the Uniform Civil Code?",
        "options": ["Article 44", "Article 45", "Article 40", "Article 51A"],
        "correct_index": 0
    },
    {
        "id": 2,
        "text": "Who was the Viceroy of India during the Partition of Bengal (1905)?",
        "options": ["Lord Curzon", "Lord Minto", "Lord Hardinge", "Lord Chelmsford"],
        "correct_index": 0
    },
    {
        "id": 3,
        "text": "The 'Ring of Fire' is associated with which ocean?",
        "options": ["Pacific Ocean", "Atlantic Ocean", "Indian Ocean", "Arctic Ocean"],
        "correct_index": 0
    },
    {
        "id": 4,
        "text": "Which Five Year Plan adopted 'Garibi Hatao' as its goal?",
        "options": ["Fourth Plan", "Fifth Plan", "Sixth Plan", "Seventh Plan"],
        "correct_index": 1
    },
    {
        "id": 5,
        "text": "The term 'Golden Revolution' is related to?",
        "options": ["Horticulture and Honey", "Oilseeds", "Jute", "Eggs"],
        "correct_index": 0
    }
]

BOSS_STATS = {
    1: {"name": "Vision Test 1", "hp": 5, "xp_reward": 100, "loot": ["Ancient Scroll", "Health Potion"]},
    2: {"name": "Mains Answer Writing", "hp": 8, "xp_reward": 200, "loot": ["Golden Quill"]},
    3: {"name": "CSAT Demon", "hp": 10, "xp_reward": 500, "loot": ["Calculator of Doom"]}
}

@arena_bp.route('/api/arena/fight/start', methods=['POST'])
def start_fight():
    try:
        data = request.json
        boss_id = data.get('boss_id', 1)
        
        # Get Boss Stats
        boss = BOSS_STATS.get(boss_id, BOSS_STATS[1])
        
        # Select random questions
        questions = random.sample(MOCK_QUESTIONS, min(len(MOCK_QUESTIONS), boss['hp'] + 2))
        
        return jsonify({
            "boss": {
                "id": boss_id,
                "name": boss['name'],
                "hp": boss['hp']
            },
            "player_hp": 3,
            "questions": questions
        })
        
    except Exception as e:
        print(f"Error starting fight: {e}")
        return jsonify({'error': str(e)}), 500

@arena_bp.route('/api/arena/fight/end', methods=['POST'])
def end_fight():
    try:
        data = request.json
        boss_id = data.get('boss_id')
        outcome = data.get('outcome') # 'VICTORY' or 'DEFEAT'
        damage_dealt = data.get('damage_dealt', 0)
        
        user_id = 1 # TODO: Session
        
        # Calculate Rewards
        xp_earned = 0
        loot_earned = []
        
        if outcome == 'VICTORY':
            boss = BOSS_STATS.get(boss_id, BOSS_STATS[1])
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
            BOSS_STATS.get(boss_id, {}).get('name', 'Unknown Boss'),
            'General Studies', # Default subject
            BOSS_STATS.get(boss_id, {}).get('hp', 10), # Total marks = Boss HP
            BOSS_STATS.get(boss_id, {}).get('hp', 10), # Cutoff = Boss HP (must kill)
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
