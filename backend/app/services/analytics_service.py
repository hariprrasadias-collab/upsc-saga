"""
Analytics Service - Data aggregation and insights
Consolidates data from all modules for comprehensive analytics
"""
from datetime import datetime, timedelta


def calculate_study_hours(conn, user_id, start_date, end_date):
    """
    Estimate study hours based on activity timestamps
    """
    try:
        # Get all activity timestamps across modules
        activities = []

        # Mock tests
        mock_tests = conn.execute('''
            SELECT submitted_at FROM test_attempts
            WHERE user_id = ? AND submitted_at BETWEEN ? AND ?
            ORDER BY submitted_at
        ''', (user_id, start_date, end_date)).fetchall()
        activities.extend([r['submitted_at'] for r in mock_tests])

        # Answer writing
        answers = conn.execute('''
            SELECT submitted_at FROM user_answers
            WHERE user_id = ? AND submitted_at BETWEEN ? AND ?
            ORDER BY submitted_at
        ''', (user_id, start_date, end_date)).fetchall()
        activities.extend([r['submitted_at'] for r in answers])

        # Flashcard reviews
        reviews = conn.execute('''
            SELECT reviewed_at FROM review_sessions
            WHERE user_id = ? AND reviewed_at BETWEEN ? AND ?
            ORDER BY reviewed_at
        ''', (user_id, start_date, end_date)).fetchall()
        activities.extend([r['reviewed_at'] for r in reviews])

        # Pomodoro Sessions
        pomodoros = conn.execute('''
            SELECT timestamp, duration FROM pomodoro_sessions
            WHERE user_id = ? AND timestamp BETWEEN ? AND ?
            ORDER BY timestamp
        ''', (user_id, start_date, end_date)).fetchall()
        # For study hours, we can use the actual duration
        pomodoro_minutes = sum([r['duration'] for r in pomodoros])
        pomodoro_hours = pomodoro_minutes / 60.0

        if not activities:
            return round(pomodoro_hours, 1)

        # Sort all activities
        try:
            activities = sorted([datetime.fromisoformat(a)
                                for a in activities])
        except ValueError:
            # If date parsing fails, skip estimates and return just pomodoro
            return round(pomodoro_hours, 1)

        # Estimate: assume 30min per mock test, 20min per answer, 10min per review session
        # Or calculate gaps between activities (if < 2 hours, count as continuous)

        # Count unique days with activity and estimate
        unique_days = set(a.date() for a in activities)
        # Conservative estimate: 2 hours per active day
        estimated_hours = len(unique_days) * 2

        # Add actual Pomodoro time
        total_hours = estimated_hours + pomodoro_hours

        return round(total_hours, 1)
    except Exception as e:
        print(f"Error calculating study hours: {e}")
        return 0


def get_subject_performance(conn, user_id, subject):
    """
    Aggregate all metrics for a specific subject
    """
    result = {
        'subject': subject,
        'mock_avg': 0,
        'answer_avg': 0,
        'syllabus_pct': 0,
        'pyq_attempted': 0,
        'flashcard_mastered': 0
    }
    try:
        # Mock tests
        mock_avg = conn.execute('''
            SELECT AVG(score) as avg_score
            FROM test_attempts mta
            JOIN mock_tests mt ON mta.test_id = mt.id
            WHERE mta.user_id = ? AND mt.subject = ?
        ''', (user_id, subject)).fetchone()
        if mock_avg and mock_avg['avg_score']:
            result['mock_avg'] = round(mock_avg['avg_score'], 1)

        # Answer writing
        answer_avg = conn.execute('''
            SELECT AVG(ae.overall_score) as avg_score
            FROM answer_evaluations ae
            JOIN user_answers ua ON ae.answer_id = ua.id
            JOIN answer_questions aq ON ua.prompt_id = aq.id
            WHERE ua.user_id = ? AND aq.subject = ?
        ''', (user_id, subject)).fetchone()
        if answer_avg and answer_avg['avg_score']:
            result['answer_avg'] = round(answer_avg['avg_score'], 1)

        # Syllabus completion
        syllabus = conn.execute('''
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
            FROM syllabus_topics
            WHERE subject = ?
        ''', (subject,)).fetchone()
        if syllabus and syllabus['total'] > 0:
            result['syllabus_pct'] = round(
                (syllabus['completed'] / syllabus['total']) * 100, 1)
    except Exception:
        pass  # Return zeroed result on error

    return result


