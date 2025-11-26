# backend/app/db_models/current_affairs.py
"""
Database operations for UPSC Current Affairs
"""
from app.db import get_db
import json
from datetime import datetime

def init_current_affairs_table():
    """Initialize the current_affairs table"""
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS current_affairs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            original_link TEXT,
            source TEXT,
            published_date TEXT,
            fetch_date TEXT DEFAULT CURRENT_TIMESTAMP,
            original_summary TEXT,
            upsc_summary TEXT,
            key_points TEXT,
            papers TEXT,
            subjects TEXT,
            importance INTEGER DEFAULT 2,
            is_bookmarked BOOLEAN DEFAULT 0,
            user_notes TEXT,
            anki_card_id INTEGER DEFAULT NULL,
            image_url TEXT,
            related_pyqs TEXT
        )
    ''')
    conn.commit()

def article_exists(link):
    """Check if article with link already exists"""
    conn = get_db()
    cursor = conn.execute('SELECT id FROM current_affairs WHERE original_link = ?', (link,))
    return cursor.fetchone() is not None

def save_article(article_data):
    """Save a new article to database"""
    conn = get_db()
    cursor = conn.execute('''
        INSERT INTO current_affairs (
            title, original_link, source, published_date,
            original_summary, upsc_summary, key_points,
            papers, subjects, importance, image_url, related_pyqs
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        article_data['title'],
        article_data['link'],
        article_data['source'],
        article_data['published'],
        article_data.get('original_summary', ''),
        article_data.get('upsc_summary', ''),
        json.dumps(article_data.get('key_points', [])),
        json.dumps(article_data.get('papers', [])),
        json.dumps(article_data.get('subjects', [])),
        article_data.get('importance', 2),
        article_data.get('image_url', ''),
        json.dumps(article_data.get('related_pyqs', []))
    ))
    conn.commit()
    return cursor.lastrowid

def get_saved_articles(filters=None):
    """Get saved articles with optional filters"""
    conn = get_db()
    query = 'SELECT * FROM current_affairs WHERE 1=1'
    params = []
    
    if filters:
        if filters.get('paper'):
            query += ' AND papers LIKE ?'
            params.append(f'%{filters["paper"]}%')
        
        if filters.get('subject'):
            query += ' AND subjects LIKE ?'
            params.append(f'%{filters["subject"]}%')
        
        if filters.get('importance'):
            query += ' AND importance = ?'
            params.append(filters['importance'])
        
        if filters.get('bookmarked'):
            query += ' AND is_bookmarked = 1'
        
        if filters.get('search'):
            query += ' AND (title LIKE ? OR upsc_summary LIKE ?)'
            search_term = f'%{filters["search"]}%'
            params.extend([search_term, search_term])
    
    query += ' ORDER BY fetch_date DESC'
    
    rows = conn.execute(query, params).fetchall()
    
    articles = []
    for row in rows:
        articles.append({
            'id': row['id'],
            'title': row['title'],
            'link': row['original_link'],
            'source': row['source'],
            'published': row['published_date'],
            'fetchDate': row['fetch_date'],
            'originalSummary': row['original_summary'],
            'upscSummary': row['upsc_summary'],
            'keyPoints': json.loads(row['key_points'] or '[]'),
            'papers': json.loads(row['papers'] or '[]'),
            'subjects': json.loads(row['subjects'] or '[]'),
            'importance': row['importance'],
            'isBookmarked': bool(row['is_bookmarked']),
            'userNotes': row['user_notes'],
            'ankiCardId': row['anki_card_id'],
            'imageUrl': row['image_url'],
            'relatedPyqs': json.loads(row['related_pyqs'] or '[]')
        })
    
    return articles

def update_article_tags(article_id, papers, subjects):
    """Update article tags"""
    conn = get_db()
    conn.execute('''
        UPDATE current_affairs 
        SET papers = ?, subjects = ?
        WHERE id = ?
    ''', (json.dumps(papers), json.dumps(subjects), article_id))
    conn.commit()

def update_article_importance(article_id, importance):
    """Update article importance"""
    conn = get_db()
    conn.execute('''
        UPDATE current_affairs 
        SET importance = ?
        WHERE id = ?
    ''', (importance, article_id))
    conn.commit()

def toggle_bookmark(article_id):
    """Toggle bookmark status"""
    conn = get_db()
    current = conn.execute(
        'SELECT is_bookmarked FROM current_affairs WHERE id = ?',
        (article_id,)
    ).fetchone()
    
    new_status = 0 if current['is_bookmarked'] else 1
    conn.execute('''
        UPDATE current_affairs 
        SET is_bookmarked = ?
        WHERE id = ?
    ''', (new_status, article_id))
    conn.commit()
    return bool(new_status)

def update_user_notes(article_id, notes):
    """Update user notes"""
    conn = get_db()
    conn.execute('''
        UPDATE current_affairs 
        SET user_notes = ?
        WHERE id = ?
    ''', (notes, article_id))
    conn.commit()

    conn.execute('''
        UPDATE current_affairs 
        SET anki_card_id = ?
        WHERE id = ?
    ''', (anki_card_id, article_id))
    conn.commit()

def link_anki_card(article_id, anki_card_id):
    """Link article to Anki card"""
    conn = get_db()
    conn.execute('''
        UPDATE current_affairs 
        SET anki_card_id = ?
        WHERE id = ?
    ''', (anki_card_id, article_id))
    conn.commit()

def update_article_content_by_link(link, article_data):
    """Update article content by link (for re-processing)"""
    conn = get_db()
    conn.execute('''
        UPDATE current_affairs 
        SET upsc_summary = ?,
            key_points = ?,
            papers = ?,
            subjects = ?,
            importance = ?,
            image_url = ?,
            related_pyqs = ?,
            fetch_date = CURRENT_TIMESTAMP
        WHERE original_link = ?
    ''', (
        article_data.get('upsc_summary', ''),
        json.dumps(article_data.get('key_points', [])),
        json.dumps(article_data.get('papers', [])),
        json.dumps(article_data.get('subjects', [])),
        article_data.get('importance', 2),
        article_data.get('image_url', ''),
        json.dumps(article_data.get('related_pyqs', [])),
        link
    ))
    conn.commit()
    
    # Return the ID
    cursor = conn.execute('SELECT id FROM current_affairs WHERE original_link = ?', (link,))
    row = cursor.fetchone()
    return row['id'] if row else None
