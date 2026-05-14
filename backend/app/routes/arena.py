from flask import Blueprint, request, jsonify, session
from app.db import get_db
import random
import json
from app.services.xp_service import award_xp

arena_bp = Blueprint('arena', __name__)

@arena_bp.route('/create-custom-boss', methods=['POST'])
def create_custom_boss():
    """Create a new custom boss from filters"""
    try:
        data = request.json
        name = data.get('name')
        filters = data.get('filters')
        
        if not name or not filters:
            return jsonify({'error': 'Name and filters are required'}), 400
            
        conn = get_db()
        cursor = conn.execute('INSERT INTO custom_bosses (name, filters) VALUES (?, ?)', 
                            (name, json.dumps(filters)))
        conn.commit()
        
        return jsonify({'success': True, 'id': cursor.lastrowid})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_boss_stats(boss_type, boss_id, precalculated_count=None):
    """Generate boss stats dynamically based on DB content"""
    conn = get_db()
    
    if boss_type == 'YEAR':
        # Boss ID is the Year (e.g., 2024)
        if precalculated_count is not None:
            count = precalculated_count
        else:
            count = conn.execute("SELECT COUNT(*) FROM pyq_questions WHERE year = ?", (boss_id,)).fetchone()[0]
        name = f"The {boss_id} Titan"
        loot = ["Time Capsule", "Ancient Scroll"]
    elif boss_type == 'SUBJECT':
        # Boss ID is the Subject Name (e.g., Geography)
        if precalculated_count is not None:
            count = precalculated_count
        else:
            count = conn.execute("SELECT COUNT(*) FROM pyq_questions WHERE subject = ?", (boss_id,)).fetchone()[0]
        name = f"The {boss_id} Golem"
        loot = ["Subject Mastery Token", "Skill Point"]
    elif boss_type == 'CUSTOM':
        # Boss ID is the Custom Boss ID
        boss_row = conn.execute("SELECT * FROM custom_bosses WHERE id = ?", (boss_id,)).fetchone()
        if not boss_row:
            raise ValueError("Custom Boss not found")
            
        filters = json.loads(boss_row['filters'])
        name = boss_row['name']
        loot = ["Custom Reward", "Glory"]
        
        # Calculate count based on filters
        if precalculated_count is not None:
            count = precalculated_count
        else:
            query = "SELECT COUNT(*) FROM pyq_questions WHERE 1=1"
            params = []
            if filters.get('year'):
                query += " AND year = ?"
                params.append(filters['year'])
            if filters.get('subject'):
                query += " AND subject = ?"
                params.append(filters['subject'])
            if filters.get('search'):
                query += " AND (question_text LIKE ? OR topic LIKE ?)"
                term = f"%{filters['search']}%"
                params.extend([term, term])

            count = conn.execute(query, params).fetchone()[0]
    else:
        # Default/Random Boss
        count = precalculated_count if precalculated_count is not None else 10
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
    """Get list of available bosses (Years, Subjects, and Custom)"""
    conn = get_db()
    
    # Bolt Optimization: Bulk fetch stats using GROUP BY to avoid N+1 queries

    # Year Bosses
    year_stats = conn.execute("SELECT year, COUNT(*) as count FROM pyq_questions GROUP BY year ORDER BY year DESC").fetchall()
    year_bosses = [get_boss_stats('YEAR', row['year'], precalculated_count=row['count']) for row in year_stats]
    
    # Subject Bosses
    subject_stats = conn.execute("SELECT subject, COUNT(*) as count FROM pyq_questions GROUP BY subject ORDER BY subject").fetchall()
    subject_bosses = [get_boss_stats('SUBJECT', row['subject'], precalculated_count=row['count']) for row in subject_stats]
    
    # Custom Bosses (These require parsing filters, keeping iterative for now since there are few)
    custom = conn.execute("SELECT id FROM custom_bosses WHERE is_active = 1 ORDER BY created_at DESC").fetchall()
    custom_bosses = []
    for row in custom:
        try:
            custom_bosses.append(get_boss_stats('CUSTOM', row['id']))
        except Exception:
            continue
    
    return jsonify({
        "year_bosses": year_bosses,
        "subject_bosses": subject_bosses,
        "custom_bosses": custom_bosses
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
        elif boss_type == 'CUSTOM':
            # Fetch filters again
            boss_row = conn.execute("SELECT * FROM custom_bosses WHERE id = ?", (boss_id,)).fetchone()
            filters = json.loads(boss_row['filters'])
            
            query = "SELECT * FROM pyq_questions WHERE 1=1"
            params = []
            if filters.get('year'):
                query += " AND year = ?"
                params.append(filters['year'])
            if filters.get('subject'):
                query += " AND subject = ?"
                params.append(filters['subject'])
            if filters.get('search'):
                query += " AND (question_text LIKE ? OR topic LIKE ?)"
                term = f"%{filters['search']}%"
                params.extend([term, term])
            
            query += " ORDER BY RANDOM() LIMIT ?"
            params.append(boss['hp'])
            
            rows = conn.execute(query, params).fetchall()
            
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
        
        user_id = session.get('user_id', 1)
        
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
