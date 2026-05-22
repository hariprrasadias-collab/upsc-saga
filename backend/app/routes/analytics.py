# Analytics API Routes
from flask import Blueprint, request, jsonify, session
from app.db import get_db
from datetime import datetime, timedelta
from app.services.analytics_service import (
    calculate_study_hours,
    get_subject_performance,
    get_all_subject_performances,
    identify_weak_areas,
    calculate_improvement_rate,
    get_streak_days
)

analytics = Blueprint('analytics', __name__)

@analytics.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# ==================== OVERVIEW ====================

@analytics.route('/api/analytics/overview', methods=['GET'])
def get_overview():
    """Get high-level analytics overview"""
    try:
        user_id = session.get('user_id') or 1


        timeframe = request.args.get('timeframe', '30d')  # 7d, 30d, all
        
        conn = get_db()
        
        # Calculate date range
        if timeframe == '7d':
            start_date = (datetime.now() - timedelta(days=7)).isoformat()
        elif timeframe == '30d':
            start_date = (datetime.now() - timedelta(days=30)).isoformat()
        else:  # all
            start_date = '2020-01-01'
        
        end_date = datetime.now().isoformat()
        
        # Study hours
        study_hours = calculate_study_hours(conn, user_id, start_date, end_date)
        
        # XP earned
        xp_data = conn.execute('''
            SELECT current_xp, level, max_xp FROM users WHERE id = ?
        ''', (user_id,)).fetchone()
        
        # Activities completed - handle missing tables gracefully
        try:
            mock_count = conn.execute('SELECT COUNT(*) FROM test_attempts WHERE user_id = ? AND submitted_at >= ?', (user_id, start_date)).fetchone()[0]
        except Exception:
            mock_count = 0
            
        try:
            answer_count = conn.execute('SELECT COUNT(*) FROM user_answers WHERE user_id = ? AND submitted_at >= ?', (user_id, start_date)).fetchone()[0]
        except Exception:
            answer_count = 0
            
        try:
            review_count = conn.execute('SELECT COUNT(DISTINCT flashcard_id) FROM review_sessions WHERE user_id = ? AND reviewed_at >= ?', (user_id, start_date)).fetchone()[0]
        except Exception:
            review_count = 0
        
        try:
            task_count = conn.execute('SELECT COUNT(*) FROM tasks WHERE user_id = ? AND isCompleted = 1', (user_id,)).fetchone()[0]
        except Exception:
            task_count = 0
        
        total_activities = mock_count + answer_count + review_count + task_count
        
        # Current streak
        streak = get_streak_days(conn, user_id)
        
        return jsonify({
            'study_hours': study_hours,
            'xp': xp_data['current_xp'] if xp_data else 0,
            'level': xp_data['level'] if xp_data else 1,
            'max_xp': xp_data['max_xp'] if xp_data else 100,
            'activities_completed': total_activities,
            'streak_days': streak
        })
    except Exception as e:
        print(f"Analytics overview error: {e}")
        # Return empty data instead of error
        return jsonify({
            'study_hours': 0,
            'xp': 0,
            'level': 1,
            'max_xp': 100,
            'activities_completed': 0,
            'streak_days': 0
        })


# ==================== SUBJECT-WISE ====================

@analytics.route('/api/analytics/subject-wise', methods=['GET'])
def get_subject_wise():
    """Get subject-wise performance across all modules"""
    try:
        user_id = session.get('user_id') or 1


        conn = get_db()
        
        subjects = ['GS1', 'GS2', 'GS3', 'GS4', 'Prelims', 'Optional']
        
        try:
            results = get_all_subject_performances(conn, user_id, subjects)
        except Exception as e:
            print(f"Error fetching all subject performances: {e}")
            results = [{
                'subject': subject,
                'mock_avg': 0,
                'answer_avg': 0,
                'syllabus_pct': 0,
                'pyq_attempted': 0,
                'flashcard_mastered': 0
            } for subject in subjects]
        
        return jsonify(results)
    except Exception as e:
        print(f"Subject-wise analytics error: {e}")
        return jsonify([]), 200


