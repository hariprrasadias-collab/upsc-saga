from flask import Blueprint, request, jsonify
from app.db import get_db
import json
from datetime import datetime
from app.validators import parse_pagination

bp = Blueprint('pyq', __name__, url_prefix='/api/pyq')

@bp.route('/questions', methods=['GET'])
def get_questions():
    """Get questions with optional filters (supports multi-select)"""
    try:
        conn = get_db()

        # Filter parameters - support both single and multi-select
        years = request.args.getlist('years') or ([request.args.get('year')] if request.args.get('year') else [])
        subjects = request.args.getlist('subjects') or ([request.args.get('subject')] if request.args.get('subject') else [])
        topics = request.args.getlist('topics') or ([request.args.get('topic')] if request.args.get('topic') else [])
        difficulty = request.args.get('difficulty')
        search = request.args.get('search')
        is_favorite = request.args.get('is_favorite')

        query = "SELECT * FROM pyq_questions WHERE 1=1"
        params = []

        # Multi-select support for years
        if years:
            placeholders = ','.join(['?'] * len(years))
            query += f" AND year IN ({placeholders})"
            params.extend(years)

        # Multi-select support for subjects
        if subjects:
            placeholders = ','.join(['?'] * len(subjects))
            query += f" AND subject IN ({placeholders})"
            params.extend(subjects)

        # Multi-select support for topics
        if topics:
            placeholders = ','.join(['?'] * len(topics))
            query += f" AND topic IN ({placeholders})"
            params.extend(topics)

        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty)

        if is_favorite == 'true':
            query += " AND is_favorite = 1"

        if search:
            # Optimization: Use FTS5 match if available
            try:
                # We join with FTS table for speed
                # Note: We can't just join easily in one query if we want to keep all filters
                # So we use the rowid from FTS to filter the main table
                fts_query = "SELECT rowid FROM pyq_questions_fts WHERE pyq_questions_fts MATCH ? ORDER BY rank"
                fts_rows = conn.execute(fts_query, (search,)).fetchall()
                if fts_rows:
                    ids = [str(r['rowid']) for r in fts_rows]
                    query += f" AND id IN ({','.join(ids)})"
                else:
                    # No matches found in FTS
                    query += " AND 1=0"
            except Exception as e:
                # Fallback to LIKE if FTS fails or table doesn't exist
                print(f"FTS Search failed, falling back to LIKE: {e}")
                query += " AND (question_text LIKE ? OR explanation LIKE ?)"
                search_term = f"%{search}%"
                params.append(search_term)
                params.append(search_term)

        query += " ORDER BY year DESC, id ASC"
        
        # Pagination
        page, per_page = parse_pagination(request.args, default_per_page=50)
        
        # Extract count query
        count_query = query.replace("SELECT *", "SELECT COUNT(*)", 1).split(" ORDER BY")[0]
        try:
            total = conn.execute(count_query, params).fetchone()[0]
        except Exception:
            total = 0
            
        query += " LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])
        
        questions = conn.execute(query, params).fetchall()
        return jsonify({
            "data": [dict(q) for q in questions],
            "total": total,
            "page": page,
            "per_page": per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/filters', methods=['GET'])
def get_filters():
    """Get available filter options"""
    try:
        conn = get_db()

        years = conn.execute("SELECT DISTINCT year FROM pyq_questions ORDER BY year DESC").fetchall()
        subjects = conn.execute("SELECT DISTINCT subject FROM pyq_questions ORDER BY subject").fetchall()
        topics = conn.execute("SELECT DISTINCT topic FROM pyq_questions WHERE topic IS NOT NULL ORDER BY topic").fetchall()

        return jsonify({
            'years': [row['year'] for row in years],
            'subjects': [row['subject'] for row in subjects],
            'topics': [row['topic'] for row in topics]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/topics', methods=['GET'])
def get_topics():
    """Get topics filtered by selected subject(s)"""
    try:
        conn = get_db()
        subjects = request.args.getlist('subjects')

        if subjects:
            # Get topics for selected subjects
            placeholders = ','.join(['?'] * len(subjects))
            query = f"""
                SELECT DISTINCT topic, subject
                FROM pyq_questions
                WHERE subject IN ({placeholders}) AND topic IS NOT NULL
                ORDER BY subject, topic
            """
            topics = conn.execute(query, subjects).fetchall()
        else:
            # Get all topics if no subject selected
            query = """
                SELECT DISTINCT topic, subject
                FROM pyq_questions
                WHERE topic IS NOT NULL
                ORDER BY subject, topic
            """
            topics = conn.execute(query).fetchall()

        return jsonify([{'topic': row['topic'], 'subject': row['subject']} for row in topics])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>/favorite', methods=['POST'])
def toggle_favorite(id):
    """Toggle favorite status of a question"""
    try:
        conn = get_db()

        # Check current status
        curr = conn.execute("SELECT is_favorite FROM pyq_questions WHERE id = ?", (id,)).fetchone()
        if not curr:
            return jsonify({'error': 'Question not found'}), 404

        new_status = not curr['is_favorite']

        conn.execute("UPDATE pyq_questions SET is_favorite = ? WHERE id = ?", (new_status, id))
        conn.commit()

        return jsonify({'id': id, 'is_favorite': new_status})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/analytics', methods=['GET'])
def get_analytics():
    """Get analytics with optional filters"""
    try:
        conn = get_db()

        # Base query filters
        filters_sql = "WHERE 1=1"
        params = []

        subjects = request.args.getlist('subjects')
        if subjects:
            placeholders = ','.join(['?'] * len(subjects))
            filters_sql += f" AND subject IN ({placeholders})"
            params.extend(subjects)

        years = request.args.getlist('years')
        if years:
            placeholders = ','.join(['?'] * len(years))
            filters_sql += f" AND year IN ({placeholders})"
            params.extend(years)

        # Subject distribution (Filtered)
        subject_counts = conn.execute(f'''
            SELECT subject, COUNT(*) as count
            FROM pyq_questions
            {filters_sql}
            GROUP BY subject
        ''', params).fetchall()

        # Year-wise distribution (Filtered)
        year_counts = conn.execute(f'''
            SELECT year, COUNT(*) as count
            FROM pyq_questions
            {filters_sql}
            GROUP BY year
            ORDER BY year
        ''', params).fetchall()

        # Topic distribution (Top 20 Filtered)
        topic_counts = conn.execute(f'''
            SELECT topic, COUNT(*) as count
            FROM pyq_questions
            {filters_sql} AND topic IS NOT NULL
            GROUP BY topic
            ORDER BY count DESC
            LIMIT 20
        ''', params).fetchall()

        # Difficulty Trends (Filtered)
        difficulty_trends = conn.execute(f'''
            SELECT year, difficulty, COUNT(*) as count
            FROM pyq_questions
            {filters_sql}
            GROUP BY year, difficulty
            ORDER BY year
        ''', params).fetchall()

        return jsonify({
            'by_subject': [dict(row) for row in subject_counts],
            'by_year': [dict(row) for row in year_counts],
            'by_topic': [dict(row) for row in topic_counts],
            'difficulty_trend': [dict(row) for row in difficulty_trends]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

from app import cache # noqa: E402

@bp.route('/strategos/<int:question_id>', methods=['POST'])
def ask_strategos(question_id):
    """Ask AI for tactical breakdown of a question"""
    try:
        # 1. Rate Limiting Check using Global Cache
        client_ip = request.remote_addr
        cache_key = f"strategos_rl_{client_ip}"
        
        if cache.get(cache_key):
            return jsonify({'success': False, 'error': 'Strategos is thinking. Please wait 5 seconds.'}), 429
            
        # Set cooldown for 5 seconds
        cache.set(cache_key, True, timeout=5)

        conn = get_db()
        question = conn.execute("SELECT * FROM pyq_questions WHERE id = ?", (question_id,)).fetchone()

        if not question:
            return jsonify({'error': 'Question not found'}), 404


        # Prepare payload
        # PHASE 7: STRATEGOS UPGRADE (REAL-TIME TACTICAL ADVICE)
        prompt_text = f"""
        # MISSION: REAL-TIME BATTLEFIELD ADVICE (STRATEGOS)
        **Context:** The user is staring at this question right now.
        **Question:** "{question['question_text']}"
        **Options:**
        A) {question['option_a']}
        B) {question['option_b']}
        C) {question['option_c']}
        D) {question['option_d']}

        **DIRECTIVE:**
        Don't solve it yet. Give a TACTICAL HINT.
        - "Look at Option B. Is 'drastically' a safe word?"
        - "Recall the timeline of 1942."

        **OUTPUT:**
        Just the hint text. Short and urgent.
        """

        # We invoke ModelManager directly for speed/custom prompt here, or use BrainService with a new action.
        # Let's stick to BrainService for consistency but upgrade the payload intent.

        # Execute Action
        # We reuse ANALYZE_QUESTION but the prompt injected above overrides standard analysis effectively
        # if the BrainService logic supported raw prompts.
        # Actually, BrainService wraps it. Let's create a new Action type for this specific feature to be clean.
        # But to avoid touching BrainService again in this step, we will use ANALYZE_QUESTION
        # and rely on the fact that we improved ANALYZE_QUESTION to be "Surgical".
        # However, "Surgical" gives the answer. Strategos should give a HINT.
        # Let's do a direct call here for Phase 7 uniqueness.
        from app.services.model_manager import model_manager
        response = model_manager.generate_content(prompt_text, model_type='fast')

        return jsonify({
            "success": True,
            "tactical_hint": response.text.strip(),
            "analysis": "Full analysis available after submission."
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/create-mock', methods=['POST'])
def create_mock_from_filters():
    """Create a mock test from filtered PYQ questions"""
    try:
        data = request.get_json()
        filters = data.get('filters', {})
        
        conn = get_db()
        
        # 1. Fetch filtered questions
        query = "SELECT * FROM pyq_questions WHERE 1=1"
        params = []
        
        title_parts = []
        
        if filters.get('year'):
            query += " AND year = ?"
            params.append(filters['year'])
            title_parts.append(str(filters['year']))
            
        if filters.get('subject'):
            query += " AND subject = ?"
            params.append(filters['subject'])
            title_parts.append(filters['subject'])
            
        if filters.get('topic'):
            query += " AND topic = ?"
            params.append(filters['topic'])
            title_parts.append(filters['topic'])
            
        if filters.get('search'):
            query += " AND (question_text LIKE ? OR explanation LIKE ?)"
            search_term = f"%{filters['search']}%"
            params.append(search_term)
            params.append(search_term)
            title_parts.append(f"Search: {filters['search']}")
            
        if filters.get('is_favorite'):
            query += " AND is_favorite = 1"
            title_parts.append("Favorites")
            
        questions = conn.execute(query, params).fetchall()
        
        if not questions:
            return jsonify({'error': 'No questions found matching filters'}), 400
            
        # 2. Create Mock Test
        title = "PYQ Archive: " + " - ".join(title_parts) if title_parts else "PYQ Archive: All Questions"
        description = f"Generated from Archives with {len(questions)} questions."
        total_questions = len(questions)
        duration = total_questions * 2 # 2 mins per question
        total_marks = total_questions * 2
        
        cursor = conn.execute('''
            INSERT INTO mock_tests (title, description, test_type, subject, total_questions, duration_minutes, total_marks, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            title, 
            description, 
            'pyq-generated', 
            filters.get('subject', 'Mixed'), 
            total_questions, 
            duration, 
            total_marks, 
            'Medium'
        ))
        
        test_id = cursor.lastrowid
        
        # 3. Insert Questions into test_questions
        questions_data = [
            (
                test_id, 
                idx + 1, 
                q['question_text'],
                q['option_a'], q['option_b'], q['option_c'], q['option_d'],
                q['correct_option'], q['explanation'],
                q['subject'], q['topic'], q['difficulty'], q['year']
            ) for idx, q in enumerate(questions)
        ]
        conn.executemany('''
            INSERT INTO test_questions (
                test_id, question_number, question_text,
                option_a, option_b, option_c, option_d,
                correct_answer, explanation, subject, topic, difficulty, year
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', questions_data)
            
        conn.commit()
        
        return jsonify({
            'success': True, 
            'test_id': test_id, 
            'message': f'Created mock test "{title}" with {total_questions} questions'
        })
        
    except Exception as e:
        print(f"Error creating mock test: {e}")
        return jsonify({'error': str(e)}), 500

# ============ QUIZ MODE ENDPOINTS ============

@bp.route('/start-quiz', methods=['POST'])
def start_quiz():
    """Start a new quiz session with filtered questions"""
    try:
        data = request.get_json()
        filters = data.get('filters', {})
        title = data.get('title', 'PYQ Quiz')
        
        conn = get_db()
        
        # Build query with filters
        query = "SELECT * FROM pyq_questions WHERE 1=1"
        params = []
        
        if filters.get('year'):
            query += " AND year = ?"
            params.append(filters['year'])
            
        if filters.get('subject'):
            query += " AND subject = ?"
            params.append(filters['subject'])
            
        if filters.get('topic'):
            query += " AND topic = ?"
            params.append(filters['topic'])
            
        if filters.get('search'):
            query += " AND (question_text LIKE ? OR explanation LIKE ?)"
            search_term = f"%{filters['search']}%"
            params.append(search_term)
            params.append(search_term)
            
        if filters.get('is_favorite'):
            query += " AND is_favorite = 1"
        
        # Randomize question order
        query += " ORDER BY RANDOM()"
        
        # Limit number of questions if specified
        try:
            limit = int(filters.get('limit', 25))
        except (ValueError, TypeError):
            limit = 25

        query += " LIMIT ?"
        params.append(limit)
        
        questions = conn.execute(query, params).fetchall()
        
        if not questions:
            return jsonify({'error': 'No questions found matching filters'}), 400
        
        # Create quiz session
        cursor = conn.execute('''
            INSERT INTO pyq_quiz_sessions (title, total_questions, filters, status, user_id)
            VALUES (?, ?, ?, ?, 1)
        ''', (title, len(questions), json.dumps(filters), 'in_progress'))
        
        session_id = cursor.lastrowid
        
        # Initialize answer records
        answers_data = [(session_id, q['id']) for q in questions]
        conn.executemany('''
            INSERT INTO pyq_quiz_answers (session_id, question_id)
            VALUES (?, ?)
        ''', answers_data)
        
        conn.commit()
        
        return jsonify({
            'session_id': session_id,
            'questions': [dict(q) for q in questions],
            'total_questions': len(questions),
            'started_at': cursor.lastrowid
        })
        
    except Exception as e:
        print(f"Error starting quiz: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/quiz/<int:session_id>/answer', methods=['POST'])
def save_answer(session_id):
    """Save user's answer for a specific question"""
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        selected_answer = data.get('selected_answer')
        time_spent = data.get('time_spent', 0)
        marked_for_review = data.get('marked_for_review', False)
        
        conn = get_db()
        
        # Get correct answer
        question = conn.execute(
            "SELECT correct_option FROM pyq_questions WHERE id = ?",
            (question_id,)
        ).fetchone()
        
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        is_correct = (selected_answer == question['correct_option']) if selected_answer else False
        
        # Update answer record
        conn.execute('''
            UPDATE pyq_quiz_answers 
            SET selected_answer = ?, is_correct = ?, time_spent = ?, marked_for_review = ?
            WHERE session_id = ? AND question_id = ?
        ''', (selected_answer, is_correct, time_spent, marked_for_review, session_id, question_id))
        
        conn.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error saving answer: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/quiz/<int:session_id>/submit', methods=['POST'])
def submit_quiz(session_id):
    """Submit quiz and calculate score"""
    try:
        conn = get_db()
        
        # Get all answers for this session
        answers = conn.execute('''
            SELECT * FROM pyq_quiz_answers WHERE session_id = ?
        ''', (session_id,)).fetchall()
        
        total_questions = len(answers)
        correct_count = sum(1 for a in answers if a['is_correct'])
        incorrect_count = total_questions - correct_count
        score = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        # Calculate total time spent
        total_time = sum(a['time_spent'] or 0 for a in answers)
        
        # Update session
        conn.execute('''
            UPDATE pyq_quiz_sessions 
            SET submitted_at = ?, duration_seconds = ?, score = ?, 
                correct_count = ?, incorrect_count = ?, status = ?
            WHERE id = ?
        ''', (datetime.now(), total_time, score, correct_count, incorrect_count, 'completed', session_id))
        
        conn.commit()
        
        # Get detailed results
        results = conn.execute('''
            SELECT qa.*, q.question_text, q.option_a, q.option_b, q.option_c, q.option_d,
                   q.correct_option, q.explanation, q.subject, q.topic, q.year
            FROM pyq_quiz_answers qa
            JOIN pyq_questions q ON qa.question_id = q.id
            WHERE qa.session_id = ?
            ORDER BY qa.id
        ''', (session_id,)).fetchall()
        
        return jsonify({
            'score': score,
            'total_questions': total_questions,
            'correct_count': correct_count,
            'incorrect_count': incorrect_count,
            'duration_seconds': total_time,
            'results': [dict(r) for r in results]
        })
        
    except Exception as e:
        print(f"Error submitting quiz: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/quiz/<int:session_id>', methods=['GET'])
def get_quiz_session(session_id):
    """Get quiz session details with answers"""
    try:
        conn = get_db()
        
        session = conn.execute(
            "SELECT * FROM pyq_quiz_sessions WHERE id = ?",
            (session_id,)
        ).fetchone()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        answers = conn.execute('''
            SELECT qa.*, q.question_text, q.option_a, q.option_b, q.option_c, q.option_d,
                   q.correct_option, q.explanation, q.subject, q.topic, q.year, q.difficulty
            FROM pyq_quiz_answers qa
            JOIN pyq_questions q ON qa.question_id = q.id
            WHERE qa.session_id = ?
            ORDER BY qa.id
        ''', (session_id,)).fetchall()
        
        return jsonify({
            'session': dict(session),
            'questions': [dict(a) for a in answers]
        })
        
    except Exception as e:
        print(f"Error fetching quiz session: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/quiz-history', methods=['GET'])
def get_quiz_history():
    """Get all quiz sessions for user"""
    try:
        conn = get_db()
        
        sessions = conn.execute('''
            SELECT * FROM pyq_quiz_sessions 
            WHERE user_id = 1
            ORDER BY started_at DESC
        ''').fetchall()
        
        return jsonify([dict(s) for s in sessions])
        
    except Exception as e:
        print(f"Error fetching quiz history: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/quiz-stats', methods=['GET'])
def get_quiz_stats():
    """Get overall quiz performance statistics"""
    try:
        conn = get_db()
        
        # Overall stats
        overall = conn.execute('''
            SELECT 
                COUNT(*) as total_quizzes,
                AVG(score) as avg_score,
                MAX(score) as best_score,
                SUM(total_questions) as total_questions_attempted
            FROM pyq_quiz_sessions
            WHERE user_id = 1 AND status = 'completed'
        ''').fetchone()
        
        # Subject-wise accuracy
        subject_stats = conn.execute('''
            SELECT 
                q.subject,
                COUNT(*) as attempted,
                SUM(CASE WHEN qa.is_correct THEN 1 ELSE 0 END) as correct,
                ROUND(AVG(CASE WHEN qa.is_correct THEN 100.0 ELSE 0.0 END), 2) as accuracy
            FROM pyq_quiz_answers qa
            JOIN pyq_questions q ON qa.question_id = q.id
            JOIN pyq_quiz_sessions qs ON qa.session_id = qs.id
            WHERE qs.user_id = 1 AND qs.status = 'completed' AND qa.selected_answer IS NOT NULL
            GROUP BY q.subject
            ORDER BY accuracy DESC
        ''').fetchall()
        
        # Recent improvement trend (last 10 quizzes)
        trend = conn.execute('''
            SELECT score, started_at
            FROM pyq_quiz_sessions
            WHERE user_id = 1 AND status = 'completed'
            ORDER BY started_at DESC
            LIMIT 10
        ''').fetchall()
        
        return jsonify({
            'overall': dict(overall) if overall else {},
            'subject_wise': [dict(s) for s in subject_stats],
            'recent_trend': [dict(t) for t in trend]
        })
        
    except Exception as e:
        print(f"Error fetching quiz stats: {e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/similar/<int:question_id>', methods=['GET'])
def get_similar_questions(question_id):
    """Find similar questions using FTS5"""
    try:
        conn = get_db()

        # Get the question text
        question = conn.execute("SELECT question_text, subject FROM pyq_questions WHERE id = ?", (question_id,)).fetchone()
        if not question:
            return jsonify({'error': 'Question not found'}), 404

        text = question['question_text']
        # Clean text for FTS query (remove special chars, etc.)
        import re
        clean_text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
        # Use first few important words or the whole thing?
        # FTS MATCH query needs to be carefully constructed.
        # Simple approach: "word1 OR word2 OR ..."
        words = [w for w in clean_text.split() if len(w) > 4][:10] # Take top 10 long words
        search_query = " OR ".join(words)

        if not search_query:
             return jsonify([])

        # FTS Query
        query = """
            SELECT q.*
            FROM pyq_questions_fts fts
            JOIN pyq_questions q ON fts.rowid = q.id
            WHERE pyq_questions_fts MATCH ?
            AND q.id != ?
            ORDER BY rank
            LIMIT 5
        """

        similar = conn.execute(query, (search_query, question_id)).fetchall()
        return jsonify([dict(q) for q in similar])

    except Exception:
        # Fallback to subject-based random
        try:
             conn = get_db()
             fallback = conn.execute("SELECT * FROM pyq_questions WHERE subject = ? AND id != ? ORDER BY RANDOM() LIMIT 5", (question['subject'], question_id)).fetchall()
             return jsonify([dict(q) for q in fallback])
        except Exception:
             return jsonify([])
