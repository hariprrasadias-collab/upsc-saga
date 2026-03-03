from app.utils.session import get_current_user_id
from flask import Blueprint, request, jsonify
from app.db import get_db
from app.services.essay_evaluator import EssayEvaluator
import json

essay_bp = Blueprint('essay', __name__)
evaluator = EssayEvaluator() # ModelManager handles internal init

@essay_bp.route('/api/essay/submit', methods=['POST'])
def submit_essay():
    """Submit an essay for AI evaluation"""
    try:
        data = request.json
        user_id = get_current_user_id()
        topic = data.get('topic')
        content = data.get('content')
        
        if not topic or not content:
            return jsonify({'error': 'Topic and content are required'}), 400
            
        # Evaluate using AI
        evaluation = evaluator.evaluate_essay(topic, content)
        score = evaluation.get('score', 0)
        
        # Save to database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO essay_submissions (user_id, topic, content, evaluation_json, score)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, topic, content, json.dumps(evaluation), score))
        conn.commit()
        submission_id = cursor.lastrowid
        
        return jsonify({
            'id': submission_id,
            'evaluation': evaluation
        })
    except Exception as e:
        print(f"Essay submission error: {e}")
        return jsonify({'error': str(e)}), 500

@essay_bp.route('/api/essay/history', methods=['GET'])
def get_essay_history():
    """Get past essay submissions"""
    try:
        user_id = get_current_user_id()
        conn = get_db()
        submissions = conn.execute('''
            SELECT id, topic, submitted_at, score
            FROM essay_submissions
            WHERE user_id = ?
            ORDER BY submitted_at DESC
        ''', (user_id,)).fetchall()
        
        return jsonify([dict(s) for s in submissions])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@essay_bp.route('/api/essay/<int:id>', methods=['GET'])
def get_essay_detail(id):
    """Get details of a specific submission"""
    try:
        user_id = get_current_user_id()
        conn = get_db()
        submission = conn.execute('''
            SELECT * FROM essay_submissions
            WHERE id = ? AND user_id = ?
        ''', (id, user_id)).fetchone()
        
        if not submission:
            return jsonify({'error': 'Submission not found'}), 404
            
        result = dict(submission)
        # Parse JSON string back to object
        if result.get('evaluation_json'):
            try:
                result['evaluation'] = json.loads(result['evaluation_json'])
            except json.JSONDecodeError:
                result['evaluation'] = {}
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@essay_bp.route('/api/essay/topics', methods=['GET'])
def get_essay_topics():
    """Get list of sample essay topics (PYQs)"""
    try:
        topics = [
            "The process of self-discovery has now been technologically outsourced.",
            "Your perception of me is a reflection of you; my reaction to you is an awareness of me.",
            "Philosophy of wantlessness is Utopian, while materialism is a chimera.",
            "The real is rational and the rational is real.",
            "Hand that rocks the cradle rules the world.",
            "Technology cannot replace manpower.",
            "Crisis of conscience in public administration.",
            "Digital economy: A leveller or a source of economic inequality."
        ]
        return jsonify(topics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
