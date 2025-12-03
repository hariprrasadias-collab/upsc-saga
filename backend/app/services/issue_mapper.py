"""
AI-powered Issue Mapping Service
Maps current affairs articles to UPSC syllabus topics using Gemini
"""
import os
import json
import sqlite3
import google.generativeai as genai
from typing import Dict, List, Optional
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'upsc_saga.db')
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def map_article_to_syllabus(article_id: int) -> List[Dict]:
    """
    Analyze a current affairs article and map it to syllabus topics using AI
    
    Args:
        article_id: ID of the article in current_affairs table
        
    Returns:
        List of mappings with topics, subjects, relevance scores
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Fetch article content
    cursor.execute("SELECT title, upsc_summary FROM current_affairs WHERE id = ?", (article_id,))
    article = cursor.fetchone()
    
    if not article:
        conn.close()
        return []
    
    # Prepare AI prompt
    prompt = f"""
You are a UPSC exam expert. Analyze this current affairs article and map it to relevant UPSC syllabus topics.

Article Title: {article['title']}
Article Content: {article['upsc_summary'][:2000]}

For each mapping, provide:
1. Subject area (e.g., Polity, Economy, Geography, IR, etc.)
2. Specific syllabus topic
3. Which GS paper (GS1/GS2/GS3/GS4)
4. Relevance score (0.0 to 1.0)
5. Key linkages: How this news connects to the topic
6. Exam utility: Potential question angles

Return ONLY a JSON array with this structure:
[
  {{
    "subject": "Polity",
    "syllabus_topic": "Constitutional Bodies",
    "paper": "GS2",
    "relevance_score": 0.85,
    "key_linkages": "Article discusses Election Commission reforms which directly relates to constitutional bodies",
    "exam_utility": "Can be asked about powers, independence, and recent reforms of EC"
  }}
]

Provide 2-4 most relevant mappings. Be specific and exam-focused.
"""
    
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        
        # Parse AI response
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        mappings = json.loads(response_text.strip())
        
        # Save mappings to database
        saved_mappings = []
        for mapping in mappings:
            cursor.execute('''
                INSERT INTO issue_mappings 
                (article_id, subject, syllabus_topic, paper, relevance_score, key_linkages, exam_utility, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article_id,
                mapping.get('subject', ''),
                mapping.get('syllabus_topic', ''),
                mapping.get('paper', ''),
                mapping.get('relevance_score', 0.0),
                mapping.get('key_linkages', ''),
                mapping.get('exam_utility', ''),
                datetime.now()
            ))
            
            saved_mappings.append({
                'id': cursor.lastrowid,
                **mapping
            })
        
        conn.commit()
        conn.close()
        
        return saved_mappings
        
    except Exception as e:
        conn.close()
        print(f"Error mapping article: {e}")
        return []

def get_mappings_for_article(article_id: int) -> List[Dict]:
    """Get all existing mappings for an article"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, subject, syllabus_topic, paper, relevance_score, 
               key_linkages, exam_utility, created_at
        FROM issue_mappings
        WHERE article_id = ?
        ORDER BY relevance_score DESC
    ''', (article_id,))
    
    mappings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return mappings

def get_articles_for_topic(topic: str) -> List[Dict]:
    """Get all articles mapped to a specific syllabus topic"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT ca.id, ca.title, ca.date, ca.source,
               im.relevance_score, im.key_linkages
        FROM current_affairs ca
        JOIN issue_mappings im ON ca.id = im.article_id
        WHERE im.syllabus_topic LIKE ?
        ORDER BY im.relevance_score DESC, ca.date DESC
    ''', (f'%{topic}%',))
    
    articles = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return articles

def get_mapping_stats() -> Dict:
    """Get statistics about issue mappings"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM issue_mappings")
    total_mappings = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(DISTINCT article_id) as mapped FROM issue_mappings")
    mapped_articles = cursor.fetchone()['mapped']
    
    cursor.execute('''
        SELECT subject, COUNT(*) as count 
        FROM issue_mappings 
        GROUP BY subject 
        ORDER BY count DESC 
        LIMIT 5
    ''')
    top_subjects = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        'total_mappings': total_mappings,
        'mapped_articles': mapped_articles,
        'top_subjects': top_subjects
    }
