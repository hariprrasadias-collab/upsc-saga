"""
API Routes for Autonomous Brain Settings and Control
"""
from flask import Blueprint, request, jsonify
import json
from app.services.autonomy_manager import autonomy_manager
from app.services.outcome_tracker import outcome_tracker

autonomy_bp = Blueprint('autonomy_core', __name__)

@autonomy_bp.route('/settings', methods=['GET'])
def get_autonomy_settings():
    """Get current autonomy settings for user"""
    try:
        level = autonomy_manager.get_user_autonomy_level(user_id=1)
        stats = autonomy_manager.get_autonomy_stats(user_id=1)
        
        return jsonify({
            'autonomy_level': level,
            'levels_available': list(autonomy_manager.AUTONOMY_LEVELS.keys()),
            'level_descriptions': {
                k: v['description'] 
                for k, v in autonomy_manager.AUTONOMY_LEVELS.items()
            },
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/settings', methods=['POST'])
def update_autonomy_settings():
    """Update user's autonomy level"""
    try:
        data = request.json
        new_level = data.get('autonomy_level')
        
        if not new_level:
            return jsonify({'error': 'autonomy_level is required'}), 400
        
        autonomy_manager.set_user_autonomy_level(user_id=1, level=new_level)
        
        return jsonify({
            'success': True,
            'message': f'Autonomy level updated to {new_level}',
            'new_level': new_level
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/action_log', methods=['GET'])
def get_action_log():
    """Get recent Brain action history"""
    try:
        from app.db import get_db
        conn = get_db()
        
        limit = request.args.get('limit', 50, type=int)
        
        actions = conn.execute('''
            SELECT id, action_type, action_label, executed_by, executed_at,
                   outcome_status, impact_score, reasoning
            FROM brain_action_log
            WHERE user_id = 1
            ORDER BY executed_at DESC
            LIMIT ?
        ''', (limit,)).fetchall()
        
        return jsonify({
            'actions': [
                {
                    'id': a['id'],
                    'type': a['action_type'],
                    'label': a['action_label'],
                    'executed_by': a['executed_by'],
                    'executed_at': a['executed_at'],
                    'status': a['outcome_status'],
                    'impact_score': a['impact_score'],
                    'reasoning': a['reasoning']
                }
                for a in actions
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/learned_patterns', methods=['GET'])
def get_learned_patterns():
    """Get Brain's learned patterns"""
    try:
        pattern_type = request.args.get('type', None)
        min_confidence = request.args.get('min_confidence', 0.5, type=float)
        
        patterns = outcome_tracker.get_learned_patterns(pattern_type, min_confidence)
        
        return jsonify({
            'patterns': patterns,
            'total_count': len(patterns)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/measure_impact/<int:action_id>', methods=['POST'])
def measure_action_impact(action_id):
    """Manually trigger impact measurement for an action"""
    try:
        impact_score = outcome_tracker.measure_action_impact(action_id)
        
        if impact_score is None:
            return jsonify({'error': 'Action not found'}), 404
        
        return jsonify({
            'success': True,
            'action_id': action_id,
            'impact_score': impact_score,
            'interpretation': (
                'Very helpful' if impact_score > 0.7 else
                'Helpful' if impact_score > 0.3 else
                'Neutral' if impact_score > -0.3 else
                'Not helpful' if impact_score > -0.7 else
                'Harmful'
            )
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/stats/overview', methods=['GET'])
def get_autonomy_overview():
    """Get comprehensive autonomy system overview"""
    try:
        from app.db import get_db
        conn = get_db()
        
        # Basic stats
        stats = autonomy_manager.get_autonomy_stats(user_id=1)
        
        # Pattern counts
        patterns = conn.execute('''
            SELECT pattern_type, COUNT(*) as count,
                   AVG(confidence_score) as avg_confidence
            FROM brain_learning_patterns
            WHERE user_id = 1
            GROUP BY pattern_type
        ''').fetchall()
        
        # Recent performance
        recent_actions = conn.execute('''
            SELECT 
                COUNT(*) as total,
                AVG(impact_score) as avg_impact,
                SUM(CASE WHEN outcome_status = 'success' THEN 1 ELSE 0 END) as successes,
                SUM(CASE WHEN outcome_status = 'failure' THEN 1 ELSE 0 END) as failures
            FROM brain_action_log
            WHERE user_id = 1
            AND executed_at > datetime('now', '-7 days')
        ''').fetchone()
        
        return jsonify({
            'autonomy_stats': stats,
            'learning_patterns': {
                p['pattern_type']: {
                    'count': p['count'],
                    'avg_confidence': round(p['avg_confidence'], 2)
                }
                for p in patterns
            },
            'recent_performance': {
                'total_actions': recent_actions['total'] if recent_actions else 0,
                'avg_impact': round(recent_actions['avg_impact'], 2) if recent_actions and recent_actions['avg_impact'] else 0,
                'success_count': recent_actions['successes'] if recent_actions else 0,
                'failure_count': recent_actions['failures'] if recent_actions else 0
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/mistakes', methods=['GET'])
def get_detected_mistakes():
    """Get detected mistakes and correction loops"""
    try:
        from app.services.mistake_detector import MistakeDetector
        detector = MistakeDetector()
        
        lookback = request.args.get('hours', 24, type=int)
        mistakes = detector.detect_mistakes(lookback_hours=lookback)
        
        return jsonify({
            'mistakes': mistakes,
            'count': len(mistakes)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/blacklist', methods=['POST'])
def blacklist_action_type():
    """Manually blacklist an action type"""
    try:
        from app.services.mistake_detector import MistakeDetector
        detector = MistakeDetector()
        
        data = request.json
        action_type = data.get('action_type')
        reason = data.get('reason', 'Manual blacklist')
        
        if not action_type:
            return jsonify({'error': 'action_type is required'}), 400
            
        entry = detector.blacklist_action(action_type, reason)
        
        return jsonify({
            'success': True,
            'message': f'Action {action_type} blacklisted until {entry.expires_at}',
            'expires_at': entry.expires_at.isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/correct/<int:mistake_action_id>', methods=['POST'])
def trigger_correction(mistake_action_id):
    """Trigger auto-correction for a specific mistake"""
    try:
        from app.services.auto_corrector import auto_corrector
        from app.services.mistake_detector import MistakeDetector
        
        # Re-construct mistake object (simplified)
        # In a real app, we might store mistakes in a DB table
        mistake_type = request.json.get('type', 'execution_failure')
        action_type = request.json.get('action_type', 'UNKNOWN')
        reason = request.json.get('reason', 'Manual trigger')
        
        mistake = {
            'type': mistake_type,
            'action_id': mistake_action_id,
            'action_type': action_type,
            'reason': reason
        }
        
        result = auto_corrector.correct_mistake(mistake)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/scholar/author', methods=['POST'])
def author_micro_book():
    """Trigger The Scholar to write a book"""
    try:
        from app.services.scholar_service import scholar_service
        data = request.json or {}
        topic = data.get('topic')
        subject = data.get('subject', 'General')

        if not topic:
            return jsonify({'error': 'Topic is required'}), 400

        result = scholar_service.generate_micro_book(topic, subject)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/newsroom/sync', methods=['POST'])
def trigger_newsroom():
    """Trigger The Newsroom to update static notes"""
    try:
        from app.services.newsroom_service import newsroom_service
        data = request.json or {}
        news = data.get('news')
        result = newsroom_service.broadcast_updates(news)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/prometheus/forecast', methods=['GET'])
def get_strategic_forecast():
    """Run Project Prometheus Strategy Simulation"""
    try:
        from app.services.prometheus_service import prometheus_service
        result = prometheus_service.run_strategy_simulation()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/evolve', methods=['POST'])
def trigger_evolution():
    """
    Manually trigger Hephaestus to evolve a specific file or the codebase.
    """
    try:
        from app.services.hephaestus_service import hephaestus
        import os
        import random

        data = request.json or {}
        target_file = data.get('target_file')

        if not target_file:
            # Pick a random service to evolve
            services_dir = os.path.join(os.getcwd(), 'backend', 'app', 'services')
            if os.path.exists(services_dir):
                files = [f for f in os.listdir(services_dir) if f.endswith('.py') and f != '__init__.py']
                if files:
                    target_file = os.path.join(services_dir, random.choice(files))

            if not target_file:
                 return jsonify({'error': 'No suitable candidate found for evolution'}), 404
        else:
            # Verify path safety (Simple check)
            if '..' in target_file or not target_file.endswith('.py'):
                return jsonify({'error': 'Invalid file path'}), 400

            # Allow relative paths from root
            if not os.path.isabs(target_file):
                target_file = os.path.join(os.getcwd(), target_file)

        if not os.path.exists(target_file):
            return jsonify({'error': f'File not found: {target_file}'}), 404

        # Trigger in background
        import threading
        def run_evolution():
            hephaestus.evolve_feature(target_file)

        threading.Thread(target=run_evolution).start()

        return jsonify({
            'success': True,
            'message': f'Evolution triggered for {os.path.basename(target_file)}',
            'mode': 'God Mode',
            'target': target_file
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/director/check', methods=['POST'])
def check_director():
    """Trigger The Director to check user velocity"""
    try:
        from app.services.director_service import director_service
        result = director_service.check_user_velocity(user_id=1)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/doppelganger/duel', methods=['POST'])
def trigger_shadow_duel():
    """Trigger a Shadow Duel (Adversarial Quiz)"""
    try:
        from app.services.doppelganger_service import doppelganger_service
        result = doppelganger_service.generate_shadow_duel(user_id=1)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/neural_lace/ingest', methods=['POST'])
def ingest_content():
    """Ingest URL or Text"""
    try:
        from app.services.neural_lace_service import neural_lace
        data = request.json
        result = neural_lace.ingest_content(
            url=data.get('url'),
            text_content=data.get('text'),
            context_tag=data.get('tag', 'General')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/review/now', methods=['POST'])
def trigger_self_review():
    """Trigger an immediate self-review"""
    try:
        from app.services.self_review import self_review_service
        
        lookback = request.json.get('days', 7) if request.json else 7
        result = self_review_service.perform_review(lookback_days=lookback)
        
        return jsonify({
            'success': True,
            'review': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/reviews/latest', methods=['GET'])
def get_latest_review():
    """Get the most recent self-review"""
    try:
        from app.services.self_review import self_review_service
        
        review = self_review_service.get_latest_review()
        
        if not review:
            return jsonify({'message': 'No reviews found'}), 404
            
        # Parse JSON fields
        if review.get('improvement_plan'):
            review['improvement_plan'] = json.loads(review['improvement_plan'])
            
        return jsonify({
            'review': review
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/optimizations', methods=['GET'])
def get_optimizations():
    """Get pending optimization opportunities"""
    try:
        from app.services.optimization_engine import optimization_engine
        
        # Trigger a scan first (in real app, this might be background job)
        optimization_engine.scan_for_optimizations()
        
        opps = optimization_engine.get_pending_optimizations()
        
        # Parse JSON payload
        for o in opps:
            if o['payload']:
                o['payload'] = json.loads(o['payload'])
        
        return jsonify({
            'opportunities': opps,
            'count': len(opps)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/optimizations/<int:opp_id>/accept', methods=['POST'])
def accept_optimization(opp_id):
    """Accept an optimization suggestion"""
    try:
        from app.services.optimization_engine import optimization_engine
        
        result = optimization_engine.accept_optimization(opp_id)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/ab_tests', methods=['POST'])
def create_ab_test():
    """Create a new A/B test"""
    try:
        from app.services.ab_tester import ab_tester
        
        data = request.json
        result = ab_tester.create_test(
            test_name=data.get('test_name'),
            strategy_a=data.get('strategy_a'),
            strategy_b=data.get('strategy_b'),
            duration_days=data.get('duration_days', 7)
        )
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@autonomy_bp.route('/ab_tests/<test_name>', methods=['GET'])
def get_ab_test_results(test_name):
    """Get results of an A/B test"""
    try:
        from app.services.ab_tester import ab_tester
        
        result = ab_tester.get_test_results(test_name)
        
        if not result:
            return jsonify({'error': 'Test not found'}), 404
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
