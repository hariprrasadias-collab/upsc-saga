from flask import Blueprint, request, jsonify
from app.db import get_db
from app.services.mimir_service import mimir_service
import json

scribe_bp = Blueprint('scribe', __name__)

@scribe_bp.route('/evaluate', methods=['POST'])
def evaluate_answer():
    try:
        data = request.json
        user_id = 1  # TODO: Get from session
        question_text = data.get('question')
        answer_text = data.get('answer')
        
        if not question_text or not answer_text:
            return jsonify({'error': 'Question and Answer are required'}), 400

        # Call AI Service (Returns Dict now)
        evaluation_data = mimir_service.evaluate_answer(question_text, answer_text)
        
        # Check if error fallback occurred
        if isinstance(evaluation_data, str): # Should not happen with new fix, but safety first
             evaluation_data = {"score": 0, "feedback": evaluation_data}

        score = evaluation_data.get('score', 0)

        # Save to Database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scribe_evaluations (user_id, question_text, answer_text, score, feedback_json)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, question_text, answer_text, score, json.dumps(evaluation_data)))
        conn.commit()
        
        new_id = cursor.lastrowid

        return jsonify({
            'id': new_id,
            'score': score,
            'feedback': evaluation_data
        })

    except Exception as e:
        print(f"Scribe evaluation error: {e}")
        return jsonify({'error': str(e)}), 500

@scribe_bp.route('/history', methods=['GET'])
def get_history():
    try:
        user_id = 1
        conn = get_db()
        rows = conn.execute('''
            SELECT id, question_text, answer_text, score, feedback_json, created_at 
            FROM scribe_evaluations
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,)).fetchall()
        
        history = []
        for row in rows:
            item = dict(row)
            if item.get('feedback_json'):
                try:
                    item['feedback_json'] = json.loads(item['feedback_json'])
                except:
                    item['feedback_json'] = {}
            history.append(item)
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
