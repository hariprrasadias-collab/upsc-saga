from flask import Blueprint, jsonify, request
from app.services.upsc_summarizer import generate_one_liner, generate_mnemonic
import sqlite3
import os

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

@bp.route('/cards/<int:card_id>', methods=['GET'])
def get_card_detail(card_id):
    """Get detailed view of a revision card"""
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
    mnemonic = generate_mnemonic(text, mnemonic_type)
    
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
    
    return jsonify({
        'success': True,
        'mnemonic': mnemonic,
        'type': mnemonic_type
    })
