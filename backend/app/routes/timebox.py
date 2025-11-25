# app/routes/timebox.py
from flask import Blueprint, request, jsonify
from app.db import get_db
from datetime import datetime, date

timebox_bp = Blueprint('timebox', __name__)

@timebox_bp.route('/api/timebox/get', methods=['GET'])
def get_timeboxes():
    """Get all time boxes for today"""
    conn = get_db()
    c = conn.cursor()
    
    today = date.today().isoformat()
    
    # Get time boxes
    c.execute('''
        SELECT subject, allocated_hours, 
               COALESCE((SELECT SUM(duration_minutes)/60.0 FROM study_sessions 
                        WHERE DATE(start_time) = ? AND subject = tb.subject), 0) as spent_hours
        FROM time_boxes tb
        WHERE user_id = 1
    ''', (today,))
    
    rows = c.fetchall()
    conn.close()
    
    return jsonify([{
        'subject': row['subject'],
        'allocated_hours': row['allocated_hours'],
        'spent_hours': round(row['spent_hours'], 2)
    } for row in rows])


@timebox_bp.route('/api/timebox/add', methods=['POST'])
def add_timebox():
    """Add a new time box"""
    data = request.get_json()
    subject = data.get('subject')
    allocated_hours = data.get('allocated_hours', 2)
    
    conn = get_db()
    c = conn.cursor()
    
    try:
        # Check if already exists
        c.execute('SELECT * FROM time_boxes WHERE user_id = 1 AND subject = ?', (subject,))
        exists = c.fetchone()
        
        if exists:
            # Update
            c.execute('''
                UPDATE time_boxes 
                SET allocated_hours = ?
                WHERE user_id = 1 AND subject = ?
            ''', (allocated_hours, subject))
        else:
            # Insert
            c.execute('''
                INSERT INTO time_boxes (user_id, subject, allocated_hours)
                VALUES (1, ?, ?)
            ''', (subject, allocated_hours))
        
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@timebox_bp.route('/api/timebox/delete/<subject>', methods=['DELETE'])
def delete_timebox(subject):
    """Delete a time box"""
    conn = get_db()
    c = conn.cursor()
    
    try:
        c.execute('DELETE FROM time_boxes WHERE user_id = 1 AND subject = ?', (subject,))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
