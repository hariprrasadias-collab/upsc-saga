"""
API Routes for The Neural Hash
"""
from flask import Blueprint, jsonify, request
from app.services.neural_hash_service import neural_hash_service

neural_hash_bp = Blueprint('neural_hash', __name__)

@neural_hash_bp.route('/decode', methods=['POST'])
def decode_text():
    """
    Decode text to find patterns and keywords.
    Expected JSON: { "text": "...", "type": "pyq|editorial|..." }
    """
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'success': False, 'error': 'No text provided'}), 400

    text = data['text']
    context_type = data.get('type', 'general')

    result = neural_hash_service.decode_text(text, context_type)
    
    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 500
