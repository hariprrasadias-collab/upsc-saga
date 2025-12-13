"""
Enhanced Visualizations Service
Provides data for Progress Heatmap and Revision Curve
"""
import sqlite3
from datetime import datetime, timedelta
import json

def get_db_connection():
    conn = sqlite3.connect('upsc_saga.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_daily_activity_heatmap(days=365):
    """
    Get daily activity intensity for the last N days (for GitHub-style heatmap)
    Returns: [{ date: 'YYYY-MM-DD', intensity: 0-10 }]
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get activity data from multiple sources
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    # First check if user_stats table exists and has data
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_stats'")
    table_exists = c.fetchone()
    
    heatmap_data = []
    
    if table_exists:
        c.execute("""
            SELECT 
                date,
                COALESCE(study_hours, 0) as study_hours,
                COALESCE(activities_completed, 0) as activities
            FROM user_stats
            WHERE date >= ?
            ORDER BY date
        """, (start_date,))
        
        stats = c.fetchall()
        
        # Calculate intensity score (0-10 scale)
        for row in stats:
            # Intensity = (study_hours * 1) + (activities * 0.5), capped at 10
            intensity = min(10, int((row['study_hours'] * 1) + (row['activities'] * 0.5)))
            
            heatmap_data.append({
                'date': row['date'],
                'intensity': intensity,
                'study_hours': row['study_hours'],
                'activities': row['activities']
            })
    
    # If no data, return empty array (frontend will handle it)
    conn.close()
    return heatmap_data

def get_revision_curve_data(deck_id=None):
    """
    Get spaced repetition effectiveness data (forgetting curve)
    Shows retention rate over time intervals
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get flashcard review data grouped by interval
    query = """
        SELECT 
            CASE 
                WHEN days_since_last < 1 THEN '0-1'
                WHEN days_since_last < 3 THEN '1-3'
                WHEN days_since_last < 7 THEN '3-7'
                WHEN days_since_last < 14 THEN '7-14'
                WHEN days_since_last < 30 THEN '14-30'
                ELSE '30+'
            END as interval_group,
            AVG(CASE WHEN rating >= 3 THEN 100.0 ELSE 0.0 END) as retention_rate,
            COUNT(*) as review_count
        FROM (
            SELECT 
                card_id,
                rating,
                julianday('now') - julianday(reviewed_at) as days_since_last
            FROM flashcard_reviews
            WHERE reviewed_at >= date('now', '-90 days')
            """ + (f" AND deck_id = {deck_id}" if deck_id else "") + """
        )
        GROUP BY interval_group
        ORDER BY interval_group
    """
    
    c.execute(query)
    results = c.fetchall()
    
    # Format for forgetting curve chart
    curve_data = []
    interval_order = ['0-1', '1-3', '3-7', '7-14', '14-30', '30+']
    
    for interval in interval_order:
        matching = [r for r in results if r['interval_group'] == interval]
        if matching:
            curve_data.append({
                'interval': interval,
                'retention': round(matching[0]['retention_rate'], 1),
                'reviews': matching[0]['review_count']
            })
        else:
            curve_data.append({
                'interval': interval,
                'retention': 0,
                'reviews': 0
            })
    
    conn.close()
    return curve_data

def get_topic_connections():
    """
    Get topic relationships for knowledge graph
    Returns nodes and edges for D3.js force-directed graph
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get all topics with their subjects
    c.execute("""
        SELECT 
            id as topic_id,
            topic_name,
            subject,
            status,
            COALESCE(completion_percentage, 0) as completion
        FROM syllabus_topics
    """)
    
    topics = c.fetchall()
    
    # Create nodes
    nodes = []
    for topic in topics:
        nodes.append({
            'id': f"topic_{topic['topic_id']}",
            'name': topic['topic_name'],
            'subject': topic['subject'],
            'status': topic['status'],
            'completion': topic['completion'],
            'group': topic['subject']  # Group by subject for color coding
        })
    
    # Create edges (connections between topics of same subject or related topics)
    edges = []
    subject_topics = {}
    
    # Group topics by subject
    for topic in topics:
        subject = topic['subject']
        if subject not in subject_topics:
            subject_topics[subject] = []
        subject_topics[subject].append(topic['topic_id'])
    
    # Connect topics within same subject
    for subject, topic_ids in subject_topics.items():
        for i, topic_id in enumerate(topic_ids):
            # Connect to next topic in same subject (chain)
            if i < len(topic_ids) - 1:
                edges.append({
                    'source': f"topic_{topic_id}",
                    'target': f"topic_{topic_ids[i+1]}",
                    'type': 'sequential'
                })
    
    conn.close()
    
    return {
        'nodes': nodes,
        'edges': edges
    }

def get_predictive_heatmap(user_id=1):
    """
    PHASE 13: THE CARTOGRAPHER
    Generates a 'Predictive Heatmap' using AI.
    It predicts where the user needs to focus based on Weak Areas vs. High Yield Trends.
    """
    from app.services.model_manager import model_manager
    if not model_manager.is_configured:
        return {"error": "AI Offline"}

    conn = get_db_connection()
    c = conn.cursor()

    # 1. Gather Data
    weak_areas = c.execute('SELECT topic, priority_score FROM weak_area_analysis WHERE user_id = ? ORDER BY priority_score DESC LIMIT 10', (user_id,)).fetchall()
    trends = c.execute('SELECT topic, question_count FROM trending_topics ORDER BY question_count DESC LIMIT 10').fetchall()

    weak_str = ", ".join([f"{w['topic']} ({w['priority_score']})" for w in weak_areas])
    trend_str = ", ".join([f"{t['topic']} ({t['question_count']})" for t in trends])

    # 2. AI Synthesis
    prompt = f"""
    # MISSION: GENERATE PREDICTIVE HEATMAP DATA
    **User Weaknesses:** {weak_str}
    **Global Trends:** {trend_str}

    **DIRECTIVE:**
    Identify 5 "Hotspots" where User Weakness overlaps with Global Trends (High Yield).

    **OUTPUT SCHEMA (JSON):**
    [
        {{ "topic": "Name", "urgency": 0-100, "reason": "High Trend + Low Accuracy" }}
    ]
    """

    try:
        response = model_manager.generate_content(prompt, model_type='fast')
        import json
        text = response.text.strip().replace('```json', '').replace('```', '')
        data = json.loads(text)
        return data
    except Exception as e:
        return [{"topic": "Error generating heatmap", "urgency": 0, "reason": str(e)}]
    finally:
        conn.close()
