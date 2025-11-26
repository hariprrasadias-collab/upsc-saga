from flask import Blueprint, jsonify, request
from app.services.pyq_analytics import (
    analyze_pyq_distribution,
    get_topic_trend,
    get_questions_by_cell,
    get_paper_distribution,
    get_db
)

bp = Blueprint('heatmap', __name__, url_prefix='/api/heatmap')

@bp.route('/pyq', methods=['GET'])
def get_pyq_heatmap():
    """Get PYQ heatmap data with optional filters"""
    paper = request.args.get('paper')
    year_start = request.args.get('year_start', type=int)
    year_end = request.args.get('year_end', type=int)
    topic = request.args.get('topic')
    subject = request.args.get('subject')
    
    try:
        data = analyze_pyq_distribution(
            paper=paper,
            year_start=year_start,
            year_end=year_end,
            topic=topic,
            subject=subject
        )
        
        return jsonify({
            'success': True,
            **data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/subjects', methods=['GET'])
def get_all_subjects():
    """Get list of all unique subjects for filtering"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT subject 
            FROM pyq_questions 
            WHERE subject IS NOT NULL AND subject != ''
            ORDER BY subject
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        subjects = [row['subject'] for row in results]
        
        return jsonify({
            'success': True,
            'subjects': subjects
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/stats', methods=['GET'])
def get_heatmap_stats():
    """Get summary statistics for all PYQs"""
    paper = request.args.get('paper')
    
    try:
        data = analyze_pyq_distribution(paper=paper)
        
        return jsonify({
            'success': True,
            'stats': data['stats'],
            'paper_distribution': get_paper_distribution()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/topic/<topic_name>', methods=['GET'])
def get_topic_details(topic_name):
    """Get trend data for a specific topic"""
    paper = request.args.get('paper')
    
    try:
        trend = get_topic_trend(topic_name, paper=paper)
        
        return jsonify({
            'success': True,
            'topic': topic_name,
            'trend': trend
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/cell', methods=['GET'])
def get_cell_questions():
    """Get questions for a specific topic-year cell"""
    topic = request.args.get('topic')
    year = request.args.get('year', type=int)
    paper = request.args.get('paper')
    
    if not topic or not year:
        return jsonify({
            'success': False,
            'error': 'Topic and year are required'
        }), 400
    
    try:
        questions = get_questions_by_cell(topic, year, paper=paper)
        
        return jsonify({
            'success': True,
            'topic': topic,
            'year': year,
            'count': len(questions),
            'questions': questions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/topics', methods=['GET'])
def get_all_topics():
    """Get list of all unique topics for filtering"""
    try:
        data = analyze_pyq_distribution()
        
        return jsonify({
            'success': True,
            'topics': data['topics']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
