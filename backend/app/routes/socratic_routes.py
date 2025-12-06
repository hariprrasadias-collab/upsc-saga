from flask import Blueprint, request, jsonify
from app.services.socratic_service import generate_debate_turn

socratic_bp = Blueprint('socratic', __name__)

@socratic_bp.route('/debate', methods=['POST'])
def debate_turn():
    try:
        data = request.json
        topic = data.get('topic')
        history = data.get('history', [])
        user_input = data.get('user_input')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
            
        response = generate_debate_turn(topic, history, user_input)
        return jsonify(response)
    except Exception as e:
        print(f"Route Error: {e}")
        return jsonify({'error': str(e)}), 500

@socratic_bp.route('/history', methods=['GET'])
def get_history():
    try:
        from app.db import get_db
        conn = get_db()
        limit = request.args.get('limit', 20)
        rows = conn.execute('SELECT * FROM socratic_conversations ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
        return jsonify({'success': True, 'data': [dict(row) for row in rows]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
