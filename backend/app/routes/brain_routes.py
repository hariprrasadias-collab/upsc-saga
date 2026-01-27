from flask import Blueprint, request, jsonify
from app.services.brain_service import brain_service
from app.utils.security import rate_limit

brain_bp = Blueprint('brain', __name__)

@brain_bp.route('/directive', methods=['POST'])
def ingest_directive():
    """
    Ingest a Strategic Directive (e.g., Golden Path).
    """
    try:
        data = request.json
        path_data = data.get('path', [])
        
        # from app.services.brain_service import brain_service # Already imported
        brain_service.ingest_strategic_directive(path_data)
        
        return jsonify({"success": True, "message": "Strategic Directive Acknowledged."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@brain_bp.route('/think', methods=['POST'])
@rate_limit(limit=10)
def think():
    """
    Main endpoint for Brain interaction.
    User sends text -> Brain returns thoughts + actions.
    """
    try:
        data = request.json
        user_input = data.get('input', '')
        context = data.get('context', {})

        response = brain_service.think(user_input, context)
        return jsonify(response)
    except Exception as e:
        return jsonify({"response_text": "I am currently offline.", "error": str(e)}), 500

@brain_bp.route('/execute', methods=['POST'])
def execute_action():
    """
    Endpoint to execute a specific action suggested by the Brain.
    """
    try:
        data = request.json
        action_type = data.get('type')
        payload = data.get('payload', {})

        result = brain_service.execute_action(action_type, payload)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@brain_bp.route('/status', methods=['GET'])
def get_status():
    """Check Brain health and connections"""
    try:
        return jsonify(brain_service._get_system_status_summary())
    except Exception as e:
        return jsonify({"status": "DEGRADED", "error": str(e)}), 500

@brain_bp.route('/proactive', methods=['GET'])
def get_proactive_insights():
    """
    Get proactive insights/optimizations for the user.
    Maps OptimizationEngine opportunities to frontend Insight format.
    """
    try:
        from app.services.optimization_engine import optimization_engine
        import json
        
        # Trigger scan
        optimization_engine.scan_for_optimizations()
        opps = optimization_engine.get_pending_optimizations()
        
        insights = []
        for opp in opps:
            # Parse payload if string
            payload = opp['payload']
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except:
                    payload = {}
                
            insights.append({
                'type': opp['type'].replace('_', ' ').title(),
                'priority': 'High', # Default for now
                'message': opp['description'],
                'actions': [{
                    'label': 'Accept',
                    'type': payload.get('action', 'UNKNOWN'),
                    'payload': payload
                }]
            })
            
        return jsonify({'insights': insights})
    except Exception as e:
        return jsonify({'error': str(e), 'insights': []})

@brain_bp.route('/optimize', methods=['POST'])
def trigger_optimization():
    """
    Trigger an immediate optimization scan.
    Returns analysis and actions taken.
    """
    try:
        from app.services.optimization_engine import optimization_engine
        import json
        
        # Trigger scan
        opportunities = optimization_engine.scan_for_optimizations()
        
        # Format response for frontend
        if not opportunities:
            analysis = "I've scanned your schedule, resources, and performance. Everything looks optimal right now! Keep up the good work."
            actions_taken = []
        else:
            analysis = f"I found {len(opportunities)} optimization opportunities to improve your workflow."
            actions_taken = []
            for opp in opportunities:
                payload = opp['payload']
                if isinstance(payload, str):
                    try:
                        payload = json.loads(payload)
                    except:
                        payload = {}
                
                actions_taken.append({
                    'label': opp['description'],
                    'type': payload.get('action', 'SUGGESTION'),
                    'payload': payload
                })
                
        return jsonify({
            'analysis': analysis,
            'actions_taken': actions_taken
        })
    except Exception as e:
        return jsonify({
            'analysis': f"Optimization failed: {str(e)}",
            'actions_taken': []
        })
