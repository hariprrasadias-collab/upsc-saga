from flask import Blueprint, request, jsonify
from app.db import get_db
import json

csat_bp = Blueprint('csat', __name__)

@csat_bp.route('/api/csat/topics', methods=['GET'])
def get_topics():
    """Get list of available CSAT topics by category"""
    try:
        conn = get_db()
        # Get unique categories and topics
        rows = conn.execute('''
            SELECT DISTINCT category, topic FROM csat_questions
            ORDER BY category, topic
        ''').fetchall()
        
        topics = {}
        for row in rows:
            category = row['category']
            topic = row['topic']
            if category not in topics:
                topics[category] = []
            topics[category].append(topic)
            
        return jsonify(topics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@csat_bp.route('/api/csat/questions', methods=['GET'])
def get_questions():
    """Get questions filtered by category and topic"""
    try:
        category = request.args.get('category')
        topic = request.args.get('topic')
        difficulty = request.args.get('difficulty')
        
        query = 'SELECT * FROM csat_questions WHERE 1=1'
        params = []
        
        if category:
            query += ' AND category = ?'
            params.append(category)
        if topic:
            query += ' AND topic = ?'
            params.append(topic)
        if difficulty:
            query += ' AND difficulty = ?'
            params.append(difficulty)
            
        conn = get_db()
        questions = conn.execute(query, params).fetchall()
        
        result = []
        for q in questions:
            q_dict = dict(q)
            # Parse options JSON
            try:
                q_dict['options'] = json.loads(q_dict['options'])
            except Exception:
                q_dict['options'] = []
            result.append(q_dict)
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@csat_bp.route('/api/csat/formulas', methods=['GET'])
def get_formulas():
    """Get formula sheet data"""
    formulas = {
        "Quant": [
            {
                "title": "Time & Work",
                "content": [
                    "If A can do a work in n days, 1 day's work = 1/n",
                    "If A is twice as good as B, A takes half the time B takes."
                ]
            },
            {
                "title": "Speed, Time & Distance",
                "content": [
                    "Speed = Distance / Time",
                    "Average Speed = (2xy)/(x+y) when distance is same",
                    "Relative Speed (Same Direction) = u - v",
                    "Relative Speed (Opposite Direction) = u + v"
                ]
            },
            {
                "title": "Percentages",
                "content": [
                    "Percentage Change = ((New - Old) / Old) * 100",
                    "A is x% more than B => B is (x/(100+x))*100 % less than A"
                ]
            }
        ],
        "Reasoning": [
            {
                "title": "Syllogism",
                "content": [
                    "All A are B => Some B are A (True)",
                    "No A is B => No B is A (True)",
                    "Some A are B => Some B are A (True)"
                ]
            },
            {
                "title": "Blood Relations",
                "content": [
                    "Father's Son = Brother or Self",
                    "Father's Daughter = Sister",
                    "Mother's Brother = Maternal Uncle"
                ]
            }
        ]
    }
    return jsonify(formulas)
