"""
API Routes for The Neural Hash
"""
from flask import Blueprint, jsonify, request
from app.services.neural_hash_service_v2 import neural_hash_service
from app.db_models.neural_hash import get_neural_hash_history

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

@neural_hash_bp.route('/history', methods=['GET'])
def get_history():
    """Get past decodes"""
    try:
        from app.db_models.neural_hash import get_neural_hash_history
        history = get_neural_hash_history()
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
