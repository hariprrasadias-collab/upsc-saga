# backend/app/services/pyq_analytics.py
"""
PYQ Analytics Engine
Analyzes the PYQ database to generate heatmap data and statistics
"""
import sqlite3
import os
from collections import defaultdict
from typing import List, Dict, Tuple, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'upsc_saga.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def analyze_pyq_distribution(
    paper: Optional[str] = None,
    year_start: Optional[int] = None,
    year_end: Optional[int] = None,
    topic: Optional[str] = None,
    subject: Optional[str] = None
) -> Dict:
    """
    Analyze PYQ database to generate heatmap data
    
    Args:
        paper: Filter by paper (not used - column doesn't exist)
        year_start: Start year for range
        year_end: End year for range
        topic: Filter by topic name
        subject: Filter by subject name
    
    Returns:
        {
            'heatmap_data': [[topic, year, count], ...],
            'topics': [unique topics],
            'years': [unique years],
            'stats': {summary statistics}
        }
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Build query with filters
    query = """
        SELECT year, topic, COUNT(*) as count
        FROM pyq_questions
        WHERE 1=1
    """
    params = []
    
    if year_start:
        query += " AND year >= ?"
        params.append(year_start)
    
    if year_end:
        query += " AND year <= ?"
        params.append(year_end)
    
    if topic:
        query += " AND topic LIKE ?"
        params.append(f"%{topic}%")
    
    if subject:
        query += " AND subject = ?"
        params.append(subject)
    
    query += " GROUP BY year, topic ORDER BY year, topic"
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    # Process results into heatmap format
    heatmap_data = []
    topics_set = set()
    years_set = set()
    total_questions = 0
    topic_counts = defaultdict(int)
    year_counts = defaultdict(int)
    
    for row in results:
        year = row['year']
        topic_name = row['topic']
        count = row['count']
        
        heatmap_data.append([topic_name, year, count])
        topics_set.add(topic_name)
        years_set.add(year)
        total_questions += count
        topic_counts[topic_name] += count
        year_counts[year] += count
    
    # Get most asked topic
    most_asked_topic = max(topic_counts.items(), key=lambda x: x[1]) if topic_counts else (None, 0)
    most_active_year = max(year_counts.items(), key=lambda x: x[1]) if year_counts else (None, 0)
    
    conn.close()
    
    return {
        'heatmap_data': heatmap_data,
        'topics': sorted(list(topics_set)),
        'years': sorted(list(years_set)),
        'stats': {
            'total_questions': total_questions,
            'unique_topics': len(topics_set),
            'year_range': f"{min(years_set)}-{max(years_set)}" if years_set else "N/A",
            'most_asked_topic': most_asked_topic[0],
            'most_asked_count': most_asked_topic[1],
            'most_active_year': most_active_year[0],
            'questions_in_active_year': most_active_year[1]
        }
    }

def get_topic_trend(topic: str, paper: Optional[str] = None) -> List[Dict]:
    """Get year-wise trend for a specific topic"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = """
        SELECT year, COUNT(*) as count
        FROM pyq_questions
        WHERE topic = ?
        GROUP BY year ORDER BY year
    """
    
    cursor.execute(query, [topic])
    results = cursor.fetchall()
    conn.close()
    
    return [{'year': row['year'], 'count': row['count']} for row in results]

def get_questions_by_cell(topic: str, year: int, paper: Optional[str] = None) -> List[Dict]:
    """
    Get all questions for a specific topic-year combination
    
    Args:
        topic: Topic name
        year: Year
        paper: Not used (column doesn't exist)
    
    Returns:
        List of questions with complete details
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Get ALL question fields for the frontend modal
    query = """
        SELECT 
            id, 
            question_text,
            option_a,
            option_b,
            option_c,
            option_d,
            correct_option,
            explanation,
            year,
            subject,
            topic,
            difficulty
        FROM pyq_questions
        WHERE topic = ? AND year = ?
        ORDER BY id
    """
    
    cursor.execute(query, [topic, year])
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]

def get_paper_distribution() -> Dict:
    """Get question distribution across subjects (not papers)"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT subject, COUNT(*) as count
        FROM pyq_questions
        GROUP BY subject
        ORDER BY subject
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    return {row['subject']: row['count'] for row in results}
