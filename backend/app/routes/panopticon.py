from flask import Blueprint, request, jsonify
from app.services.panopticon_service import panopticon

panopticon_bp = Blueprint('panopticon', __name__)

@panopticon_bp.route('/api/panopticon/log', methods=['POST'])
def log_metrics():
    """Log daily bio-metrics."""
    data = request.json
    if not data or 'date' not in data:
        return jsonify({"success": False, "message": "Date is required"}), 400
        
    result = panopticon.log_daily_metrics(data)
    return jsonify(result)

@panopticon_bp.route('/api/panopticon/dashboard', methods=['GET'])
def get_dashboard():
    """Get data for the Panopticon dashboard."""
    try:
        data = panopticon.get_dashboard_data()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
