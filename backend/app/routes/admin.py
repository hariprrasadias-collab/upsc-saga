# Admin API Routes
from flask import Blueprint, jsonify, request
from app.db import get_db
from app.utils.session import get_current_user_id
import json
import time as import_time
from app.utils.session import get_current_user_id

admin_bp = Blueprint('admin', __name__)

def is_admin(user_id):
    """
    Check if the user has admin privileges.
    Verifies the is_admin column in the users table.
    """
    try:
        conn = get_db()
        # Fetch is_admin status from database
        user = conn.execute('SELECT is_admin FROM users WHERE id = ?', (user_id,)).fetchone()

        # If user exists and is_admin is explicitly set to 1/True
        if user:
            # In SQLite, boolean is 0 or 1.
            if user['is_admin']:
                return True
            else:
                return False

        # User not found
        return False

    except Exception as e:
        print(f"Admin check failed for user {user_id}: {e}")
        # Fail Closed: If DB is unreachable or errored, deny access.
        # Do not allow admin access on error to prevent bypasses.
        return False

@admin_bp.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    """Get overview statistics for admin dashboard"""
    try:
        user_id = get_current_user_id()

        if not is_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
            
        conn = get_db()
        
        # Count questions
        questions_count = conn.execute('SELECT COUNT(*) FROM mock_questions').fetchone()[0]
        
        # Count users
        users_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        
        # Count articles (Ravens)
        articles_count = conn.execute('SELECT COUNT(*) FROM current_affairs').fetchone()[0]
        
        # Recent activity (mock tests taken)
        recent_tests = conn.execute('''
            SELECT COUNT(*) FROM test_attempts 
            WHERE started_at >= date('now', '-7 days')
        ''').fetchone()[0]
        
        return jsonify({
            'total_questions': questions_count,
            'total_users': users_count,
            'total_articles': articles_count,
            'weekly_tests': recent_tests
        })
    except Exception as e:
        print(f"Error getting admin stats: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/questions', methods=['GET'])
def get_questions():
    """Get paginated questions for management"""
    try:
        user_id = get_current_user_id()
        if not is_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
            
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        subject = request.args.get('subject')
        search = request.args.get('search')
        
        offset = (page - 1) * per_page
        
        conn = get_db()
        query = 'SELECT * FROM mock_questions WHERE 1=1'
        params = []
        
        if subject:
            query += ' AND subject = ?'
            params.append(subject)
            
        if search:
            query += ' AND (question_text LIKE ? OR topic LIKE ?)'
            params.append(f'%{search}%')
            params.append(f'%{search}%')
            
        # Get total count for pagination
        count_query = query.replace('SELECT *', 'SELECT COUNT(*)')
        total = conn.execute(count_query, params).fetchone()[0]
        
        # Get data
        query += ' ORDER BY id DESC LIMIT ? OFFSET ?'
        params.extend([per_page, offset])
        
        questions = conn.execute(query, params).fetchall()
        
        return jsonify({
            'questions': [dict(q) for q in questions],
            'total': total,
            'page': page,
            'pages': (total + per_page - 1) // per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/questions', methods=['POST'])
def add_question():
    """Add a new question"""
    try:
        user_id = get_current_user_id()
        if not is_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
            
        data = request.get_json()
        
        required = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'subject', 'topic']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
                
        conn = get_db()
        cursor = conn.execute('''
            INSERT INTO mock_questions 
            (question_text, option_a, option_b, option_c, option_d, correct_option, explanation, subject, topic, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['question_text'],
            data['option_a'],
            data['option_b'],
            data['option_c'],
            data['option_d'],
            data['correct_option'],
            data.get('explanation', ''),
            data['subject'],
            data['topic'],
            data.get('difficulty', 'medium')
        ))
        
        conn.commit()
        return jsonify({'success': True, 'id': cursor.lastrowid})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/questions/<int:id>', methods=['PUT'])
def update_question(id):
    """Update an existing question"""
    try:
        user_id = get_current_user_id()
        if not is_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
            
        data = request.get_json()
        conn = get_db()
        
        # Build update query dynamically
        fields = []
        params = []
        allowed_fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'explanation', 'subject', 'topic', 'difficulty']
        
        for field in allowed_fields:
            if field in data:
                fields.append(f'{field} = ?')
                params.append(data[field])
                
        if not fields:
            return jsonify({'error': 'No fields to update'}), 400
            
        params.append(id)
        query = f'UPDATE mock_questions SET {", ".join(fields)} WHERE id = ?'
        
        conn.execute(query, params)
        conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/questions/<int:id>', methods=['DELETE'])
def delete_question(id):
    """Delete a question"""
    try:
        user_id = get_current_user_id()
        if not is_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
            
        conn = get_db()
        conn.execute('DELETE FROM mock_questions WHERE id = ?', (id,))
        conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Article Management Routes ---

@admin_bp.route('/api/admin/articles', methods=['GET'])
def get_articles():
    """Get paginated articles"""
    try:
        user_id = get_current_user_id()
        if not is_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
            
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search')
        
        offset = (page - 1) * per_page
        
        conn = get_db()
        query = 'SELECT * FROM current_affairs WHERE 1=1'
        params = []
        
        if search:
            query += ' AND (title LIKE ? OR upsc_summary LIKE ? OR subjects LIKE ?)'
            params.append(f'%{search}%')
            params.append(f'%{search}%')
            params.append(f'%{search}%')
            
        # Get total count
        count_query = query.replace('SELECT *', 'SELECT COUNT(*)')
        total = conn.execute(count_query, params).fetchone()[0]
        
        # Get data
        query += ' ORDER BY fetch_date DESC LIMIT ? OFFSET ?'
        params.extend([per_page, offset])
        
        articles = conn.execute(query, params).fetchall()
        
        articles_list = []
        for a in articles:
            d = dict(a)
            # Map DB columns to frontend expected fields
            d['tags'] = d.get('subjects', '')
            d['category'] = d.get('papers', '')
            # Clean up JSON strings for display if needed, but raw string is fine for now
            articles_list.append(d)

        return jsonify({
            'articles': articles_list,
            'total': total,
            'page': page,
            'pages': (total + per_page - 1) // per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/articles', methods=['POST'])
def add_article():
    """Add a new article"""
    try:
        user_id = get_current_user_id()
        if not is_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
            
        data = request.get_json()
        
        if 'title' not in data or 'content' not in data:
            return jsonify({'error': 'Title and content are required'}), 400
            
        conn = get_db()
        # Map 'content' to 'upsc_summary' and 'original_summary'
        # Map 'tags' to 'subjects'
        # Map 'category' to 'papers'
        
        import json
        subjects = json.dumps([data.get('tags', '')]) if data.get('tags') else '[]'
        papers = json.dumps([data.get('category', 'General')])
        
        cursor = conn.execute('''
            INSERT INTO current_affairs (
                title, upsc_summary, original_summary, subjects, source, papers, 
                published_date, original_link
            )
            VALUES (?, ?, ?, ?, ?, ?, DATE('now'), ?)
        ''', (
            data['title'],
            data['content'],
            data['content'], # Use content for both summaries for manual entry
            subjects,
            data.get('source', 'Manual'),
            papers,
            'manual-entry-' + str(int(import_time.time())) # Dummy link
        ))
        
        conn.commit()
        return jsonify({'success': True, 'id': cursor.lastrowid})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/articles/<int:id>', methods=['PUT'])
def update_article(id):
    """Update an article"""
    try:
        user_id = get_current_user_id()
        if not is_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
            
        data = request.get_json()
        conn = get_db()
        
        fields = []
        params = []
        
        if 'title' in data:
            fields.append('title = ?')
            params.append(data['title'])
            
        if 'content' in data:
            fields.append('upsc_summary = ?')
            fields.append('original_summary = ?')
            params.append(data['content'])
            params.append(data['content'])
            
        if 'tags' in data:
            import json
            fields.append('subjects = ?')
            params.append(json.dumps([data['tags']]))
            
        if 'source' in data:
            fields.append('source = ?')
            params.append(data['source'])
            
        if not fields:
            return jsonify({'error': 'No fields to update'}), 400
            
        params.append(id)
        query = f'UPDATE current_affairs SET {", ".join(fields)} WHERE id = ?'
        
        conn.execute(query, params)
        conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/articles/<int:id>', methods=['DELETE'])
def delete_article(id):
    """Delete an article"""
    try:
        user_id = get_current_user_id()
        if not is_admin(user_id):
            return jsonify({'error': 'Unauthorized'}), 403
            
        conn = get_db()
        conn.execute('DELETE FROM current_affairs WHERE id = ?', (id,))
        conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
