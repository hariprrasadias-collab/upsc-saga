# Flashcards API Routes
from flask import Blueprint, request, jsonify
from app.db import get_db
from datetime import datetime, timedelta
from app.services.ebisu_srs import (
    get_initial_parameters,
    update_recall,
    get_next_review_datetime,
    predict_recall,
    get_urgency_score,
    get_card_maturity
)
from app.services.xp_service import award_xp
from app.utils.session import get_current_user_id as get_user_id
from app.validators import require_json_fields
import json

flashcards = Blueprint('flashcards', __name__)

from app import cache

# ==================== DECK MANAGEMENT ====================

@flashcards.route('/api/flashcards/decks', methods=['GET'])
@cache.cached(timeout=120)
def get_decks():
    """Get all decks with card counts"""
    try:
        user_id = get_user_id()
        conn = get_db()
        
        decks = conn.execute('''
            SELECT d.id, d.name, d.description, d.subject, d.color, d.created_at,
                   COUNT(f.id) as card_count
            FROM decks d
            LEFT JOIN flashcards f ON d.id = f.deck_id
            WHERE d.user_id = ?
            GROUP BY d.id
            ORDER BY d.created_at DESC
        ''', (user_id,)).fetchall()
        
        return jsonify([dict(d) for d in decks])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@flashcards.route('/api/flashcards/decks',methods=['POST'])
def create_deck():
    """Create a new deck"""
    try:
        user_id = get_user_id()
        data = request.get_json()
        
        conn = get_db()
        cursor = conn.execute('''
            INSERT INTO decks (user_id, name, description, subject, color)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, data['name'], data.get('description', ''),
              data.get('subject', ''), data.get('color', '#3498db')))
        
        deck_id = cursor.lastrowid
        conn.commit()
        cache.clear()
        
        return jsonify({'id': deck_id, 'message': 'Deck created'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@flashcards.route('/api/flashcards/decks/<int:deck_id>', methods=['GET'])
def get_deck(deck_id):
    """Get deck with all its cards"""
    try:
        user_id = get_user_id()
        conn = get_db()
        
        deck = conn.execute(
            'SELECT * FROM decks WHERE id = ? AND user_id = ?',
            (deck_id, user_id)
        ).fetchone()
        
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404
        
        cards = conn.execute('''
            SELECT f.*, 
                   (SELECT rating FROM review_sessions 
                    WHERE flashcard_id = f.id 
                    ORDER BY reviewed_at DESC LIMIT 1) as last_rating,
                   (SELECT reviewed_at FROM review_sessions 
                    WHERE flashcard_id = f.id 
                    ORDER BY reviewed_at DESC LIMIT 1) as last_reviewed
            FROM flashcards f
            WHERE f.deck_id = ?
            ORDER BY f.created_at DESC
        ''', (deck_id,)).fetchall()
        
        return jsonify({
            'deck': dict(deck),
            'cards': [dict(c) for c in cards]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@flashcards.route('/api/flashcards/decks/<int:deck_id>', methods=['DELETE'])
def delete_deck(deck_id):
    """Delete deck and all its cards"""
    try:
        user_id = get_user_id()
        conn = get_db()
        
        # Check ownership
        deck = conn.execute(
            'SELECT * FROM decks WHERE id = ? AND user_id = ?',
            (deck_id, user_id)
        ).fetchone()
        
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404
        
        # CASCADE will delete flashcards and review_sessions
        conn.execute('DELETE FROM decks WHERE id = ?', (deck_id,))
        conn.commit()
        cache.clear()
        
        return jsonify({'message': 'Deck deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== FLASHCARD CRUD ====================

@flashcards.route('/api/flashcards', methods=['POST'])
def create_flashcard():
    """Create a new flashcard"""
    try:
        user_id = get_user_id()
        data = request.get_json()
        
        valid, err = require_json_fields(data, ['deck_id', 'front', 'back'])
        if not valid:
            return jsonify({'error': err}), 400
            
        conn = get_db()
        
        cursor = conn.execute('''
            INSERT INTO flashcards (deck_id, front, back, card_type, source, source_id, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['deck_id'],
            data['front'],
            data['back'],
            data.get('card_type', 'basic'),
            data.get('source', 'manual'),
            data.get('source_id'),
            json.dumps(data.get('tags', []))
        ))
        
        card_id = cursor.lastrowid
        conn.commit()
        
        # Award 2 XP for creating a card (handle failure gracefully)
        try:
            award_xp(user_id, 2, 0)
        except Exception as xp_error:
            print(f"Failed to award XP for flashcard creation: {xp_error}")
        
        return jsonify({'id': card_id, 'message': 'Card created'}), 201
    except Exception as e:
        print(f"Error creating flashcard: {e}")
        return jsonify({'error': str(e)}), 500


