# Answer Writing API Routes
from flask import Blueprint, request, jsonify
from app.db import get_db
from app.services.answer_evaluator import evaluator
import json
from datetime import datetime
from app.services.xp_service import award_xp

answer_writing = Blueprint('answer_writing', __name__)

@answer_writing.route('/api/answer-writing/daily-prompt', methods=['GET'])
def get_daily_prompt():
    """Get today's featured prompt or a random one"""
    try:
        conn = get_db()
        
        # Get a random active prompt
        prompt = conn.execute('''
            SELECT * FROM answer_writing_prompts 
            WHERE is_active = 1 
            ORDER BY RANDOM() 
            LIMIT 1
        ''').fetchone()
        
        if not prompt:
            return jsonify({'error': 'No prompts available'}), 404
        
        return jsonify(dict(prompt))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@answer_writing.route('/api/answer-writing/prompts', methods=['GET'])
def get_prompts():
    """Get prompts with optional filters"""
    try:
        conn = get_db()
        subject = request.args.get('subject')
        difficulty = request.args.get('difficulty')
        word_limit = request.args.get('word_limit')
        
        query = 'SELECT * FROM answer_writing_prompts WHERE is_active = 1'
        params = []
        
        if subject:
            query += ' AND subject = ?'
            params.append(subject)
        
        if difficulty:
            query += ' AND difficulty = ?'
            params.append(difficulty)
        
        if word_limit:
            query += ' AND word_limit = ?'
            params.append(int(word_limit))
        
        query += ' ORDER BY created_at DESC'
        
        prompts = conn.execute(query, params).fetchall()
        
        return jsonify([dict(p) for p in prompts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@answer_writing.route('/api/answer-writing/submit', methods=['POST'])
def submit_answer():
    """Submit an answer and get AI evaluation"""
    try:
        data = request.get_json()
        user_id = 1  # Get from session in production
        prompt_id = data.get('prompt_id')
        answer_text = data.get('answer_text', '').strip()
        time_taken = data.get('time_taken', 0)
        
        if not prompt_id or not answer_text:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get prompt details
        conn = get_db()
        prompt = conn.execute(
            'SELECT * FROM answer_writing_prompts WHERE id = ?',
            (prompt_id,)
        ).fetchone()
        
        if not prompt:
            return jsonify({'error': 'Prompt not found'}), 404
        
        # Calculate word count
        word_count = len(answer_text.split())
        
        # Save answer
        cursor = conn.execute('''
            INSERT INTO user_answers (user_id, prompt_id, answer_text, word_count, time_taken)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, prompt_id, answer_text, word_count, time_taken))
        
        answer_id = cursor.lastrowid
        conn.commit()
        
        # Get AI evaluation
        evaluation_result = evaluator.evaluate_answer(
            question=prompt['question'],
            answer_text=answer_text,
            word_limit=prompt['word_limit'],
            keywords=prompt['keywords'],
            model_answer=prompt['model_answer']
        )
        
        # Save evaluation
        conn.execute('''
            INSERT INTO answer_evaluations 
            (answer_id, overall_score, structure_score, content_score, relevance_score,
             keyword_coverage, strengths, improvements, missing_keywords)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            answer_id,
            evaluation_result['overall_score'],
            evaluation_result['structure_score'],
            evaluation_result['content_score'],
            evaluation_result['relevance_score'],
            evaluation_result['keyword_coverage'],
            json.dumps(evaluation_result['strengths']),
            json.dumps(evaluation_result['improvements']),
            json.dumps(evaluation_result['missing_keywords'])
        ))
        
        conn.commit()
        
        # Award XP
        overall_score = evaluation_result['overall_score']
        xp_earned = 50 + int(overall_score * 10)
        hacksilver_earned = int(overall_score * 5)
        award_xp(user_id, xp_earned, hacksilver_earned)
        
        return jsonify({
            'answer_id': answer_id,
            'evaluation': evaluation_result,
            'xp_earned': xp_earned,
            'hacksilver_earned': hacksilver_earned
        })
        
    except Exception as e:
        print(f"Error in submit_answer: {e}")
        return jsonify({'error': str(e)}), 500

@answer_writing.route('/api/answer-writing/my-answers', methods=['GET'])
def get_my_answers():
    """Get user's submission history"""
    try:
        user_id = 1
        limit = request.args.get('limit', 10, type=int)
        
        conn = get_db()
        answers = conn.execute('''
            SELECT 
                ua.id, ua.prompt_id, ua.answer_text, ua.word_count, ua.time_taken, ua.submitted_at,
                p.question, p.word_limit, p.subject, p.topic,
                ae.overall_score, ae.structure_score, ae.content_score, ae.relevance_score,
                ae.keyword_coverage
            FROM user_answers ua
            JOIN answer_writing_prompts p ON ua.prompt_id = p.id
            LEFT JOIN answer_evaluations ae ON ua.id = ae.answer_id
            WHERE ua.user_id = ?
            ORDER BY ua.submitted_at DESC
            LIMIT ?
        ''', (user_id, limit)).fetchall()
        
        return jsonify([dict(a) for a in answers])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@answer_writing.route('/api/answer-writing/answer/<int:answer_id>', methods=['GET'])
def get_answer_detail(answer_id):
    """Get specific answer with full evaluation"""
    try:
        user_id = 1
        conn = get_db()
        
        answer = conn.execute('''
            SELECT 
                ua.*,
                p.question, p.word_limit, p.subject, p.topic, p.model_answer,
                ae.*
            FROM user_answers ua
            JOIN answer_writing_prompts p ON ua.prompt_id = p.id
            LEFT JOIN answer_evaluations ae ON ua.id = ae.answer_id
            WHERE ua.id = ? AND ua.user_id = ?
        ''', (answer_id, user_id)).fetchone()
        
        if not answer:
            return jsonify({'error': 'Answer not found'}), 404
        
        result = dict(answer)
        
        # Parse JSON fields
        for field in ['strengths', 'improvements', 'missing_keywords']:
            if result.get(field):
                try:
                    result[field] = json.loads(result[field])
                except:
                    result[field] = []
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@answer_writing.route('/api/answer-writing/analytics', methods=['GET'])
def get_analytics():
    """Get performance analytics"""
    try:
        user_id = 1
        conn = get_db()
        
        # Overall stats
        stats = conn.execute('''
            SELECT 
                COUNT(*) as total_answers,
                AVG(ae.overall_score) as avg_score,
                MAX(ae.overall_score) as best_score,
                AVG(ua.word_count) as avg_words,
                AVG(ua.time_taken) as avg_time
            FROM user_answers ua
            LEFT JOIN answer_evaluations ae ON ua.id = ae.answer_id
            WHERE ua.user_id = ?
        ''', (user_id,)).fetchone()
        
        # Subject-wise performance
        by_subject = conn.execute('''
            SELECT 
                p.subject,
                COUNT(*) as count,
                AVG(ae.overall_score) as avg_score
            FROM user_answers ua
            JOIN answer_writing_prompts p ON ua.prompt_id = p.id
            LEFT JOIN answer_evaluations ae ON ua.id = ae.answer_id
            WHERE ua.user_id = ?
            GROUP BY p.subject
        ''', (user_id,)).fetchall()
        
        # Recent trend (last 10 answers)
        recent_scores = conn.execute('''
            SELECT ae.overall_score, ua.submitted_at
            FROM user_answers ua
            LEFT JOIN answer_evaluations ae ON ua.id = ae.answer_id
            WHERE ua.user_id = ?
            ORDER BY ua.submitted_at DESC
            LIMIT 10
        ''', (user_id,)).fetchall()
        
        return jsonify({
            'overall': dict(stats) if stats else {},
            'by_subject': [dict(s) for s in by_subject],
            'recent_trend': [dict(r) for r in recent_scores]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
