from flask import Blueprint, request, jsonify, session
from app.db import get_db
from app.services.mimir_service import mimir_service

mimir_bp = Blueprint('mimir_chat', __name__)

@mimir_bp.route('/api/mimir/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_id = session.get('user_id', 1)
        message = data.get('message')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
            
        conn = get_db()
        
        # Get recent history for context
        history_rows = conn.execute('''
            SELECT role, content FROM mimir_chat_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (user_id,)).fetchall()
        
        # Reverse to chronological order
        history = [{'role': row['role'], 'content': row['content']} for row in reversed(history_rows)]
        
        # Generate AI response
        ai_response = mimir_service.generate_response(message, history)
        
        # Save User message
        conn.execute('''
            INSERT INTO mimir_chat_history (user_id, role, content)
            VALUES (?, ?, ?)
        ''', (user_id, 'user', message))
        
        # Save AI response
        conn.execute('''
            INSERT INTO mimir_chat_history (user_id, role, content)
            VALUES (?, ?, ?)
        ''', (user_id, 'model', ai_response))
        
        conn.commit()
        
        return jsonify({'response': ai_response})
        
    except Exception as e:
        print(f"Mimir chat error: {e}")
        return jsonify({'error': str(e)}), 500

@mimir_bp.route('/api/mimir/history', methods=['GET'])
def get_history():
    try:
        user_id = session.get('user_id', 1)
        conn = get_db()
        rows = conn.execute('''
            SELECT role, content, timestamp FROM mimir_chat_history
            WHERE user_id = ?
            ORDER BY timestamp ASC
        ''', (user_id,)).fetchall()
        
        history = [dict(row) for row in rows]
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mimir_bp.route('/api/mimir/clear', methods=['POST'])
def clear_history():
    try:
        user_id = session.get('user_id', 1)
        conn = get_db()
        conn.execute('DELETE FROM mimir_chat_history WHERE user_id = ?', (user_id,))
        conn.commit()
        return jsonify({'message': 'History cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
