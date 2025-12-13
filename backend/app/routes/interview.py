from flask import Blueprint, request, jsonify
from app.services.interview_service import interview_service

interview_bp = Blueprint('interview', __name__)

@interview_bp.route('/respond', methods=['POST'])
def respond_to_candidate():
    """
    Simulate Board Response
    Expects: {
        "topic": str,
        "history": list[dict],
        "daf_profile": dict
    }
    """
    try:
        data = request.json
        response = interview_service.generate_board_response(
            topic=data.get('topic'),
            history=data.get('history'),
            daf_profile=data.get('daf_profile')
        )
        return jsonify(response)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