def get_all_subject_performance(conn, user_id, subjects):
    """
    Aggregate all metrics for multiple subjects efficiently using batched queries.
    Prevents N+1 query loops.
    """
    results = {s: {
        'subject': s,
        'mock_avg': 0,
        'answer_avg': 0,
        'syllabus_pct': 0,
        'pyq_attempted': 0,
        'flashcard_mastered': 0
    } for s in subjects}

    if not subjects:
        return []

    placeholders = ','.join(['?'] * len(subjects))

    # 1. Mock tests
    try:
        mock_data = conn.execute(f'''
            SELECT mt.subject, AVG(mta.score) as avg_score
            FROM test_attempts mta
            JOIN mock_tests mt ON mta.test_id = mt.id
            WHERE mta.user_id = ? AND mt.subject IN ({placeholders})
            GROUP BY mt.subject
        ''', [user_id] + subjects).fetchall()
        for r in mock_data:
            if r['avg_score'] is not None:
                results[r['subject']]['mock_avg'] = round(r['avg_score'], 1)
    except Exception as e:
        print(f"Error fetching mock tests for subjects: {e}")

    # 2. Answer writing
    try:
        answer_data = conn.execute(f'''
            SELECT aq.subject, AVG(ae.overall_score) as avg_score
            FROM answer_evaluations ae
            JOIN user_answers ua ON ae.answer_id = ua.id
            JOIN answer_questions aq ON ua.prompt_id = aq.id
            WHERE ua.user_id = ? AND aq.subject IN ({placeholders})
            GROUP BY aq.subject
        ''', [user_id] + subjects).fetchall()
        for r in answer_data:
            if r['avg_score'] is not None:
                results[r['subject']]['answer_avg'] = round(r['avg_score'], 1)
    except Exception as e:
        print(f"Error fetching answer evaluations for subjects: {e}")

    # 3. Syllabus completion
    try:
        syllabus_data = conn.execute(f'''
            SELECT subject,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
            FROM syllabus_topics
            WHERE subject IN ({placeholders})
            GROUP BY subject
        ''', subjects).fetchall()
        for r in syllabus_data:
            if r['total'] > 0:
                results[r['subject']]['syllabus_pct'] = round(
                    (r['completed'] / r['total']) * 100, 1)
    except Exception as e:
        print(f"Error fetching syllabus completion for subjects: {e}")

    return list(results.values())


def identify_weak_areas(conn, user_id, limit=10):
    """
    Identify topics needing attention based on performance
    """
    weak_areas = []

    try:
        # Check syllabus topics not started or in progress
        syllabus_weak = conn.execute('''
            SELECT subject, name, status
            FROM syllabus_topics
            WHERE status IN ('Not Started', 'Reading')
            ORDER BY subject, name
            LIMIT ?
        ''', (limit,)).fetchall()

        for topic in syllabus_weak:
            weak_areas.append({
                'subject': topic['subject'],
                'topic': f"{topic['name']}",
                'weakness_score': 80 if topic['status'] == 'Not Started' else 50,
                'source': 'Syllabus',
                'action': 'Start reading' if topic['status'] == 'Not Started' else 'Complete reading'
            })

        # Check mock test subjects with low scores (get bottom performing ones)
        low_scores = conn.execute('''
            SELECT mt.subject, AVG(mta.score) as avg_score, COUNT(*) as attempts
            FROM test_attempts mta
            JOIN mock_tests mt ON mta.test_id = mt.id
            WHERE mta.user_id = ?
            GROUP BY mt.subject
            ORDER BY avg_score ASC
            LIMIT ?
        ''', (user_id, limit)).fetchall()

        for subj in low_scores:
            # Calculate trend for this subject
            subject_scores = conn.execute('''
                SELECT mta.score
                FROM test_attempts mta
                JOIN mock_tests mt ON mta.test_id = mt.id
                WHERE mta.user_id = ? AND mt.subject = ?
                ORDER BY mta.submitted_at ASC
            ''', (user_id, subj['subject'])).fetchall()

            scores_list = [s['score'] for s in subject_scores]
            trend_val = calculate_improvement_rate(scores_list)
            trend_direction = 'improving' if trend_val > 0 else 'declining' if trend_val < 0 else 'stable'

            # Get last 5 scores for sparkline
            recent_scores = scores_list[-5:] if scores_list else []
            last_attempt = subject_scores[-1]['submitted_at'] if subject_scores else None

            weak_areas.append({
                'subject': subj['subject'],
                'topic': f"{subj['subject']} (Mock Tests)",
                'weakness_score': max(0, 100 - (subj['avg_score'] or 0)),
                'source': 'Mock Tests',
                'action': f"Practice {subj['subject']} questions",
                'trend': trend_direction,
                'trend_value': abs(trend_val),
                'impact': 'High' if (subj['avg_score'] or 0) < 40 else 'Medium',
                'recent_scores': recent_scores,
                'last_attempt': last_attempt
            })
    except Exception as e:
        print(f"Error identifying weak areas: {e}")

    # Sort by weakness score and limit
    weak_areas.sort(key=lambda x: x['weakness_score'], reverse=True)
    return weak_areas[:limit]


