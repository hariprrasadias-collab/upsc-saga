from flask import Blueprint, request, jsonify
from app.services.mock_test_service import MockTestService
from app.db import get_db

mock_tests_bp = Blueprint('mock_tests', __name__)

@mock_tests_bp.route('/api/mock-tests/context', methods=['GET'])
def get_context():
    """Get brain context for mock tests"""
    try:
        return jsonify(MockTestService.get_brain_context())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mock_tests_bp.route('/api/mock-tests/generate', methods=['POST'])
def generate_test():
    """Generate a new AI mock test"""
    try:
        data = request.json
        topic = data.get('topic', 'General Studies')
        count = data.get('count', 10)
        
        result = MockTestService.generate_from_topic(topic, count)
        if result.get('success'):
            return jsonify(result), 201
        else:
            return jsonify(result), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@mock_tests_bp.route('/api/mock-tests', methods=['GET'])
def get_tests():
    """Get all mock tests"""
    try:
        conn = get_db()
        tests = conn.execute('SELECT * FROM mock_tests ORDER BY created_at DESC').fetchall()
        return jsonify([dict(t) for t in tests])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mock_tests_bp.route('/api/mock-tests/<int:test_id>', methods=['GET'])
def get_test(test_id):
    """Get specific test with questions"""
    try:
        conn = get_db()
        test = conn.execute('SELECT * FROM mock_tests WHERE id = ?', (test_id,)).fetchone()
        if not test:
            return jsonify({'error': 'Test not found'}), 404
            
        questions = conn.execute('SELECT * FROM test_questions WHERE test_id = ? ORDER BY question_number', (test_id,)).fetchall()
        
        return jsonify({
            'test': dict(test),
            'questions': [dict(q) for q in questions]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mock_tests_bp.route('/api/mock-tests/<int:test_id>/submit', methods=['POST'])
def submit_test(test_id):
    """Submit test attempt"""
    try:
        data = request.json
        answers = data.get('answers', {}) # map of question_id -> option char
        
        conn = get_db()
        
        # Calculate score
        questions = conn.execute('SELECT id, correct_answer FROM test_questions WHERE test_id = ?', (test_id,)).fetchall()
        total = len(questions)
        correct = 0
        
        for q in questions:
            q_id = str(q['id'])
            if q_id in answers and answers[q_id].upper() == q['correct_answer'].upper():
                correct += 1

        score = correct * 2 # 2 marks per q
        percentage = (correct / total) * 100 if total > 0 else 0
        
        # Save attempt
        conn.execute('''
            INSERT INTO test_attempts (user_id, test_id, score, percentage, answers, status)
            VALUES (?, ?, ?, ?, ?, 'completed')
        ''', (1, test_id, score, percentage, import_json().dumps(answers)))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'score': score,
            'total': total * 2,
            'correct': correct,
            'percentage': percentage
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def import_json():
    import json
    return json
