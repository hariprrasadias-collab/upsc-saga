from flask import Blueprint, request, jsonify
from app.services.triangulation_service import analyze_topic_triangulation

triangulation_bp = Blueprint('triangulation', __name__)

@triangulation_bp.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        text = data.get('text')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
            
        result = analyze_topic_triangulation(text)
        return jsonify(result)
    except Exception as e:
        print(f"Triangulation Route Error: {e}")
        return jsonify({'error': str(e)}), 500