def calculate_improvement_rate(scores):
    """
    Calculate improvement rate percentage
    """
    if len(scores) < 2:
        return 0

    first_half = scores[:len(scores)//2]
    second_half = scores[len(scores)//2:]

    avg_first = sum(first_half) / len(first_half) if first_half else 0
    avg_second = sum(second_half) / len(second_half) if second_half else 0

    if avg_first == 0:
        return 0

    improvement = ((avg_second - avg_first) / avg_first) * 100
    return round(improvement, 1)


def get_streak_days(conn, user_id):
    """
    Calculate consecutive days with activity
    """
    try:
        # Get all activity dates
        dates = set()

        # Mock tests
        mock_dates = conn.execute('''
            SELECT DATE(submitted_at) as date FROM test_attempts
            WHERE user_id = ?
        ''', (user_id,)).fetchall()
        dates.update([r['date'] for r in mock_dates])

        # Answer writing
        answer_dates = conn.execute('''
            SELECT DATE(submitted_at) as date FROM user_answers
            WHERE user_id = ?
        ''', (user_id,)).fetchall()
        dates.update([r['date'] for r in answer_dates])

        # Flashcards
        review_dates = conn.execute('''
            SELECT DATE(reviewed_at) as date FROM review_sessions
            WHERE user_id = ?
        ''', (user_id,)).fetchall()
        dates.update([r['date'] for r in review_dates])

        # Pomodoro Sessions
        pomodoro_dates = conn.execute('''
            SELECT DATE(timestamp) as date FROM pomodoro_sessions
            WHERE user_id = ?
        ''', (user_id,)).fetchall()
        dates.update([r['date'] for r in pomodoro_dates])

        # War Map (Calendar Events) Completed
        warmap_dates = conn.execute('''
            SELECT DATE(updated_at) as date FROM calendar_event_metadata
            WHERE user_id = ? AND is_completed = 1
        ''', (user_id,)).fetchall()
        dates.update([r['date'] for r in warmap_dates])

        if not dates:
            return 0

        # Filter out None values and convert to set of date objects
        dates_objs = set()
        for d in dates:
            if d:
                try:
                    dates_objs.add(datetime.fromisoformat(d).date())
                except ValueError:
                    pass  # Ignore invalid date formats

        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        # Determine where the streak ends (today or yesterday)
        if today in dates_objs:
            current_date = today
        elif yesterday in dates_objs:
            current_date = yesterday
        else:
            return 0

        streak = 0
        while current_date in dates_objs:
            streak += 1
            current_date -= timedelta(days=1)

        return streak
    except Exception as e:
        print(f"Error calculating streak: {e}")
        return 0


def generate_weekly_performance_review(conn, user_id):
    """
    PHASE 7: THE WAR ROOM
    Generates a corporate-style 'Weekly Appraisal' for the aspirant.
    """
    from app.services.model_manager import model_manager
    if not model_manager.is_configured:
        return {"error": "AI Offline"}

    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    study_hours = calculate_study_hours(conn, user_id, start_date, end_date)
    streak = get_streak_days(conn, user_id)

    # Get Weak Areas
    weak_areas = identify_weak_areas(conn, user_id, limit=3)
    weak_str = ", ".join([w['topic'] for w in weak_areas])

    prompt = f"""
    # MISSION: WEEKLY PERFORMANCE REVIEW
    **Role:** The High-Command (Military/Corporate Hybrid).

    **METRICS:**
    - Hours Logged: {study_hours}
    - Streak: {streak} Days
    - Critical Weaknesses: {weak_str}

    **DIRECTIVE:**
    Write a brutal but motivating review.
    - If hours > 40: Commend the discipline.
    - If hours < 20: Issue a 'Show Cause Notice'.
    - If streak broken: Express disappointment.

    **OUTPUT SCHEMA (JSON):**
    {{
        "verdict": "Exemplary / Needs Improvement / Critical",
        "message": "The narrative review...",
        "action_plan": ["Specific Task 1", "Specific Task 2"]
    }}
    """

    try:
        response = model_manager.generate_content(prompt, model_type='pro')
        import json
        text = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}
