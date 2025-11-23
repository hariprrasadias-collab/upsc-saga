from flask import Blueprint, request, jsonify
from flask_cors import CORS
from app.db import get_db

bp = Blueprint('pyq', __name__, url_prefix='/api/pyq')
CORS(bp)

@bp.route('/questions', methods=['GET'])
def get_questions():
    """Get questions with optional filters"""
    conn = get_db()
    
    # Filter parameters
    year = request.args.get('year')
    subject = request.args.get('subject')
    difficulty = request.args.get('difficulty')
    search = request.args.get('search')
    is_favorite = request.args.get('is_favorite')
    
    query = "SELECT * FROM pyq_questions WHERE 1=1"
    params = []
    
    if year:
        query += " AND year = ?"
        params.append(year)
    
    if subject:
        query += " AND subject = ?"
        params.append(subject)
        
    if difficulty:
        query += " AND difficulty = ?"
        params.append(difficulty)
        
    if is_favorite == 'true':
        query += " AND is_favorite = 1"
        
    if search:
        query += " AND (question_text LIKE ? OR explanation LIKE ?)"
        search_term = f"%{search}%"
        params.append(search_term)
        params.append(search_term)
        
    query += " ORDER BY year DESC, id ASC"
    
    questions = conn.execute(query, params).fetchall()
    return jsonify([dict(q) for q in questions])

@bp.route('/filters', methods=['GET'])
def get_filters():
    """Get available filter options"""
    conn = get_db()
    
    years = conn.execute("SELECT DISTINCT year FROM pyq_questions ORDER BY year DESC").fetchall()
    subjects = conn.execute("SELECT DISTINCT subject FROM pyq_questions ORDER BY subject").fetchall()
    
    return jsonify({
        'years': [row['year'] for row in years],
        'subjects': [row['subject'] for row in subjects]
    })

@bp.route('/<int:id>/favorite', methods=['POST'])
def toggle_favorite(id):
    """Toggle favorite status of a question"""
    conn = get_db()
    
    # Check current status
    curr = conn.execute("SELECT is_favorite FROM pyq_questions WHERE id = ?", (id,)).fetchone()
    if not curr:
        return jsonify({'error': 'Question not found'}), 404
        
    new_status = not curr['is_favorite']
    
    conn.execute("UPDATE pyq_questions SET is_favorite = ? WHERE id = ?", (new_status, id))
    conn.commit()
    
    return jsonify({'id': id, 'is_favorite': new_status})

@bp.route('/analytics', methods=['GET'])
def get_analytics():
    """Get simple analytics for charts"""
    conn = get_db()
    
    # Subject distribution
    subject_counts = conn.execute('''
        SELECT subject, COUNT(*) as count 
        FROM pyq_questions 
        GROUP BY subject
    ''').fetchall()
    
    # Year-wise distribution
    year_counts = conn.execute('''
        SELECT year, COUNT(*) as count 
        FROM pyq_questions 
        GROUP BY year 
        ORDER BY year
    ''').fetchall()
    
    return jsonify({
        'by_subject': [dict(row) for row in subject_counts],
        'by_year': [dict(row) for row in year_counts]
    })
