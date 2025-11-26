from flask import Blueprint, jsonify, request
from app.services.weak_area_analyzer import (
    record_attempt,
    analyze_all_performance,
    get_weak_areas,
    get_dashboard_stats,
    generate_practice_set,
    track_improvement
)

bp = Blueprint('weak_areas', __name__, url_prefix='/api/weak-areas')

@bp.route('/record', methods=['POST'])
def record_question_attempt():
    """Record a question attempt for performance tracking"""
    data = request.get_json()
    
    question_id = data.get('question_id')
    topic = data.get('topic')
    subject = data.get('subject')
    is_correct = data.get('is_correct')
    time_taken = data.get('time_taken', 0)
    
    if not all([question_id, topic, subject, is_correct is not None]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    try:
        record_attempt(question_id, topic, subject, is_correct, time_taken)
        
        return jsonify({
            'success': True,
            'message': 'Attempt recorded successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/analyze', methods=['GET'])
def analyze():
    """Trigger analysis and return weak areas"""
    try:
        weak_areas = analyze_all_performance()
        
        return jsonify({
            'success': True,
            'weak_areas': weak_areas,
            'count': len(weak_areas)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/dashboard', methods=['GET'])
def dashboard():
    """Get statistics for weak areas dashboard"""
    try:
        stats = get_dashboard_stats()
        weak_areas = get_weak_areas(limit=10)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'weak_areas': weak_areas
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/practice', methods=['POST'])
def generate_practice():
    """Generate practice set for weak areas"""
    data = request.get_json()
    count = data.get('count', 10)
    
    try:
        # Get weak topics
        weak_areas = get_weak_areas(limit=5)
        weak_topics = [area['topic'] for area in weak_areas if area['topic']]
        
        if not weak_topics:
            return jsonify({
                'success': False,
                'error': 'No weak areas found. Complete some quizzes first!'
            }), 404
        
        questions = generate_practice_set(weak_topics, count)
        
        return jsonify({
            'success': True,
            'questions': questions,
            'weak_topics': weak_topics,
            'count': len(questions)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/progress/<topic>', methods=['GET'])
def topic_progress(topic):
    """Track improvement for a specific topic"""
    days = request.args.get('days', default=30, type=int)
    
    try:
        timeline = track_improvement(topic, days)
        
        return jsonify({
            'success': True,
            'topic': topic,
            'timeline': timeline,
            'days': days
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
