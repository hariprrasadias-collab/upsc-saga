"""
Project Foresight API Routes
Endpoints for question prediction and probability analysis
"""

from flask import Blueprint, request, jsonify
from app.services.foresight_engine import foresight_engine

foresight_bp = Blueprint('foresight', __name__)

@foresight_bp.route('/predict', methods=['POST'])
def predict_questions():
    """
    Trigger question prediction.
    
    Request Body:
        {
            "subject": "Polity",  # Optional, defaults to "All"
            "timeframe_days": 90   # Optional, defaults to 90
        }
    
    Response:
        {
            "predictions": [...],
            "count": 10,
            "generated_at": "2024-..."
        }
    """
    data = request.json or {}
    subject = data.get('subject', 'All')
    timeframe_days = data.get('timeframe_days', 90)
    
    try:
        predictions = foresight_engine.predict_questions(
            subject=subject,
            timeframe_days=timeframe_days
        )
        
        return jsonify({
            'predictions': predictions,
            'count': len(predictions),
            'subject': subject,
            'timeframe_days': timeframe_days
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'predictions': []
        }), 500

@foresight_bp.route('/subjects', methods=['GET'])
def get_subjects():
    """Get available subjects for focused predictions"""
    subjects = [
        "All",
        "Polity",
        "History",
        "Geography",
        "Economy",
        "Science & Technology",
        "Environment",
        "Current Affairs",
        "International Relations"
    ]
    return jsonify({'subjects': subjects})

@foresight_bp.route('/save', methods=['POST'])
def save_prediction():
    """Save a prediction to favorites"""
    try:
        from app.db import get_db
        conn = get_db()
        data = request.json
        
        conn.execute('''
            INSERT INTO foresight_predictions 
            (user_id, question, type, probability, reasoning, subject, topic, preparation_tip)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            1, # Default User ID
            data.get('question'),
            data.get('type'),
            data.get('probability'),
            data.get('reasoning'),
            data.get('subject'),
            data.get('topic'),
            data.get('preparation_tip')
        ))
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Prediction saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@foresight_bp.route('/saved', methods=['GET'])
def get_saved_predictions():
    """Get all saved predictions"""
    try:
        from app.db import get_db
        conn = get_db()
        
        rows = conn.execute('SELECT * FROM foresight_predictions ORDER BY created_at DESC').fetchall()
        predictions = []
        for r in rows:
            predictions.append({
                'id': r['id'],
                'question': r['question'],
                'type': r['type'],
                'probability': r['probability'],
                'reasoning': r['reasoning'],
                'subject': r['subject'],
                'topic': r['topic'],
                'preparation_tip': r['preparation_tip'],
                'generated_at': r['created_at'],
                'is_favorite': True
            })
            
        return jsonify({'predictions': predictions})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@foresight_bp.route('/unsave/<int:pred_id>', methods=['DELETE'])
def unsave_prediction(pred_id):
    """Remove a prediction from favorites"""
    try:
        from app.db import get_db
        conn = get_db()
        conn.execute('DELETE FROM foresight_predictions WHERE id = ?', (pred_id,))
        conn.commit()
        return jsonify({'success': True, 'message': 'Prediction removed'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
