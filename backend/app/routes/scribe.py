from flask import Blueprint, request, jsonify
from app.db import get_db
from app.services.mimir_service import mimir_service
import json

scribe_bp = Blueprint('scribe', __name__)

@scribe_bp.route('/api/scribe/evaluate', methods=['POST'])
def evaluate_answer():
    try:
        data = request.json
        user_id = 1  # TODO: Get from session
        question_text = data.get('question')
        answer_text = data.get('answer')
        question_id = data.get('question_id')  # Optional

        if not question_text or not answer_text:
            return jsonify({'error': 'Question and Answer are required'}), 400

        # Call AI Service
        evaluation_json_str = mimir_service.evaluate_answer(question_text, answer_text)
        
        # Parse JSON
        try:
            evaluation_data = json.loads(evaluation_json_str)
            score = evaluation_data.get('score', 0)
        except json.JSONDecodeError:
            # Fallback if AI returns bad JSON
            print(f"Failed to parse AI response: {evaluation_json_str}")
            return jsonify({'error': 'Failed to generate valid evaluation', 'raw_response': evaluation_json_str}), 500

        # Save to Database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO answer_evaluations (user_id, question_id, question_text, answer_text, score, feedback_json)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, question_id, question_text, answer_text, score, evaluation_json_str))
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

@scribe_bp.route('/api/scribe/history', methods=['GET'])
def get_history():
    try:
        user_id = 1
        conn = get_db()
        rows = conn.execute('''
            SELECT id, question_text, score, created_at 
            FROM answer_evaluations
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,)).fetchall()
        
        history = [dict(row) for row in rows]
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
