from flask import Blueprint, request, jsonify
from app.services.socratic_service import generate_debate_turn, continue_autonomous_debate
from app.db_models.automation_storage import save_socratic_dialogue
import json

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

@socratic_bp.route('/continue', methods=['POST'])
def continue_debate():
    """
    Continues an existing debate and updates the DB.
    """
    try:
        data = request.json
        dialogue_id = data.get('id')
        topic = data.get('topic')
        current_history = data.get('history')

        if not dialogue_id or not topic:
             return jsonify({'error': 'ID and Topic required'}), 400

        # Generate new turns
        new_history_json, new_history_list, new_verdict = continue_autonomous_debate(topic, current_history, additional_turns=3)

        # Update DB
        from app.db import get_db
        conn = get_db()
        verdict_json = json.dumps(new_verdict)

        conn.execute('''
            UPDATE socratic_conversations
            SET dialogue = ?, insight = ?
            WHERE id = ?
        ''', (new_history_json, verdict_json, dialogue_id))
        conn.commit()

        return jsonify({
            'success': True,
            'dialogue': new_history_json,
            'insight': verdict_json
        })

    except Exception as e:
        print(f"Continue Route Error: {e}")
        return jsonify({'error': str(e)}), 500

@socratic_bp.route('/history', methods=['GET'])
def get_history():
    try:
        from app.db import get_db
        conn = get_db()
        # SECURITY: Explicitly cast 'limit' to int to prevent potential SQL injection or type confusion when passed to parameterized queries
        limit = request.args.get('limit', 20, type=int)
        rows = conn.execute('SELECT * FROM socratic_conversations ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
        return jsonify({'success': True, 'data': [dict(row) for row in rows]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