# ==================== TIME DISTRIBUTION ====================

@analytics.route('/api/analytics/time-distribution', methods=['GET'])
def get_time_distribution():
    """Get daily study time distribution for heatmap"""
    try:
        user_id = session.get('user_id') or 1


        days = request.args.get('days', 30, type=int)
        
        conn = get_db()
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        end_date = datetime.now().isoformat()
        
        # Get all activity dates
        activities = {}
        
        # Group by date
        dates = conn.execute('''
            SELECT DATE(submitted_at) as date FROM test_attempts
            WHERE user_id = ? AND submitted_at >= ?
            UNION ALL
            SELECT DATE(submitted_at) FROM user_answers
            WHERE user_id = ? AND submitted_at >= ?
            UNION ALL
            SELECT DATE(reviewed_at) FROM review_sessions
            WHERE user_id = ? AND reviewed_at >= ?
        ''', (user_id, start_date, user_id, start_date, user_id, start_date)).fetchall()
        
        # Count activities per date
        for row in dates:
            date = row['date']
            activities[date] = activities.get(date, 0) + 1
        
        # Convert to heatmap format: [{date, value}]
        heatmap_data = [
            {'date': date, 'hours': min(count * 0.5, 8)}  # Estimate: 30min per activity, cap at 8h
            for date, count in activities.items()
        ]
        
        return jsonify(heatmap_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== MOCK TESTS ====================

@analytics.route('/api/analytics/mock-tests', methods=['GET'])
def get_mock_test_analytics():
    """Get mock test performance trends"""
    try:
        user_id = session.get('user_id') or 1


        conn = get_db()
        
        # Score trends over time
        try:
            trends = conn.execute('''
                SELECT 
                    DATE(submitted_at) as date,
                    score,
                    mt.subject
                FROM test_attempts mta
                JOIN mock_tests mt ON mta.test_id = mt.id
                WHERE mta.user_id = ?
                ORDER BY submitted_at ASC
            ''', (user_id,)).fetchall()
            trend_data = [dict(t) for t in trends]
            scores = [t['score'] for t in trends]
            improvement = calculate_improvement_rate(scores)
        except Exception:
            trend_data = []
            improvement = 0
        
        # Subject-wise accuracy
        try:
            subject_stats = conn.execute('''
                SELECT 
                    mt.subject,
                    AVG(mta.score) as avg_score,
                    COUNT(*) as attempts
                FROM test_attempts mta
                JOIN mock_tests mt ON mta.test_id = mt.id
                WHERE mta.user_id = ?
                GROUP BY mt.subject
            ''', (user_id,)).fetchall()
            subject_stats_data = [dict(s) for s in subject_stats]
        except Exception:
            subject_stats_data = []
        
        return jsonify({
            'trends': trend_data,
            'improvement_rate': improvement,
            'subject_stats': subject_stats_data
        })
    except Exception as e:
        print(f"Mock test analytics error: {e}")
        return jsonify({'trends': [], 'improvement_rate': 0, 'subject_stats': []}), 200


# ==================== ANSWER WRITING ====================

@analytics.route('/api/analytics/answer-writing', methods=['GET'])
def get_answer_writing_analytics():
    """Get answer writing performance stats"""
    try:
        user_id = session.get('user_id') or 1


        conn = get_db()
        
        # Retrieve scores with date and subject
        try:
            scores = conn.execute('''
                SELECT ae.overall_score, DATE(ua.submitted_at) as date, aq.subject
                FROM answer_evaluations ae
                JOIN user_answers ua ON ae.answer_id = ua.id
                JOIN answer_questions aq ON ua.prompt_id = aq.id
                WHERE ua.user_id = ?
                ORDER BY ua.submitted_at ASC
            ''', (user_id,)).fetchall()
            score_data = [dict(s) for s in scores]
            # Improvement rate based on overall scores
            improvement = calculate_improvement_rate([s['overall_score'] for s in scores])
        except Exception:
            score_data = []
            improvement = 0
            
        # Average score per subject
        try:
            subject_avg = conn.execute('''
                SELECT aq.subject, AVG(ae.overall_score) as avg_score, COUNT(*) as count
                FROM answer_evaluations ae
                JOIN user_answers ua ON ae.answer_id = ua.id
                JOIN answer_questions aq ON ua.prompt_id = aq.id
                WHERE ua.user_id = ?
                GROUP BY aq.subject
            ''', (user_id,)).fetchall()
            subject_avg_data = [dict(s) for s in subject_avg]
        except Exception:
            subject_avg_data = []
            
        return jsonify({
            'scores': score_data,
            'improvement_rate': improvement,
            'subject_averages': subject_avg_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== WEAK AREAS ====================

@analytics.route('/api/analytics/weak-areas', methods=['GET'])
def get_weak_areas():
    """Identify weak topics needing attention"""
    try:
        user_id = session.get('user_id') or 1


        limit = request.args.get('limit', 10, type=int)
        
        conn = get_db()
        weak_areas = identify_weak_areas(conn, user_id, limit)
        
        return jsonify(weak_areas)
    except Exception as e:
        print(f"Weak areas analytics error: {e}")
        return jsonify([]), 200


# ==================== PROGRESS TREND ====================

@analytics.route('/api/analytics/progress-trend', methods=['GET'])
def get_progress_trend():
    """Get time-series progress data for charts"""
    try:
        user_id = session.get('user_id') or 1


        metric = request.args.get('metric', 'xp')  # xp, syllabus, mock_score
        days = request.args.get('days', 30, type=int)
        
        conn = get_db()
        start_date = (datetime.now() - timedelta(days=days)).date()
        
        trend_data = []
        
        if metric == 'syllabus':
            # Syllabus completion over time (cumulative)
            # Bolt optimization: syllabus_topics lacks historical data tracking,
            # so we only need to calculate the current progress once instead of (days + 1) times.
            completed = conn.execute('''
                SELECT COUNT(*) FROM syllabus_topics
                WHERE status = 'Completed'
            ''').fetchone()[0]

            total = conn.execute('SELECT COUNT(*) FROM syllabus_topics').fetchone()[0]

            value = round((completed / total * 100) if total > 0 else 0, 1)

            for i in range(days + 1):
                date = start_date + timedelta(days=i)
                trend_data.append({
                    'date': date.isoformat(),
                    'value': value
                })
        
        elif metric == 'mock_score':
            # Mock test scores over time
            scores = conn.execute('''
                SELECT DATE(submitted_at) as date, AVG(score) as avg_score
                FROM test_attempts
                WHERE user_id = ? AND DATE(submitted_at) >= ?
                GROUP BY DATE(submitted_at)
                ORDER BY date ASC
            ''', (user_id, start_date.isoformat())).fetchall()
            
            trend_data = [{'date': s['date'], 'value': round(s['avg_score'], 1)} for s in scores]
        
        return jsonify(trend_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== PERFORMANCE SCATTER ====================

@analytics.route('/api/analytics/performance-scatter', methods=['GET'])
def get_performance_scatter():
    """Get speed vs accuracy data for scatter plot"""
    try:
        user_id = session.get('user_id') or 1


        conn = get_db()
        
        # Group by time spent (bucketed by 10 seconds)
        # SQLite integer division automatically floors
        data = conn.execute('''
            SELECT 
                (time_spent / 10) * 10 as time_bucket,
                AVG(is_correct) * 100 as accuracy,
                COUNT(*) as count
            FROM pyq_quiz_answers
            WHERE time_spent > 0 AND time_spent < 300  -- Filter outliers (> 5 mins)
            GROUP BY time_bucket
            ORDER BY time_bucket ASC
        ''').fetchall()
        
        scatter_data = [
            {
                'time_per_question': row['time_bucket'],
                'accuracy': round(row['accuracy'], 1),
                'count': row['count']
            }
            for row in data
        ]
        
        return jsonify(scatter_data)
    except Exception as e:
        print(f"Performance scatter error: {e}")
        return jsonify([]), 200
