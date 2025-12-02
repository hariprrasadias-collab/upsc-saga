from flask import Blueprint, request, jsonify
from app.services.golden_path_service import golden_path

golden_path_bp = Blueprint('golden_path', __name__)

@golden_path_bp.route('/graph', methods=['GET'])
def get_graph():
    """Get the full syllabus graph structure."""
    try:
        data = golden_path.get_graph_data()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@golden_path_bp.route('/optimize', methods=['POST'])
def optimize_path():
    """
    Calculate the optimal study path.
    Body: { "time_budget": 100 } (hours)
    """
    try:
        data = request.json
        time_budget = data.get('time_budget', 100) # Default 100 hours
        
        result = golden_path.calculate_optimal_path(time_budget)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
