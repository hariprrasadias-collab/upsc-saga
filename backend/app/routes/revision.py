from flask import Blueprint, jsonify, request
from app.services.upsc_summarizer import generate_one_liner, generate_mnemonic
import sqlite3
import os
import json
from app.services.model_manager import model_manager

bp = Blueprint('revision', __name__, url_prefix='/api/revision')

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'upsc_saga.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@bp.route('/one-liner', methods=['POST'])
def create_one_liner():
    """Generate a one-liner summary for a topic"""
    data = request.json
    topic_id = data.get('topic_id')
    title = data.get('title')
    content = data.get('content', '')
    
    if not title:
        return jsonify({'success': False, 'error': 'Title required'}), 400
    
    # Generate one-liner using AI
    one_liner = generate_one_liner(title, content)
    
    # Save to database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO revision_cards (topic_id, title, one_liner, full_content, created_at)
        VALUES (?, ?, ?, ?, datetime('now'))
    ''', (topic_id, title, one_liner, content))
    conn.commit()
    card_id = cursor.lastrowid
    conn.close()
    
    return jsonify({
        'success': True,
        'card': {
            'id': card_id,
            'topic_id': topic_id,
            'title': title,
            'one_liner': one_liner
        }
    })

@bp.route('/auto-forge', methods=['POST'])
def auto_forge_weakness_cards():
    """Auto-generates 3-5 flashcards based on the user's weakest topics."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 1. Fetch the user's weakest metrics (e.g. from weekly analytics)
        # Using a simple heuristic for now: weakest stat or random active subjects
        cursor.execute('''
            SELECT topic, subject, status 
            FROM syllabus_topics 
            WHERE status != 'Mastered'
            ORDER BY RANDOM() LIMIT 3
        ''')
        weak_topics = cursor.fetchall()
        
        if not weak_topics:
            return jsonify({'success': False, 'message': 'No weak topics found to auto-forge.'})
            
        topics_context = ", ".join([t['topic'] for t in weak_topics])
        
        # 2. Call the Oracle (Model Manager)
        prompt = f"""
        You are the 'Flashcard Forge AI' for a UPSC aspirant.
        The user is currently struggling with these topics: {topics_context}.
        
        Generate exactly 3 high-yield revision flashcards targeting these topics.
        Provide the response ONLY as valid JSON in this exact format, with no markdown code blocks:
        [
          {{
            "title": "Short Topic Concept",
            "one_liner": "A brilliant, easy-to-remember 1-sentence summary that acts as a memory hook."
          }}
        ]
        """
        response = model_manager.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        cards_data = json.loads(text)
        
        # 3. Save the new cards to the DB
        saved_cards = []
        if cards_data:
            placeholders = ", ".join(["(?, ?, ?, ?, datetime('now'))"] * len(cards_data))
            params = []
            for card in cards_data:
                params.extend(['auto-forged', card['title'], card['one_liner'], "Auto-forged from weakness scan"])

            cursor.execute(f'''
                INSERT INTO revision_cards (topic_id, title, one_liner, full_content, created_at)
                VALUES {placeholders}
            ''', params)
            
            # Fetch the inserted cards to get their IDs
            last_n_ids = cursor.execute(f'SELECT id FROM revision_cards ORDER BY id DESC LIMIT {len(cards_data)}').fetchall()
            # IDs are returned in descending order, we reverse them to match the insertion order
            inserted_ids = [row['id'] for row in reversed(last_n_ids)]

            for i, card in enumerate(cards_data):
                saved_cards.append({
                    'id': inserted_ids[i] if i < len(inserted_ids) else None,
                    'topic_id': 'auto-forged',
                    'title': card['title'],
                    'one_liner': card['one_liner'],
                    'created_at': "Just now" # Frontend will fix the date
                })
            
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'cards': saved_cards
        })
        
    except Exception as e:
        print(f"Auto-forge Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/hint', methods=['POST'])
def get_card_hint():
    """Generates an AI hint for a specific revision card."""
    data = request.json
    item_type = data.get('item_type')
    item_id = data.get('item_id')

    # For now, we only support finding the title/content from revision_cards
    # Other items (like quests) might not be in this table, but we can try reading them later
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Determine table based on item_type if needed, assuming revision_cards for now
        table = 'revision_cards'
        if item_type == 'concept':
             table = 'revision_cards' # Map it

        cursor.execute(f"SELECT title, one_liner, full_content FROM revision_cards WHERE id = ?", (item_id,))
        card = cursor.fetchone()
        conn.close()

        title = card['title'] if card else f"Item {item_id}"
        content = card['full_content'] if card else "General Knowledge"

        prompt = f"""
        You are an AI Whisperer/Hint Generator for a UPSC aspirant.
        The user is stuck trying to recall this flashcard:
        Title: {title}
        Content Text: {content[:1000]}

        Provide a very short, cryptic, but helpful 1-sentence hint or mnemonic. Do NOT give away the exact answer. Make it sound mystical or analytical.
        """
        response = model_manager.generate_content(prompt)
        
        return jsonify({
            'success': True,
            'hint': response.text.replace("\"", "").strip()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/cards', methods=['GET'])
def get_revision_cards():
    """Get all revision cards"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, topic_id, title, one_liner, created_at
        FROM revision_cards
        ORDER BY created_at DESC
    ''')
    cards = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'success': True,
        'cards': [dict(card) for card in cards]
    })

