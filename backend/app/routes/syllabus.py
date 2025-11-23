from flask import Blueprint, request, jsonify
from flask_cors import CORS
from app.db import get_db
from app.services.xp_service import award_xp

bp = Blueprint('syllabus', __name__, url_prefix='/api/syllabus')
CORS(bp)

@bp.route('/', methods=['GET'])
def get_syllabus():
    """Get all syllabus topics"""
    conn = get_db()
    topics = conn.execute("SELECT * FROM syllabus_topics ORDER BY paper, subject, id").fetchall()
    return jsonify([dict(row) for row in topics])

@bp.route('/<int:id>/status', methods=['POST'])
def update_status(id):
    """Update status of a topic"""
    data = request.json
    status = data.get('status')
    user_id = 1 # Hardcoded for now
    
    if status not in ['Not Started', 'Reading', 'Notes Done', 'Revision 1', 'Revision 2', 'Completed']:
        return jsonify({'error': 'Invalid status'}), 400
        
    conn = get_db()
    
    # Check previous status for XP award
    curr = conn.execute("SELECT status FROM syllabus_topics WHERE id = ?", (id,)).fetchone()
    
    if curr:
        print(f"DEBUG: Topic {id} status: {curr['status']} -> {status}")
    
    if curr and curr['status'] != 'Completed' and status == 'Completed':
        # Award XP for completing a topic
        print(f"DEBUG: Condition met! Awarding XP.")
        award_xp(user_id, 100, 50)
        
    conn.execute("UPDATE syllabus_topics SET status = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ?", (status, id))
    conn.commit()
    
    return jsonify({'id': id, 'status': status})

@bp.route('/<int:id>/notes', methods=['POST'])
def update_notes(id):
    """Update notes for a topic"""
    data = request.json
    notes = data.get('notes')
    
    conn = get_db()
    conn.execute("UPDATE syllabus_topics SET notes = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ?", (notes, id))
    conn.commit()
    
    return jsonify({'id': id, 'notes': notes})

@bp.route('/analytics', methods=['GET'])
def get_analytics():
    """Get progress analytics"""
    conn = get_db()
    
    # Total topics per paper
    total_counts = conn.execute('''
        SELECT paper, COUNT(*) as total 
        FROM syllabus_topics 
        GROUP BY paper
    ''').fetchall()
    
    # Completed/In Progress counts
    # We'll consider anything not 'Not Started' as In Progress, and 'Completed' as Done
    progress_counts = conn.execute('''
        SELECT paper, status, COUNT(*) as count 
        FROM syllabus_topics 
        GROUP BY paper, status
    ''').fetchall()
    
    return jsonify({
        'totals': [dict(row) for row in total_counts],
        'breakdown': [dict(row) for row in progress_counts]
    })
