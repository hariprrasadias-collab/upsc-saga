"""
Predictive Analytics Routes
Exposes predictive analytics endpoints
"""
from flask import Blueprint, jsonify, request
from app.services.predictive_analytics import (
    calculate_exam_readiness,
    calculate_success_probability,
    calculate_optimal_study_time,
    detect_burnout
)

predictive_bp = Blueprint('predictive', __name__)

@predictive_bp.route('/api/analytics/predictive/exam-readiness', methods=['GET'])
def get_exam_readiness():
    try:
        result = calculate_exam_readiness()
        return jsonify(result)
    except Exception as e:
        print(f"Error calculating exam readiness: {e}")
        return jsonify({'error': str(e)}), 500

@predictive_bp.route('/api/analytics/predictive/success-probability', methods=['GET'])
def get_success_probability():
    try:
        result = calculate_success_probability()
        return jsonify(result)
    except Exception as e:
        print(f"Error calculating success probability: {e}")
        return jsonify({'error': str(e)}), 500

@predictive_bp.route('/api/analytics/predictive/optimal-study-time', methods=['GET'])
def get_optimal_study_time():
    try:
        result = calculate_optimal_study_time()
        return jsonify(result)
    except Exception as e:
        print(f"Error calculating optimal study time: {e}")
        return jsonify({'error': str(e)}), 500

@predictive_bp.route('/api/analytics/predictive/burnout-detection', methods=['GET'])
def get_burnout_detection():
    try:
        result = detect_burnout()
        return jsonify(result)
    except Exception as e:
        print(f"Error detecting burnout: {e}")
        return jsonify({'error': str(e)}), 500

@predictive_bp.route('/api/analytics/predictive/all', methods=['GET'])
def get_all_predictive_analytics():
    """Get all predictive analytics in one call"""
    try:
        result = {
            'exam_readiness': calculate_exam_readiness(),
            'success_probability': calculate_success_probability(),
            'optimal_study_time': calculate_optimal_study_time(),
            'burnout_detection': detect_burnout()
        }
        return jsonify(result)
    except Exception as e:
        print(f"Error calculating predictive analytics: {e}")
        return jsonify({'error': str(e)}), 500

@predictive_bp.route('/api/analytics/predictive/simulate-outcome', methods=['GET'])
def simulate_exam():
    """Run Monte Carlo simulation for Prelims"""
    try:
        from app.services.foresight_engine import foresight_engine
        result = foresight_engine.simulate_exam_outcome(user_id=1)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Enhanced Visualizations Endpoints
from app.services.visualizations import (
    get_daily_activity_heatmap,
    get_revision_curve_data,
    get_topic_connections
)

@predictive_bp.route('/api/analytics/visualizations/heatmap', methods=['GET'])
def get_activity_heatmap():
    """Get daily activity heatmap data"""
    try:
        days = request.args.get('days', 365, type=int)
        result = get_daily_activity_heatmap(days)
        return jsonify(result)
    except Exception as e:
        print(f"Error getting heatmap data: {e}")
        return jsonify({'error': str(e)}), 500

@predictive_bp.route('/api/analytics/visualizations/revision-curve', methods=['GET'])
def get_revision_curve():
    """Get revision effectiveness curve data"""
    try:
        deck_id = request.args.get('deck_id', None, type=int)
        result = get_revision_curve_data(deck_id)
        return jsonify(result)
    except Exception as e:
        print(f"Error getting revision curve: {e}")
        return jsonify({'error': str(e)}), 500

@predictive_bp.route('/api/analytics/visualizations/knowledge-graph', methods=['GET'])
def get_knowledge_graph():
    """Get topic connections for knowledge graph"""
    try:
        result = get_topic_connections()
        return jsonify(result)
    except Exception as e:
        print(f"Error getting knowledge graph: {e}")
        return jsonify({'error': str(e)}), 500
