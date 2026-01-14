from flask import Blueprint, request, jsonify
from flask_cors import CORS
from app.db import get_db
from app.services.xp_service import award_xp
from datetime import datetime, timedelta

bp = Blueprint('syllabus', __name__, url_prefix='/api/syllabus')
CORS(bp)

@bp.route('/', methods=['GET'])
def get_syllabus():
    """Get all syllabus topics with revision info"""
    try:
        conn = get_db()
        # Optimize: exclude large notes, only return structure + has_notes flag
        topics = conn.execute('''
            SELECT t.id, t.paper, t.subject, t.topic, t.subtopic, t.status, t.last_updated,
                   (CASE WHEN length(t.notes) > 0 THEN 1 ELSE 0 END) as has_notes,
                   r.revision_count, r.next_revision_date, r.last_revised_at
            FROM syllabus_topics t
            LEFT JOIN topic_revisions r ON t.id = r.topic_id
            ORDER BY t.paper, t.subject, t.id
        ''').fetchall()
        return jsonify([dict(row) for row in topics])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>', methods=['GET'])
def get_topic_details(id):
    """Get full details for a single topic, including notes"""
    try:
        conn = get_db()
        topic = conn.execute('''
            SELECT t.*, r.revision_count, r.next_revision_date, r.last_revised_at
            FROM syllabus_topics t
            LEFT JOIN topic_revisions r ON t.id = r.topic_id
            WHERE t.id = ?
        ''', (id,)).fetchone()

        if not topic:
            return jsonify({'error': 'Topic not found'}), 404

        return jsonify(dict(topic))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>/status', methods=['POST'])
def update_status(id):
    """Update status of a topic"""
    try:
        data = request.json
        status = data.get('status')
        user_id = 1 # Hardcoded for now
        
        if status not in ['Not Started', 'Reading', 'Notes Done', 'Revision 1', 'Revision 2', 'Completed']:
            return jsonify({'error': 'Invalid status'}), 400

        conn = get_db()
        
        # Check previous status for XP award
        curr = conn.execute("SELECT status FROM syllabus_topics WHERE id = ?", (id,)).fetchone()

        if curr and curr['status'] != 'Completed' and status == 'Completed':
            # Award XP for completing a topic
            try:
                award_xp(user_id, 100, 50)
            except Exception as e:
                print(f"XP Award Error: {e}")

        conn.execute("UPDATE syllabus_topics SET status = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ?", (status, id))
        conn.commit()

        return jsonify({'id': id, 'status': status})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>/notes', methods=['POST'])
def update_notes(id):
    """Update notes for a topic"""
    try:
        data = request.json
        notes = data.get('notes')

        conn = get_db()
        conn.execute("UPDATE syllabus_topics SET notes = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ?", (notes, id))
        conn.commit()

        return jsonify({'id': id, 'notes': notes})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>/revise', methods=['POST'])
def mark_revised(id):
    """Mark a topic as revised and schedule next revision"""
    try:
        conn = get_db()

        # Get current revision state
        curr = conn.execute("SELECT * FROM topic_revisions WHERE topic_id = ?", (id,)).fetchone()

        now = datetime.now()
        today = now.date()

        if curr:
            count = curr['revision_count'] + 1
        else:
            count = 1

        # Spaced Repetition Algorithm
        intervals = {1: 1, 2: 3, 3: 7, 4: 21}
        days_to_add = intervals.get(count, 30)
        
        next_date = today + timedelta(days=days_to_add)
        
        if curr:
            conn.execute('''
                UPDATE topic_revisions
                SET last_revised_at = ?, revision_count = ?, next_revision_date = ?, status = 'pending'
                WHERE topic_id = ?
            ''', (now, count, next_date, id))
        else:
            conn.execute('''
                INSERT INTO topic_revisions (topic_id, last_revised_at, revision_count, next_revision_date, status)
                VALUES (?, ?, ?, ?, 'pending')
            ''', (id, now, count, next_date))

        conn.commit()

        # Award XP for revision
        try:
            award_xp(1, 20, 10) # 20 XP, 10 Strength
        except Exception as e:
            print(f"XP Award Error: {e}")

        return jsonify({
            'topic_id': id,
            'revision_count': count,
            'next_revision_date': next_date.isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/due', methods=['GET'])
def get_due_revisions():
    """Get topics due for revision"""
    try:
        conn = get_db()

        # Get overdue or due today
        due = conn.execute('''
            SELECT t.id, t.topic as title, t.subject, t.paper, r.revision_count, r.next_revision_date, r.last_revised_at
            FROM topic_revisions r
            JOIN syllabus_topics t ON r.topic_id = t.id
            WHERE r.next_revision_date <= date('now')
            ORDER BY r.next_revision_date ASC
        ''').fetchall()

        return jsonify([dict(row) for row in due])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/analytics', methods=['GET'])
def get_analytics():
    """Get progress analytics"""
    try:
        conn = get_db()

        # Total topics per paper
        total_counts = conn.execute('''
            SELECT paper, COUNT(*) as total
            FROM syllabus_topics
            GROUP BY paper
        ''').fetchall()

        # Completed/In Progress counts
        progress_counts = conn.execute('''
            SELECT paper, status, COUNT(*) as count
            FROM syllabus_topics
            GROUP BY paper, status
        ''').fetchall()

        return jsonify({
            'totals': [dict(row) for row in total_counts],
            'breakdown': [dict(row) for row in progress_counts]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
