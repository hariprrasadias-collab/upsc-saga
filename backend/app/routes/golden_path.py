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
    Body: {
        "time_budget": 100,
        "energy_level": 50,
        "subject": "History",
        "topic": "All"
    }
    """
    try:
        data = request.json
        time_budget = data.get('time_budget', 100)
        energy_level = data.get('energy_level', 50)
        subject = data.get('subject', 'All')
        topic = data.get('topic', 'All')
        
        result = golden_path.calculate_optimal_path(
            time_budget_hours=time_budget,
            energy_level=energy_level,
            filter_subject=subject,
            filter_topic=topic
        )
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
