# app/routes/timebox.py
from flask import Blueprint, request, jsonify
from app.db import get_db
from datetime import date
from flask_cors import cross_origin
from app.utils.session import get_current_user_id

timebox_bp = Blueprint('timebox', __name__)


@timebox_bp.route('/api/timebox/get', methods=['GET'])
@cross_origin()
def get_timeboxes():
    """Get all time boxes for today"""
    try:
        conn = get_db()
        c = conn.cursor()

        today = date.today().isoformat()

        user_id = get_current_user_id()
        # Get time boxes
        c.execute('''
            SELECT subject, allocated_hours,
                   COALESCE((SELECT SUM(duration_minutes)/60.0 FROM study_sessions
                            WHERE DATE(start_time) = ? AND subject = tb.subject), 0) as spent_hours
            FROM time_boxes tb
            WHERE user_id = ?
        ''', (today, user_id))

        rows = c.fetchall()
        conn.close()

        return jsonify([{
            'subject': row['subject'],
            'allocated_hours': row['allocated_hours'],
            'spent_hours': round(row['spent_hours'], 2)
        } for row in rows])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@timebox_bp.route('/api/timebox/add', methods=['POST'])
@cross_origin()
def add_timebox():
    """Add a new time box"""
    try:
        data = request.get_json()
        subject = data.get('subject')
        allocated_hours = data.get('allocated_hours', 2)

        user_id = get_current_user_id()
        conn = get_db()
        c = conn.cursor()

        # Check if already exists
        c.execute('SELECT * FROM time_boxes WHERE user_id = ? AND subject = ?', (user_id, subject))
        exists = c.fetchone()

        if exists:
            # Update
            c.execute('''
                UPDATE time_boxes
                SET allocated_hours = ?
                WHERE user_id = ? AND subject = ?
            ''', (allocated_hours, user_id, subject))
        else:
            # Insert
            c.execute('''
                INSERT INTO time_boxes (user_id, subject, allocated_hours)
                VALUES (?, ?, ?)
            ''', (user_id, subject, allocated_hours))

        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@timebox_bp.route('/api/timebox/delete/<subject>', methods=['DELETE'])
@cross_origin()
def delete_timebox(subject):
    """Delete a time box"""
    try:
        user_id = get_current_user_id()
        conn = get_db()
        c = conn.cursor()

        c.execute('DELETE FROM time_boxes WHERE user_id = ? AND subject = ?', (user_id, subject))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@timebox_bp.route('/api/timebox/suggestions', methods=['GET'])
@cross_origin()
def get_suggestions():
    """Get smart suggestions for time boxing based on weak areas"""
    try:
        conn = get_db()
        user_id = get_current_user_id()
        # Import here to avoid circular imports if any, or just standard practice for service usage
        from app.services.analytics_service import identify_weak_areas

        # Get top 3 weak areas
        weak_areas = identify_weak_areas(conn, user_id, limit=3)
        conn.close()

        suggestions = []
        for area in weak_areas:
            suggestions.append({
                'subject': area['subject'],
                'reason': f"Weakness Score: {area['weakness_score']}% - {area['action']}",
                'recommended_hours': 2.0  # Default recommendation
            })

        return jsonify(suggestions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