@bp.route('/cards/<int:card_id>', methods=['GET', 'DELETE'])
def handle_card(card_id):
    """Get or delete a specific revision card"""
    if request.method == 'GET':
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, topic_id, title, one_liner, full_content, created_at
            FROM revision_cards
            WHERE id = ?
        ''', (card_id,))
        card = cursor.fetchone()
        conn.close()
        
        if card:
            return jsonify({
                'success': True,
                'card': dict(card)
            })
        else:
            return jsonify({'success': False, 'error': 'Card not found'}), 404
    
    elif request.method == 'DELETE':
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM revision_cards WHERE id = ?', (card_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if deleted:
            return jsonify({'success': True, 'message': 'Card deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Card not found'}), 404

@bp.route('/mnemonic', methods=['POST'])
def create_mnemonic():
    """Generate a mnemonic for given content"""
    data = request.json
    text = data.get('text')
    mnemonic_type = data.get('type', 'facts')  # facts, dates, list, concept
    flashcard_id = data.get('flashcard_id')
    
    if not text:
        return jsonify({'success': False, 'error': 'Text required'}), 400
    
    # Generate mnemonic using AI
    result_data = generate_mnemonic(text, mnemonic_type)
    mnemonic = result_data.get('mnemonic', 'Error generating mnemonic')
    vis_prompt = result_data.get('visualization_prompt', '')
    
    # If flashcard_id provided, update that flashcard
    if flashcard_id:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE flashcards
            SET mnemonic = ?
            WHERE id = ?
        ''', (mnemonic, flashcard_id))
        conn.commit()
        conn.close()
    
    # Save to history
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO mnemonics_history (mnemonic_text, original_text, mnemonic_type, visualization_prompt)
            VALUES (?, ?, ?, ?)
        ''', (mnemonic, text, mnemonic_type, vis_prompt))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving mnemonic history: {e}")
    
    return jsonify({
        'success': True,
        'mnemonic': mnemonic,
        'visualization_prompt': vis_prompt,
        'type': mnemonic_type
    })

@bp.route('/mnemonic/history', methods=['GET'])
def get_mnemonic_history():
    """Get mnemonic generation history"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, mnemonic_text, original_text, mnemonic_type, visualization_prompt, created_at
            FROM mnemonics_history
            ORDER BY created_at DESC
        ''')
        history = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'history': [dict(row) for row in history]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/mnemonic/history/<int:history_id>', methods=['DELETE'])
def delete_mnemonic_history(history_id):
    """Delete a mnemonic from history"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM mnemonics_history WHERE id = ?', (history_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if deleted:
            return jsonify({'success': True, 'message': 'Mnemonic deleted successfully'})
        else:
            return jsonify({'success': False, 'error': 'Mnemonic not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
