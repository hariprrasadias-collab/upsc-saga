# Weak Area API Routes
from flask import Blueprint, jsonify, request
from app.services.weak_area_service import weak_area_analyzer

weak_areas_bp = Blueprint('weak_areas', __name__)

@weak_areas_bp.route('/api/weak-areas/analysis', methods=['GET'])
def get_weak_areas():
    """
    Get user's weak areas analysis.
    Optional query param: days (default: 30)
    """
    try:
        user_id = 1  # TODO: Get from session
        days = request.args.get('days', 30, type=int)
        
        weak_areas = weak_area_analyzer.analyze_user_performance(user_id, days)
        
        return jsonify({
            'weak_areas': weak_areas,
            'total_count': len(weak_areas)
        })
    except Exception as e:
        print(f"Error getting weak areas: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@weak_areas_bp.route('/api/weak-areas/practice-set', methods=['POST'])
def generate_practice_set():
    """
    Generate a targeted practice set based on weak areas.
    Body: { num_questions: 10 }
    """
    try:
        user_id = 1  # TODO: Get from session
        data = request.get_json() or {}
        num_questions = data.get('num_questions', 10)
        
        practice_set = weak_area_analyzer.generate_practice_set(user_id, num_questions)
        
        if not practice_set:
            return jsonify({
                'error': 'No weak areas identified yet. Complete more mock tests first.'
            }), 404
        
        return jsonify(practice_set)
    except Exception as e:
        print(f"Error generating practice set: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@weak_areas_bp.route('/api/weak-areas/practice-sets', methods=['GET'])
def get_practice_sets():
    """
    Get user's practice sets.
    Optional query param: completed (true/false)
    """
    try:
        user_id = 1  # TODO: Get from session
        completed_param = request.args.get('completed')
        
        completed = None
        if completed_param is not None:
            completed = completed_param.lower() == 'true'
        
        sets = weak_area_analyzer.get_practice_sets(user_id, completed)
        
        return jsonify({'practice_sets': sets})
    except Exception as e:
        print(f"Error getting practice sets: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@weak_areas_bp.route('/api/weak-areas/practice-set/<int:set_id>/submit', methods=['POST'])
def submit_practice_answer(set_id):
    """
    Submit an answer for a practice set question.
    Body: { question_id: int, is_correct: bool, time_taken: int }
    """
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        is_correct = data.get('is_correct')
        time_taken = data.get('time_taken', 0)
        
        if question_id is None or is_correct is None:
            return jsonify({'error': 'question_id and is_correct are required'}), 400
        
        weak_area_analyzer.submit_practice_result(
            set_id, question_id, is_correct, time_taken
        )
        
        return jsonify({'success': True, 'message': 'Answer recorded'})
    except Exception as e:
        print(f"Error submitting practice answer: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@weak_areas_bp.route('/api/weak-areas/progress', methods=['GET'])
def get_improvement_progress():
    """
    Track improvement in weak areas over time.
    """
    try:
        user_id = 1  # TODO: Get from session
        
        from app.db import get_db
        conn = get_db()
        
        # Get topics that have improved
        improving = conn.execute('''
            SELECT topic, subject, accuracy_rate, trend
            FROM weak_area_analysis
            WHERE user_id = ? AND trend = 'improving'
            ORDER BY accuracy_rate DESC
        ''', (user_id,)).fetchall()
        
        # Get topics still struggling
        struggling = conn.execute('''
            SELECT topic, subject, accuracy_rate, total_attempts
            FROM weak_area_analysis
            WHERE user_id = ? AND accuracy_rate < 60 AND trend != 'improving'
            ORDER BY priority_score DESC
            LIMIT 5
        ''', (user_id,)).fetchall()
        
        return jsonify({
            'improving': [dict(row) for row in improving],
            'still_struggling': [dict(row) for row in struggling]
        })
    except Exception as e:
        print(f"Error getting progress: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
