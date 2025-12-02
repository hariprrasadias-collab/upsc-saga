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
