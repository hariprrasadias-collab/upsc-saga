# Mock Tests API Routes
from flask import Blueprint, request, jsonify
from app.db import get_db
from datetime import datetime
import json
from app.services.xp_service import award_xp

mock_tests = Blueprint('mock_tests', __name__)

@mock_tests.route('/api/mock-tests', methods=['GET'])
def get_tests():
    """Get all available tests with optional filters"""
    try:
        conn = get_db()
        test_type = request.args.get('test_type')
        difficulty = request.args.get('difficulty')
        
        query = 'SELECT * FROM mock_tests WHERE is_active = 1'
        params = []
        
        if test_type:
            query += ' AND test_type = ?'
            params.append(test_type)
        
        if difficulty:
            query += ' AND difficulty = ?'
            params.append(difficulty)
        
        query += ' ORDER BY created_at DESC'
        
        tests = conn.execute(query, params).fetchall()
        
        return jsonify([dict(t) for t in tests])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mock_tests.route('/api/mock-tests', methods=['POST'])
def create_test():
    """Create a new mock test manually"""
    try:
        data = request.get_json()
        title = data.get('title')
        subject = data.get('subject', 'General')
        description = data.get('description', '')
        difficulty = data.get('difficulty', 'Medium')
        questions = data.get('questions', [])
        
        if not title or not questions:
            return jsonify({'error': 'Title and questions are required'}), 400
            
        conn = get_db()
        
        # Create Test
        cursor = conn.execute('''
            INSERT INTO mock_tests (title, subject, description, total_questions, duration_minutes, difficulty, is_active, test_type, total_marks)
            VALUES (?, ?, ?, ?, ?, ?, 1, 'MOCK', ?)
        ''', (title, subject, description, len(questions), len(questions)*2, difficulty, len(questions)*2)) # Approx 2 min per question, 2 marks per question
        test_id = cursor.lastrowid
        
        # Add Questions
        for i, q in enumerate(questions, 1):
            conn.execute('''
                INSERT INTO test_questions 
                (test_id, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, subject, topic, marks)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                test_id, 
                i, 
                q['question_text'], 
                q['option_a'], q['option_b'], q['option_c'], q['option_d'], 
                q['correct_answer'], 
                q.get('explanation', ''), 
                q.get('subject', subject), 
                q.get('topic', ''),
                q.get('marks', 2.0)
            ))
            
        conn.commit()
        return jsonify({'success': True, 'test_id': test_id, 'message': 'Test created successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mock_tests.route('/api/mock-tests/<int:test_id>', methods=['GET'])
def get_test_details(test_id):
    """Get test details without revealing answers"""
    try:
        conn = get_db()
        
        test = conn.execute(
            'SELECT * FROM mock_tests WHERE id = ? AND is_active =1',
            (test_id,)
        ).fetchone()
        
        if not test:
            return jsonify({'error': 'Test not found'}), 404
        
        # Get questions without correct answers
        questions = conn.execute('''
            SELECT id, question_number, question_text, option_a, option_b, option_c, option_d, subject, topic
            FROM test_questions
            WHERE test_id = ?
            ORDER BY question_number
        ''', (test_id,)).fetchall()
        
        return jsonify({
            'test': dict(test),
            'questions': [dict(q) for q in questions]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mock_tests.route('/api/mock-tests/<int:test_id>/start', methods=['POST'])
def start_test(test_id):
    """Start a new test attempt"""
    try:
        user_id = 1  # Get from session in production
        conn = get_db()
        
        # Create attempt
        cursor = conn.execute('''
            INSERT INTO test_attempts (user_id, test_id, status)
            VALUES (?, ?, 'in_progress')
        ''', (user_id, test_id))
        
        attempt_id = cursor.lastrowid
        conn.commit()
        
        # Get test and questions
        test = conn.execute('SELECT * FROM mock_tests WHERE id = ?', (test_id,)).fetchone()
        questions = conn.execute('''
            SELECT id, question_number, question_text, option_a, option_b, option_c, option_d, subject, topic
            FROM test_questions
            WHERE test_id = ?
            ORDER BY question_number
        ''', (test_id,)).fetchall()
        
        return jsonify({
            'attempt_id': attempt_id,
            'test': dict(test),
            'questions': [dict(q) for q in questions]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mock_tests.route('/api/mock-tests/attempt/<int:attempt_id>', methods=['GET'])
def get_attempt_state(attempt_id):
    """Get current attempt state with saved answers"""
    try:
        user_id = 1
        conn = get_db()
        
        attempt = conn.execute('''
            SELECT * FROM test_attempts
            WHERE id = ? AND user_id = ?
        ''', (attempt_id, user_id)).fetchone()
        
        if not attempt:
            return jsonify({'error': 'Attempt not found'}), 404
        
        # Get saved answers
        answers = conn.execute('''
            SELECT question_id, selected_answer, is_marked
            FROM test_answers
            WHERE attempt_id = ?
        ''', (attempt_id,)).fetchall()
        
        return jsonify({
            'attempt': dict(attempt),
            'answers': [dict(a) for a in answers]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mock_tests.route('/api/mock-tests/attempt/<int:attempt_id>/answer', methods=['PUT'])
def save_answer(attempt_id):
    """Save or update answer for a question"""
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        selected_answer = data.get('selected_answer')  # 'A', 'B', 'C', 'D', or None
        is_marked = data.get('is_marked', False)
        
        conn = get_db()
        
        # Check if answer already exists
        existing = conn.execute('''
            SELECT id FROM test_answers
            WHERE attempt_id = ? AND question_id = ?
        ''', (attempt_id, question_id)).fetchone()
        
        if existing:
            # Update
            conn.execute('''
                UPDATE test_answers
                SET selected_answer = ?, is_marked = ?
                WHERE attempt_id = ? AND question_id = ?
            ''', (selected_answer, is_marked, attempt_id, question_id))
        else:
            # Insert
            conn.execute('''
                INSERT INTO test_answers (attempt_id, question_id, selected_answer, is_marked)
                VALUES (?, ?, ?, ?)
            ''', (attempt_id, question_id, selected_answer, is_marked))
        
        conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mock_tests.route('/api/mock-tests/attempt/<int:attempt_id>/submit', methods=['POST'])
def submit_test(attempt_id):
    """Submit test and calculate results"""
    try:
        user_id = 1
        conn = get_db()
        
        # Get attempt and test details
        attempt = conn.execute('''
            SELECT at.*, mt.negative_marking
            FROM test_attempts at
            JOIN mock_tests mt ON at.test_id = mt.id
            WHERE at.id = ? AND at.user_id = ?
        ''', (attempt_id, user_id)).fetchone()
        
        if not attempt:
            return jsonify({'error': 'Attempt not found'}), 404
        
        if attempt['status'] == 'completed':
            return jsonify({'error': 'Test already submitted'}), 400
        
        test_id = attempt['test_id']
        negative_marking = attempt['negative_marking']
        
        # Get all questions with correct answers
        questions = conn.execute('''
            SELECT id, correct_answer, marks
            FROM test_questions
            WHERE test_id = ?
        ''', (test_id,)).fetchall()
        
        # Get user's answers
        user_answers = conn.execute('''
            SELECT question_id, selected_answer
            FROM test_answers
            WHERE attempt_id = ?
        ''', (attempt_id,)).fetchall()
        
        answer_dict = {a['question_id']: a['selected_answer'] for a in user_answers}
        
        # Calculate scores
        total_correct = 0
        total_incorrect = 0
        total_unattempted = 0
        score = 0.0
        
        for q in questions:
            qid = q['id']
            correct_ans = q['correct_answer']
            marks = q['marks']
            
            if qid not in answer_dict or answer_dict[qid] is None:
                total_unattempted += 1
            elif answer_dict[qid] == correct_ans:
                total_correct += 1
                score += marks
                # Update is_correct in test_answers
                conn.execute('''
                    UPDATE test_answers SET is_correct = 1
                    WHERE attempt_id = ? AND question_id = ?
                ''', (attempt_id, qid))
            else:
                total_incorrect += 1
                score -= (marks * negative_marking)
                conn.execute('''
                    UPDATE test_answers SET is_correct = 0
                    WHERE attempt_id = ? AND question_id = ?
                ''', (attempt_id, qid))
        
        total_questions = len(questions)
        total_attempted = total_correct + total_incorrect
        max_score = sum(q['marks'] for q in questions)
        percentage = (score / max_score * 100) if max_score > 0 else 0
        
        # Calculate time taken
        started_at = datetime.fromisoformat(attempt['started_at'])
        time_taken = int((datetime.now() - started_at).total_seconds())
        
        # Update attempt
        conn.execute('''
            UPDATE test_attempts
            SET submitted_at = CURRENT_TIMESTAMP,
            time_taken = ?,
            total_attempted = ?,
            total_correct = ?,
            total_incorrect = ?,
            total_unattempted = ?,
            score = ?,
            percentage = ?,
            status = 'completed'
            WHERE id = ?
        ''', (time_taken, total_attempted, total_correct, total_incorrect,
              total_unattempted, score, percentage, attempt_id))
        
        conn.commit()
        
        # Award XP and Hacksilver
        xp_earned = max(0, int(score * 2))
        hacksilver_earned = max(0, int(score))
        award_xp(user_id, xp_earned, hacksilver_earned)
        
        return jsonify({
            'score': round(score, 2),
            'max_score': max_score,
            'percentage': round(percentage, 2),
            'correct': total_correct,
            'incorrect': total_incorrect,
            'unattempted': total_unattempted,
            'attempted': total_attempted,
            'total_questions': total_questions,
            'time_taken': time_taken,
            'accuracy': round((total_correct / total_attempted * 100) if total_attempted > 0 else 0, 2),
            'xp_earned': xp_earned,
            'hacksilver_earned': hacksilver_earned
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mock_tests.route('/api/mock-tests/attempt/<int:attempt_id>/results', methods=['GET'])
def get_results(attempt_id):
    """Get detailed results with question-wise breakdown"""
    try:
        user_id = 1
        conn = get_db()
        
        # Get attempt summary
        attempt = conn.execute('''
            SELECT at.*, mt.title as test_title
            FROM test_attempts at
            JOIN mock_tests mt ON at.test_id = mt.id
            WHERE at.id = ? AND at.user_id = ?
        ''', (attempt_id, user_id)).fetchone()
        
        if not attempt:
            return jsonify({'error': 'Attempt not found'}), 404
        
        # Get question-wise results
        results = conn.execute('''
            SELECT 
                tq.question_number, tq.question_text, tq.option_a, tq.option_b, tq.option_c, tq.option_d,
                tq.correct_answer, tq.explanation, tq.subject, tq.topic,
                ta.selected_answer, ta.is_correct
            FROM test_questions tq
            LEFT JOIN test_answers ta ON tq.id = ta.question_id AND ta.attempt_id = ?
            WHERE tq.test_id = ?
            ORDER BY tq.question_number
        ''', (attempt_id, attempt['test_id'])).fetchall()
        
        # Subject-wise performance
        subject_stats = conn.execute('''
            SELECT 
                tq.subject,
                COUNT(*) as total,
                SUM(CASE WHEN ta.is_correct = 1 THEN 1 ELSE 0 END) as correct
            FROM test_questions tq
            LEFT JOIN test_answers ta ON tq.id = ta.question_id AND ta.attempt_id = ?
            WHERE tq.test_id = ?
            GROUP BY tq.subject
        ''', (attempt_id, attempt['test_id'])).fetchall()
        
        return jsonify({
            'attempt': dict(attempt),
            'questions': [dict(r) for r in results],
            'subject_stats': [dict(s) for s in subject_stats]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mock_tests.route('/api/mock-tests/my-attempts', methods=['GET'])
def get_my_attempts():
    """Get user's test history"""
    try:
        user_id = 1
        limit = request.args.get('limit', 10, type=int)
        
        conn = get_db()
        
        attempts = conn.execute('''
            SELECT 
                at.*,
                mt.title as test_title,
                mt.total_questions
            FROM test_attempts at
            JOIN mock_tests mt ON at.test_id = mt.id
            WHERE at.user_id = ?
            ORDER BY at.started_at DESC
            LIMIT ?
        ''', (user_id, limit)).fetchall()
        
        return jsonify([dict(a) for a in attempts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mock_tests.route('/api/mock-tests/analytics', methods=['GET'])
def get_analytics():
    """Get overall performance analytics"""
    try:
        user_id = 1
        conn = get_db()
        
        # Overall stats
        stats = conn.execute('''
            SELECT 
                COUNT(*) as total_attempts,
                AVG(score) as avg_score,
                MAX(score) as best_score,
                AVG(percentage) as avg_percentage,
                AVG(time_taken) as avg_time
            FROM test_attempts
            WHERE user_id = ? AND status = 'completed'
        ''', (user_id,)).fetchone()
        
        return jsonify(dict(stats) if stats else {})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