@flashcards.route('/api/flashcards/<int:card_id>', methods=['PUT'])
def update_flashcard(card_id):
    """Update a flashcard"""
    try:
        user_id = get_user_id()
        data = request.get_json()
        conn = get_db()
        
        # Verify ownership via deck
        card = conn.execute('''
            SELECT f.id FROM flashcards f
            JOIN decks d ON f.deck_id = d.id
            WHERE f.id = ? AND d.user_id = ?
        ''', (card_id, user_id)).fetchone()
        
        if not card:
            return jsonify({'error': 'Card not found'}), 404
        
        conn.execute('''
            UPDATE flashcards
            SET front = ?, back = ?, tags = ?
            WHERE id = ?
        ''', (data['front'], data['back'], json.dumps(data.get('tags', [])), card_id))
        
        conn.commit()
        
        return jsonify({'message': 'Card updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@flashcards.route('/api/flashcards/<int:card_id>', methods=['DELETE'])
def delete_flashcard(card_id):
    """Delete a flashcard"""
    try:
        user_id = get_user_id()
        conn = get_db()
        
        # Verify ownership via deck
        card = conn.execute('''
            SELECT f.id FROM flashcards f
            JOIN decks d ON f.deck_id = d.id
            WHERE f.id = ? AND d.user_id = ?
        ''', (card_id, user_id)).fetchone()
        
        if not card:
            return jsonify({'error': 'Card not found'}), 404
        
        conn.execute('DELETE FROM flashcards WHERE id = ?', (card_id,))
        conn.commit()
        
        return jsonify({'message': 'Card deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== REVIEW SYSTEM ====================

@flashcards.route('/api/flashcards/due', methods=['GET'])
def get_due_cards():
    """Get cards due for review"""
    try:
        user_id = get_user_id()
        deck_id = request.args.get('deck_id', type=int)
        limit = request.args.get('limit', 20, type=int)
        
        conn = get_db()
        
        # Get cards with their latest review session
        query = '''
            SELECT f.*,
                   rs.halflife, rs.alpha, rs.beta, rs.next_review, rs.reviewed_at
            FROM flashcards f
            LEFT JOIN (
                SELECT flashcard_id, halflife, alpha, beta, next_review, reviewed_at
                FROM review_sessions
                WHERE (flashcard_id, reviewed_at) IN (
                    SELECT flashcard_id, MAX(reviewed_at)
                    FROM review_sessions
                    GROUP BY flashcard_id
                )
            ) rs ON f.id = rs.flashcard_id
            WHERE 1=1
        '''
        
        params = []
        if deck_id:
            query += ' AND f.deck_id = ?'
            params.append(deck_id)
        
        # Get all cards
        all_cards = conn.execute(query, params).fetchall()
        
        # Calculate urgency for each card
        cards_with_urgency = []
        for card in all_cards:
            card_dict = dict(card)
            
            if card['reviewed_at'] is None:
                # New card - highest urgency
                urgency = 10.0
                card_dict['maturity'] = 'new'
            else:
                # Calculate urgency based on Ebisu
                last_review = datetime.fromisoformat(card['reviewed_at'])
                urgency = get_urgency_score(
                    card['alpha'], card['beta'], card['halflife'], last_review
                )
                card_dict['maturity'] = get_card_maturity(
                    card['alpha'], card['beta'], card['halflife']
                )
            
            card_dict['urgency'] = urgency
            cards_with_urgency.append(card_dict)
        
        # Sort by urgency (highest first) and limit
        cards_with_urgency.sort(key=lambda x: x['urgency'], reverse=True)
        due_cards = cards_with_urgency[:limit]
        
        return jsonify(due_cards)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@flashcards.route('/api/flashcards/<int:card_id>/review', methods=['POST'])
def review_flashcard(card_id):
    """Record a review result"""
    try:
        user_id = get_user_id()
        data = request.get_json()
        rating = data['rating']  # 1=Again, 2=Hard, 3=Good, 4=Easy
        time_taken = data.get('time_taken', 0)
        
        conn = get_db()
        
        # Get last review session for this card
        last_session = conn.execute('''
            SELECT * FROM review_sessions
            WHERE flashcard_id = ?
            ORDER BY reviewed_at DESC
            LIMIT 1
        ''', (card_id,)).fetchone()
        
        if last_session:
            # Calculate elapsed time
            last_review_time = datetime.fromisoformat(last_session['reviewed_at'])
            elapsed = datetime.now() - last_review_time
            elapsed_hours = elapsed.total_seconds() / 3600
            
            # Update Ebisu parameters
            new_alpha, new_beta, new_halflife = update_recall(
                last_session['alpha'],
                last_session['beta'],
                last_session['halflife'],
                rating,
                elapsed_hours
            )
        else:
            # First review - use initial parameters
            new_alpha, new_beta, new_halflife = get_initial_parameters()
            
            # Apply first review
            new_alpha, new_beta, new_halflife = update_recall(
                new_alpha, new_beta, new_halflife, rating, 24.0  # Assume 1 day
            )
        
        # Calculate next review time
        next_review = get_next_review_datetime(new_alpha, new_beta, new_halflife)
        
        # Save review session
        conn.execute('''
            INSERT INTO review_sessions
            (flashcard_id, user_id, rating, time_taken, halflife, alpha, beta, next_review)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (card_id, user_id, rating, time_taken, new_halflife, new_alpha, new_beta, next_review))
        
        conn.commit()
        
        return jsonify({
            'message': 'Review recorded',
            'next_review': next_review.isoformat(),
            'halflife_days': round(new_halflife, 2),
            'maturity': get_card_maturity(new_alpha, new_beta, new_halflife)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@flashcards.route('/api/flashcards/award-xp', methods=['POST'])
def award_review_xp():
    """Award XP after completing review session"""
    try:
        user_id = get_user_id()
        data = request.get_json()
        cards_reviewed = data.get('cards_reviewed', 0)
        
        # Award 5 XP per 10 cards
        xp_per_batch = 5
        batches = cards_reviewed // 10
        xp_earned = batches * xp_per_batch
        
        if xp_earned > 0:
            award_xp(user_id, xp_earned, 0)
        
        return jsonify({'xp_earned': xp_earned})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ANALYTICS ====================

@flashcards.route('/api/flashcards/analytics', methods=['GET'])
def get_analytics():
    """Get review statistics"""
    try:
        user_id = get_user_id()
        conn = get_db()
        
        # Total cards
        total = conn.execute('SELECT COUNT(*) FROM flashcards').fetchone()[0]
        
        # Get maturity breakdown
        all_cards = conn.execute('''
            SELECT f.id, rs.halflife, rs.alpha, rs.beta
            FROM flashcards f
            LEFT JOIN (
                SELECT flashcard_id, halflife, alpha, beta
                FROM review_sessions
                WHERE (flashcard_id, reviewed_at) IN (
                    SELECT flashcard_id, MAX(reviewed_at)
                    FROM review_sessions
                    GROUP BY flashcard_id
                )
            ) rs ON f.id = rs.flashcard_id
        ''').fetchall()
        
        maturity_counts = {'new': 0, 'learning': 0, 'young': 0, 'mature': 0, 'mastered': 0}
        for card in all_cards:
            if card['halflife'] is None:
                maturity_counts['new'] += 1
            else:
                maturity = get_card_maturity(card['alpha'], card['beta'], card['halflife'])
                maturity_counts[maturity] += 1
        
        # Review streak (days with at least one review)
        recent_days = conn.execute('''
            SELECT DATE(reviewed_at) as review_date
            FROM review_sessions
            WHERE user_id = ? AND reviewed_at >= date('now', '-30 days')
            GROUP BY DATE(reviewed_at)
            ORDER BY review_date DESC
        ''', (user_id,)).fetchall()
        
        streak = 0
        if recent_days:
            last_date = datetime.now().date()
            for row in recent_days:
                review_date = datetime.fromisoformat(row['review_date']).date()
                if (last_date - review_date).days <= 1:
                    streak += 1
                    last_date = review_date
                else:
                    break
        
        # Total reviews
        total_reviews = conn.execute(
            'SELECT COUNT(*) FROM review_sessions WHERE user_id = ?',
            (user_id,)
        ).fetchone()[0]
        
        return jsonify({
            'total_cards': total,
            'new': maturity_counts['new'],
            'learning': maturity_counts['learning'],
            'young': maturity_counts['young'],
            'mature': maturity_counts['mature'],
            'mastered': maturity_counts['mastered'],
            'daily_streak': streak,
            'total_reviews': total_reviews
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== CSV IMPORT ====================

@flashcards.route('/api/flashcards/import', methods=['POST'])
def import_flashcards_csv():
    """Import flashcards from CSV file"""
    try:
        import csv
        import io
        
        deck_id = request.form.get('deck_id', type=int)
        if not deck_id:
            return jsonify({'error': 'deck_id is required'}), 400
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read CSV with proper quote handling
        stream = io.StringIO(file.stream.read().decode('UTF8'), newline=None)
        csv_reader = csv.DictReader(stream)
        
        conn = get_db()
        imported_count = 0
        errors = []
        
        for i, row in enumerate(csv_reader, start=2):  # Start at 2 (line 1 is header)
            try:
                front = row.get('Front', '').strip()
                back = row.get('Back', '').strip()
                
                if not front or not back:
                    errors.append(f"Line {i}: Missing front or back content")
                    continue
                
                # Insert flashcard
                conn.execute('''\
                    INSERT INTO flashcards (deck_id, front, back, card_type, source)
                    VALUES (?, ?, ?, ?, ?)
                ''', (deck_id, front, back, 'basic', 'csv_import'))
                
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Line {i}: {str(e)}")
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'imported': imported_count,
            'errors': errors
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
