from flask import Blueprint, request, jsonify
from app.services.study_planner import generate_study_plan
import datetime

bp = Blueprint('planner', __name__, url_prefix='/api/planner')

@bp.route('/generate', methods=['POST'])
def generate_plan():
    data = request.get_json()
    start_date = data.get('start_date', datetime.date.today().isoformat())
    
    try:
        plan = generate_study_plan(start_date)
        return jsonify({"success": True, "plan": plan})
    except Exception as e:
        import traceback
        return jsonify({"success": False, "error": str(e), "trace": traceback.format_exc()}), 500
