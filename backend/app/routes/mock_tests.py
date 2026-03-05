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
            INSERT INTO test_attempts (user_id, test_id, score, percentage, status)
            VALUES (?, ?, ?, ?, 'completed')
        ''', (1, test_id, score, percentage))
        
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

@mock_tests_bp.route('/api/mock-tests/<int:test_id>/start', methods=['POST'])
def start_test(test_id):
    """Start a new test attempt - creates attempt record and returns questions"""
    try:
        conn = get_db()
        
        # Verify test exists
        test = conn.execute('SELECT * FROM mock_tests WHERE id = ?', (test_id,)).fetchone()
        if not test:
            return jsonify({'error': 'Test not found'}), 404
        
        # Get questions
        questions = conn.execute(
            'SELECT * FROM test_questions WHERE test_id = ? ORDER BY question_number',
            (test_id,)
        ).fetchall()
        
        if not questions:
            return jsonify({'error': 'No questions found for this test'}), 404
        
        # Create a new attempt
        cursor = conn.execute('''
            INSERT INTO test_attempts (user_id, test_id, status)
            VALUES (?, ?, 'in_progress')
        ''', (1, test_id))
        conn.commit()
        attempt_id = cursor.lastrowid
        
        return jsonify({
            'attempt_id': attempt_id,
            'questions': [dict(q) for q in questions]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mock_tests_bp.route('/api/mock-tests/attempt/<int:attempt_id>/answer', methods=['PUT'])
def save_answer(attempt_id):
    """Save/update a single answer for an in-progress attempt"""
    try:
        data = request.json
        question_id = data['question_id']
        selected_answer = data.get('selected_answer')
        is_marked = data.get('is_marked', False)
        
        conn = get_db()
        
        # Upsert — check if answer exists
        existing = conn.execute(
            'SELECT id FROM test_answers WHERE attempt_id = ? AND question_id = ?',
            (attempt_id, question_id)
        ).fetchone()
        
        if existing:
            conn.execute('''
                UPDATE test_answers 
                SET selected_answer = ?, is_marked = ?
                WHERE attempt_id = ? AND question_id = ?
            ''', (selected_answer, is_marked, attempt_id, question_id))
        else:
            conn.execute('''
                INSERT INTO test_answers (attempt_id, question_id, selected_answer, is_marked)
                VALUES (?, ?, ?, ?)
            ''', (attempt_id, question_id, selected_answer, is_marked))
        
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mock_tests_bp.route('/api/mock-tests/attempt/<int:attempt_id>/submit', methods=['POST'])
def submit_attempt(attempt_id):
    """Grade and finalize an attempt"""
    try:
        conn = get_db()
        
        # Get the attempt
        attempt = conn.execute('SELECT * FROM test_attempts WHERE id = ?', (attempt_id,)).fetchone()
        if not attempt:
            return jsonify({'error': 'Attempt not found'}), 404
        
        test_id = attempt['test_id']
        
        # Get all questions for this test
        questions = conn.execute(
            'SELECT id, correct_answer, marks FROM test_questions WHERE test_id = ?',
            (test_id,)
        ).fetchall()
        
        # Get submitted answers
        answers = conn.execute(
            'SELECT question_id, selected_answer FROM test_answers WHERE attempt_id = ?',
            (attempt_id,)
        ).fetchall()
        answer_map = {a['question_id']: a['selected_answer'] for a in answers}
        
        total = len(questions)
        correct = 0
        incorrect = 0
        unattempted = 0
        
        for q in questions:
            selected = answer_map.get(q['id'])
            if not selected:
                unattempted += 1
            elif selected.upper() == q['correct_answer'].upper():
                correct += 1
                # Mark answer as correct
                conn.execute(
                    'UPDATE test_answers SET is_correct = 1 WHERE attempt_id = ? AND question_id = ?',
                    (attempt_id, q['id'])
                )
            else:
                incorrect += 1
                conn.execute(
                    'UPDATE test_answers SET is_correct = 0 WHERE attempt_id = ? AND question_id = ?',
                    (attempt_id, q['id'])
                )
        
        marks_per_q = 2.0
        negative_mark = 0.66  # 1/3 negative marking
        score = (correct * marks_per_q) - (incorrect * negative_mark)
        max_score = total * marks_per_q
        percentage = (score / max_score) * 100 if max_score > 0 else 0
        accuracy = (correct / (correct + incorrect)) * 100 if (correct + incorrect) > 0 else 0
        
        # Update attempt record
        conn.execute('''
            UPDATE test_attempts 
            SET status = 'completed',
                submitted_at = CURRENT_TIMESTAMP,
                total_attempted = ?,
                total_correct = ?,
                total_incorrect = ?,
                total_unattempted = ?,
                score = ?,
                percentage = ?
            WHERE id = ?
        ''', (correct + incorrect, correct, incorrect, unattempted, score, percentage, attempt_id))
        conn.commit()
        
        return jsonify({
            'success': True,
            'score': round(score, 2),
            'max_score': max_score,
            'correct': correct,
            'incorrect': incorrect,
            'unattempted': unattempted,
            'percentage': round(percentage, 1),
            'accuracy': round(accuracy, 1)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mock_tests_bp.route('/api/mock-tests/attempt/<int:attempt_id>/results', methods=['GET'])
def get_attempt_results(attempt_id):
    """Get detailed results for a completed attempt"""
    try:
        conn = get_db()
        
        attempt = conn.execute('SELECT * FROM test_attempts WHERE id = ?', (attempt_id,)).fetchone()
        if not attempt:
            return jsonify({'error': 'Attempt not found'}), 404
        
        test_id = attempt['test_id']
        
        # Get questions with answers
        questions = conn.execute('''
            SELECT tq.*, ta.selected_answer, ta.is_correct, ta.is_marked
            FROM test_questions tq
            LEFT JOIN test_answers ta ON tq.id = ta.question_id AND ta.attempt_id = ?
            WHERE tq.test_id = ?
            ORDER BY tq.question_number
        ''', (attempt_id, test_id)).fetchall()
        
        # Subject-wise stats
        subject_map = {}
        for q in questions:
            subj = q['subject'] or 'General'
            if subj not in subject_map:
                subject_map[subj] = {'subject': subj, 'total': 0, 'correct': 0, 'incorrect': 0}
            subject_map[subj]['total'] += 1
            if q['is_correct']:
                subject_map[subj]['correct'] += 1
            elif q['selected_answer']:
                subject_map[subj]['incorrect'] += 1
        
        return jsonify({
            'score': attempt['score'],
            'max_score': attempt['total_correct'] + attempt['total_incorrect'] + attempt['total_unattempted'],
            'percentage': attempt['percentage'],
            'correct': attempt['total_correct'],
            'incorrect': attempt['total_incorrect'],
            'unattempted': attempt['total_unattempted'],
            'accuracy': round((attempt['total_correct'] / max(1, attempt['total_correct'] + attempt['total_incorrect'])) * 100, 1),
            'subject_stats': list(subject_map.values()),
            'questions': [dict(q) for q in questions]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mock_tests_bp.route('/api/mock-tests/<int:test_id>', methods=['DELETE'])
def delete_test(test_id):
    """Delete a test and its questions"""
    try:
        conn = get_db()
        conn.execute('DELETE FROM test_questions WHERE test_id = ?', (test_id,))
        conn.execute('DELETE FROM test_attempts WHERE test_id = ?', (test_id,))
        conn.execute('DELETE FROM mock_tests WHERE id = ?', (test_id,))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mock_tests_bp.route('/api/mock-tests', methods=['POST'])
def create_test():
    """Create a new test with questions"""
    import json as json_mod
    try:
        data = request.json
        conn = get_db()
        
        questions = data.get('questions', [])
        
        cursor = conn.execute('''
            INSERT INTO mock_tests (title, subject, description, difficulty, total_questions, duration_minutes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['title'],
            data.get('subject', 'General'),
            data.get('description', ''),
            data.get('difficulty', 'Medium'),
            len(questions),
            data.get('duration_minutes', max(len(questions) * 2, 30))
        ))
        test_id = cursor.lastrowid
        
        for i, q in enumerate(questions, 1):
            conn.execute('''
                INSERT INTO test_questions (test_id, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, subject)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                test_id, i,
                q['question_text'],
                q.get('option_a', ''),
                q.get('option_b', ''),
                q.get('option_c', ''),
                q.get('option_d', ''),
                q.get('correct_answer', 'A'),
                q.get('explanation', ''),
                q.get('subject', data.get('subject', 'General'))
            ))
        
        conn.commit()
        return jsonify({'success': True, 'test_id': test_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
