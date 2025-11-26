from flask import Blueprint, jsonify, request
from app.db import get_db
from app.services.issue_mapper import (
    map_article_to_syllabus,
    get_mappings_for_article,
    get_articles_for_topic,
    get_mapping_stats
)

bp = Blueprint('issue_mapping', __name__, url_prefix='/api/issue-mapping')

@bp.route('/analyze', methods=['POST'])
def analyze_article():
    """Trigger AI analysis to map article to syllabus topics"""
    data = request.get_json()
    article_id = data.get('article_id')
    
    if not article_id:
        return jsonify({'success': False, 'error': 'article_id required'}), 400
    
    try:
        mappings = map_article_to_syllabus(article_id)
        
        return jsonify({
            'success': True,
            'mappings': mappings,
            'count': len(mappings)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/article/<int:article_id>', methods=['GET'])
def get_article_mappings(article_id):
    """Get all mappings for a specific article"""
    try:
        mappings = get_mappings_for_article(article_id)
        
        # Fetch tags
        conn = get_db()
        article = conn.execute("SELECT tags FROM current_affairs WHERE id = ?", (article_id,)).fetchone()
        tags = []
        if article and article['tags']:
            tags = article['tags'].split(',')
        
        return jsonify({
            'success': True,
            'article_id': article_id,
            'mappings': mappings,
            'tags': tags,
            'count': len(mappings)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/topic/<topic>', methods=['GET'])
def get_topic_articles(topic):
    """Get all articles mapped to a syllabus topic"""
    try:
        articles = get_articles_for_topic(topic)
        
        return jsonify({
            'success': True,
            'topic': topic,
            'articles': articles,
            'count': len(articles)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/tags', methods=['POST'])
def update_tags():
    """Update tags for an article"""
    data = request.get_json()
    article_id = data.get('article_id')
    tags = data.get('tags') # List of strings
    
    if not article_id:
        return jsonify({'success': False, 'error': 'article_id required'}), 400
        
    conn = get_db()
    try:
        # Convert list to comma-separated string
        tags_str = ",".join(tags) if tags else ""
        
        conn.execute(
            "UPDATE current_affairs SET tags = ? WHERE id = ?", 
            (tags_str, article_id)
        )
        conn.commit()
        
        return jsonify({
            'success': True,
            'article_id': article_id,
            'tags': tags
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/stats', methods=['GET'])
def get_stats():
    """Get overall mapping statistics"""
    try:
        stats = get_mapping_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
