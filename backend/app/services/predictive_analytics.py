"""
Predictive Analytics Service
Calculates exam readiness, success probability, optimal study time, and burnout risk
"""
import sqlite3
from datetime import datetime, timedelta
import math

def get_db_connection():
    conn = sqlite3.connect('upsc_saga.db')
    conn.row_factory = sqlite3.Row
    return conn

def calculate_exam_readiness():
    """
    Calculate Exam Readiness Score (0-100%)
    Factors: Topic Coverage, Study Hours, Mock Performance, Consistency
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    # 1. Topic Coverage (0-25 points): % of syllabus topics marked as 'mastered' or 'in-progress'
    c.execute("""
        SELECT 
            COUNT(CASE WHEN status IN ('mastered', 'in-progress') THEN 1 END) * 100.0 / COUNT(*) as coverage
        FROM syllabus_topics
    """)
    topic_coverage = c.fetchone()['coverage'] or 0
    coverage_score = (topic_coverage / 100) * 25
    
    # 2. Study Hours (0-25 points): At least 6 hours/day avg in last 30 days
    c.execute("""
        SELECT SUM(study_hours) / 30.0 as avg_hours
        FROM user_stats
        WHERE date >= date('now', '-30 days')
    """)
    avg_hours = c.fetchone()['avg_hours'] or 0
    hours_score = min((avg_hours / 6.0) * 25, 25)
    
    # 3. Mock Performance (0-30 points): Avg score of last 5 mocks
    c.execute("""
        SELECT AVG(score) as avg_score
        FROM mock_test_results
        ORDER BY created_at DESC
        LIMIT 5
    """)
    avg_mock_score = c.fetchone()['avg_score'] or 0
    mock_score = (avg_mock_score / 100) * 30
    
    # 4. Consistency (0-20 points): Study streak days
    c.execute("SELECT current_streak FROM user_stats WHERE user_id = 1")
    row = c.fetchone()
    streak = row['current_streak'] if row else 0
    consistency_score = min((streak / 30.0) * 20, 20)
    
    conn.close()
    
    total_score = coverage_score + hours_score + mock_score + consistency_score
    return {
        'overall_score': round(total_score, 1),
        'breakdown': {
            'topic_coverage': round(coverage_score, 1),
            'study_hours': round(hours_score, 1),
            'mock_performance': round(mock_score, 1),
            'consistency': round(consistency_score, 1)
        },
        'recommendations': generate_readiness_recommendations(total_score, {
            'coverage': coverage_score,
            'hours': hours_score,
            'mocks': mock_score,
            'consistency': consistency_score
        })
    }

def generate_readiness_recommendations(total_score, breakdown):
    """Generate actionable recommendations based on scores"""
    recommendations = []
    
    if breakdown['coverage'] < 15:
        recommendations.append("Focus on covering more syllabus topics")
    if breakdown['hours'] < 15:
        recommendations.append("Increase daily study hours to 6+")
    if breakdown['mocks'] < 20:
        recommendations.append("Practice more mock tests to improve scores")
    if breakdown['consistency'] < 15:
        recommendations.append("Build a longer study streak for consistency")
    
    if total_score >= 80:
        recommendations.append("Excellent prep! Focus on revision and mock tests")
    elif total_score >= 60:
        recommendations.append("Good progress! Strengthen weak areas")
    else:
        recommendations.append("Intensify preparation across all areas")
    
    return recommendations

def calculate_success_probability():
    """
    Calculate Success Probability (0-100%)
    Based on: Mock scores trend, topic mastery, historical data
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get last 5 mock test scores
    c.execute("""
        SELECT score, created_at
        FROM mock_test_results
        ORDER BY created_at DESC
        LIMIT 5
    """)
    mocks = c.fetchall()
    
    if len(mocks) < 3:
        return {'probability': 0, 'confidence': 'low', 'message': 'Take at least 3 mock tests for accurate prediction'}
    
    # Calculate trend (improving vs declining)
    scores = [m['score'] for m in reversed(mocks)]
    avg_score = sum(scores) / len(scores)
    
    # Simple linear regression to detect trend
    n = len(scores)
    x_mean = (n - 1) / 2
    y_mean = avg_score
    numerator = sum((i - x_mean) * (scores[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    slope = numerator / denominator if denominator != 0 else 0
    
    # Base probability on average score
    base_prob = min(avg_score, 100)
    
    # Adjust for trend
    trend_adjustment = slope * 5  # 5% adjustment per point of slope
    probability = max(0, min(100, base_prob + trend_adjustment))
    
    # Confidence level
    score_variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
    if score_variance < 100:
        confidence = 'high'
    elif score_variance < 300:
        confidence = 'medium'
    else:
        confidence = 'low'
    
    conn.close()
    
    return {
        'probability': round(probability, 1),
        'confidence': confidence,
        'trend': 'improving' if slope > 0 else 'declining',
        'avg_mock_score': round(avg_score, 1),
        'message': f"Based on {len(mocks)} mock tests with {confidence} confidence"
    }

def calculate_optimal_study_time():
    """
    Identify optimal study time based on activity patterns
    Analyzes when user is most productive (completes most tasks, gets highest scores)
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get activity timestamps from various sources
    c.execute("""
        SELECT strftime('%H', created_at) as hour, COUNT(*) as activity_count
        FROM (
            SELECT created_at FROM mock_test_results
            UNION ALL
            SELECT created_at FROM flashcard_reviews
            UNION ALL
            SELECT created_at FROM battle_history
        )
        WHERE created_at >= datetime('now', '-30 days')
        GROUP BY hour
        ORDER BY activity_count DESC
        LIMIT 3
    """)
    
    peak_hours = c.fetchall()
    conn.close()
    
    if not peak_hours:
        return {'message': 'Not enough data to determine optimal study time', 'peak_hours': []}
    
    hours_list = [int(h['hour']) for h in peak_hours]
    
    # Format hours into readable time ranges
    def format_hour(h):
        return f"{h}:00-{h+1}:00" if h < 12 else f"{h}:00-{h+1}:00"
    
    return {
        'peak_hours': hours_list,
        'formatted_times': [format_hour(h) for h in hours_list],
        'recommendation': f"You're most productive between {format_hour(hours_list[0])}",
        'suggestion': "Schedule challenging topics during these peak hours"
    }

def detect_burnout():
    """
    Detect potential burnout based on:
    - Excessive study hours without breaks
    - Declining performance despite high effort
    - Reduced activity after intense periods
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check study hours in last 7 days
    c.execute("""
        SELECT date, study_hours FROM user_stats
        WHERE date >= date('now', '-7 days')
        ORDER BY date DESC
    """)
    recent_hours = c.fetchall()
    
    if len(recent_hours) < 7:
        return {'burnout_risk': 'unknown', 'message': 'Not enough data'}
    
    hours_list = [r['study_hours'] for r in recent_hours]
    avg_hours = sum(hours_list) / len(hours_list)
    
    # Check if hours are excessively high (> 10 hours/day consistently)
    excessive_hours = avg_hours > 10
    
    # Check for declining mock scores despite high effort
    c.execute("""
        SELECT score FROM mock_test_results
        ORDER BY created_at DESC
        LIMIT 3
    """)
    recent_scores = [r['score'] for r in c.fetchall()]
    
    scores_declining = False
    if len(recent_scores) >= 3:
        scores_declining = recent_scores[0] < recent_scores[-1] - 10
    
    # Check for reduced activity (less than half of average in last 2 days)
    recent_activity_low = hours_list[0] < avg_hours / 2 and hours_list[1] < avg_hours / 2
    
    conn.close()
    
    # Determine burnout risk
    risk_factors = sum([excessive_hours, scores_declining, recent_activity_low])
    
    if risk_factors >= 2:
        risk = 'high'
        message = "⚠️ High burnout risk detected! Consider taking a break."
        recommendations = [
            "Take a full day off to recharge",
            "Reduce daily hours to 6-7",
            "Focus on lighter revision instead of new topics"
        ]
    elif risk_factors == 1:
        risk = 'moderate'
        message = "Moderate burnout risk. Monitor your energy levels."
        recommendations = [
            "Include more breaks in your study schedule",
            "Ensure 7-8 hours of sleep",
            "Mix challenging topics with easier revision"
        ]
    else:
        risk = 'low'
        message = "✅ Healthy study pattern detected"
        recommendations = [
            "Maintain current pace",
            "Continue balanced study routine"
        ]
    
    return {
        'burnout_risk': risk,
        'message': message,
        'recommendations': recommendations,
        'avg_study_hours': round(avg_hours, 1),
        'factors': {
            'excessive_hours': excessive_hours,
            'scores_declining': scores_declining,
            'recent_activity_low': recent_activity_low
        }
    }
