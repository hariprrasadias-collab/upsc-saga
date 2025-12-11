from flask import Blueprint, jsonify, request
import sqlite3
import os
import json
from app.services.model_manager import model_manager

bp = Blueprint('model_answers', __name__, url_prefix='/api/model-answers')

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'upsc_saga.db')
# Config managed by ModelManager

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@bp.route('', methods=['POST'])
def create_model_answer():
    """Create a new model answer"""
    data = request.json
    
    required_fields = ['title', 'question_text', 'answer_text']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'{field} is required'}), 400
    
    # Calculate word count
    word_count = len(data['answer_text'].split())
    
    # Convert tags to JSON string
    tags = json.dumps(data.get('tags', []))
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO model_answers 
        (question_id, title, question_text, answer_text, word_count, score, year, paper, tags, question_type, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('question_id'),
        data['title'],
        data['question_text'],
        data['answer_text'],
        word_count,
        data.get('score'),
        data.get('year'),
        data.get('paper'),
        tags,
        data.get('question_type'),
        data.get('source', 'custom')
    ))
    
    answer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'id': answer_id,
        'message': 'Model answer created successfully'
    })

@bp.route('', methods=['GET'])
def get_model_answers():
    """Get all model answers with optional filters"""
    paper = request.args.get('paper')
    question_type = request.args.get('type')
    year = request.args.get('year', type=int)
    min_score = request.args.get('min_score', type=int)
    tag = request.args.get('tag')
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM model_answers WHERE 1=1"
    params = []
    
    if paper:
        query += " AND paper = ?"
        params.append(paper)
    
    if question_type:
        query += " AND question_type = ?"
        params.append(question_type)
    
    if year:
        query += " AND year = ?"
        params.append(year)
    
    if min_score:
        query += " AND score >= ?"
        params.append(min_score)
    
    if tag:
        query += " AND tags LIKE ?"
        params.append(f'%{tag}%')
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    answers = cursor.fetchall()
    
    # Get total count
    count_query = "SELECT COUNT(*) as total FROM model_answers WHERE 1=1"
    cursor.execute(count_query)
    total = cursor.fetchone()['total']
    
    conn.close()
    
    result = []
    for answer in answers:
        answer_dict = dict(answer)
        answer_dict['tags'] = json.loads(answer_dict['tags']) if answer_dict['tags'] else []
        result.append(answer_dict)
    
    return jsonify({
        'success': True,
        'answers': result,
        'total': total,
        'limit': limit,
        'offset': offset
    })

@bp.route('/<int:answer_id>', methods=['GET'])
def get_model_answer(answer_id):
    """Get a specific model answer"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM model_answers WHERE id = ?', (answer_id,))
    answer = cursor.fetchone()
    conn.close()
    
    if not answer:
        return jsonify({'success': False, 'error': 'Answer not found'}), 404
    
    answer_dict = dict(answer)
    answer_dict['tags'] = json.loads(answer_dict['tags']) if answer_dict['tags'] else []
    
    return jsonify({
        'success': True,
        'answer': answer_dict
    })

@bp.route('/<int:answer_id>', methods=['PUT'])
def update_model_answer(answer_id):
    """Update a model answer"""
    data = request.json
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Build update query dynamically
    update_fields = []
    params = []
    
    if 'title' in data:
        update_fields.append('title = ?')
        params.append(data['title'])
    
    if 'question_text' in data:
        update_fields.append('question_text = ?')
        params.append(data['question_text'])
    
    if 'answer_text' in data:
        update_fields.append('answer_text = ?')
        params.append(data['answer_text'])
        update_fields.append('word_count = ?')
        params.append(len(data['answer_text'].split()))
    
    if 'score' in data:
        update_fields.append('score = ?')
        params.append(data['score'])
    
    if 'year' in data:
        update_fields.append('year = ?')
        params.append(data['year'])
    
    if 'paper' in data:
        update_fields.append('paper = ?')
        params.append(data['paper'])
    
    if 'tags' in data:
        update_fields.append('tags = ?')
        params.append(json.dumps(data['tags']))
    
    if 'question_type' in data:
        update_fields.append('question_type = ?')
        params.append(data['question_type'])
    
    if 'source' in data:
        update_fields.append('source = ?')
        params.append(data['source'])
    
    update_fields.append('updated_at = CURRENT_TIMESTAMP')
    
    if not update_fields:
        return jsonify({'success': False, 'error': 'No fields to update'}), 400
    
    query = f"UPDATE model_answers SET {', '.join(update_fields)} WHERE id = ?"
    params.append(answer_id)
    
    cursor.execute(query, params)
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'Model answer updated successfully'
    })

@bp.route('/<int:answer_id>', methods=['DELETE'])
def delete_model_answer(answer_id):
    """Delete a model answer"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM model_answers WHERE id = ?', (answer_id,))
    conn.commit()
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'success': False, 'error': 'Answer not found'}), 404
    
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'Model answer deleted successfully'
    })

@bp.route('/search', methods=['POST'])
def search_model_answers():
    """AI-powered semantic search for model answers"""
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({'success': False, 'error': 'Query is required'}), 400
    
    if not GEMINI_API_KEY:
        # Fallback to simple text search
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM model_answers 
            WHERE question_text LIKE ? OR answer_text LIKE ? OR title LIKE ?
            LIMIT 10
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        results = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'answers': [dict(r) for r in results],
            'method': 'text_search'
        })
    
    # AI-powered search
    try:
        # Use AI to find relevant answers
        prompt = f"""Given this search query: "{query}"

Find the most relevant answers from this list:
{json.dumps([dict(a) for a in all_answers[:50]], indent=2)}

Return a JSON array of answer IDs in order of relevance (most relevant first), max 5 IDs.
Format: {{"answer_ids": [1, 2, 3]}}"""
        
        # Use ModelManager (Pro model for search reasoning)
        response = model_manager.generate_content(prompt, model_type='pro')
        text = response.text.strip().replace('```json', '').replace('```', '').strip()
        
        result = json.loads(text)
        answer_ids = result.get('answer_ids', [])
        
        # Fetch full details for relevant answers
        conn = get_db()
        cursor = conn.cursor()
        placeholders = ','.join('?' * len(answer_ids))
        cursor.execute(f'SELECT * FROM model_answers WHERE id IN ({placeholders})', answer_ids)
        answers = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'answers': [dict(a) for a in answers],
            'method': 'ai_search'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Search failed: {str(e)}'
        }), 500

@bp.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics about model answers"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total FROM model_answers')
    total = cursor.fetchone()['total']
    
    cursor.execute('SELECT paper, COUNT(*) as count FROM model_answers GROUP BY paper')
    by_paper = {row['paper']: row['count'] for row in cursor.fetchall() if row['paper']}
    
    cursor.execute('SELECT question_type, COUNT(*) as count FROM model_answers GROUP BY question_type')
    by_type = {row['question_type']: row['count'] for row in cursor.fetchall() if row['question_type']}
    
    cursor.execute('SELECT AVG(score) as avg_score FROM model_answers WHERE score IS NOT NULL')
    avg_score = cursor.fetchone()['avg_score'] or 0
    
    conn.close()
    
    return jsonify({
        'success': True,
        'stats': {
            'total': total,
            'by_paper': by_paper,
            'by_type': by_type,
            'average_score': round(avg_score, 2)
        }
    })
