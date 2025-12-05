from flask import Blueprint, request, jsonify, current_app
import threading
from app.services.study_planner import generate_study_plan, get_plan_for_range, check_and_reschedule_pending
from app.db_models.study_plan import update_task_status, get_task_by_id
from app.services.brain_service import brain_service

study_plan_bp = Blueprint('study_plan', __name__)

@study_plan_bp.route('/api/planner/generate', methods=['POST'])
def generate():
    data = request.get_json()
    start_date = data.get('start_date')
    force_new = data.get('force_new', False)
    
    if not start_date:
        return jsonify({"error": "Start date required"}), 400
        
    result = generate_study_plan(start_date, force_new=force_new)
    return jsonify(result)

@study_plan_bp.route('/api/planner/current', methods=['GET'])
def get_current_plan():
    start_date = request.args.get('start_date')
    days = int(request.args.get('days', 30))
    
    if not start_date:
        return jsonify({"error": "Start date required"}), 400
        
    plan = get_plan_for_range(start_date, days)
    return jsonify({"success": True, "plan": plan})

@study_plan_bp.route('/api/planner/reschedule-check', methods=['POST'])
def reschedule_check():
    result = check_and_reschedule_pending()
    return jsonify(result)

@study_plan_bp.route('/api/planner/task/<int:task_id>/status', methods=['PUT'])
def update_status(task_id):
    data = request.get_json()
    status = data.get('status')
    if not status:
        return jsonify({"error": "Status required"}), 400
        
    # Trigger Brain if task is completed
    if status == 'Completed':
        task = get_task_by_id(task_id)
        if task:
            # Capture app context for the thread
            app = current_app._get_current_object()
            def run_in_context(app, task_data):
                with app.app_context():
                    brain_service.process_task_completion(task_data)

            thread = threading.Thread(target=run_in_context, args=(app, task))
            thread.start()

    update_task_status(task_id, status)
    return jsonify({"success": True})
