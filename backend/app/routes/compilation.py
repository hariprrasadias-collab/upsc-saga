from flask import Blueprint, jsonify
from app.services.compilation_service import CompilationService

bp = Blueprint('compilation', __name__, url_prefix='/api/compilation')

@bp.route('/months', methods=['GET'])
def get_months():
    """Get list of months with available articles"""
    try:
        months = CompilationService.get_available_months()
        return jsonify(months)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:year>/<int:month>', methods=['GET'])
def get_compilation(year, month):
    """Get compilation for a specific month"""
    try:
        compilation = CompilationService.get_monthly_compilation(year, month)
        return jsonify(compilation)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
