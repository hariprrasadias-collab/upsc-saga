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

@bp.route('/tactical-brief', methods=['POST'])
def get_tactical_briefing():
    """
    Receives current contextual tasks from frontend and passes them to the AI War Room.
    """
    try:
        from app.services.war_room_service import WarRoomService
        
        data = request.get_json() or {}
        tasks_context = data.get('context', 'No specific targets designated for today.')
        
        # We mock today_tasks struct since WarRoom expects list of dicts mostly
        # but WarRoom generate_morning_brief uses them as a string representation anyway.
        # So we pass it just as it asks.
        today_tasks_mock = [{"study_tasks": {"subject": "Operation targets:", "topic": tasks_context}}]
        
        war_room = WarRoomService()
        result = war_room.generate_morning_brief(user_id=1, today_tasks=today_tasks_mock)
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        return jsonify({"success": False, "error": str(e), "trace": traceback.format_exc()}), 500

