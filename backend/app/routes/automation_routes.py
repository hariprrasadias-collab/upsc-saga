from flask import Blueprint, jsonify, request
from app.db import get_db
import json

automation_bp = Blueprint('automation_content', __name__)

@automation_bp.route('/content', methods=['GET'])
def get_content():
    """
    Get AI generated content with optional filtering.
    QueryParams:
    - type: Filter by content_type (e.g., 'podcast', 'essay')
    - topic: Filter by topic string (partial match)
    - limit: Max items (default 20)
    """
    type_filter = request.args.get('type')
    topic_filter = request.args.get('topic')
    limit = request.args.get('limit', 20)
    
    conn = get_db()
    
    query = "SELECT * FROM ai_generated_content WHERE 1=1"
    params = []
    
    if type_filter:
        query += " AND content_type = ?"
        params.append(type_filter)
        
    if topic_filter:
        query += " AND topic LIKE ?"
        params.append(f"%{topic_filter}%")
        
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor = conn.execute(query, params)
    rows = cursor.fetchall()
    
    results = []
    for row in rows:
        item = dict(row)
        # Parse metadata JSON if it exists
        if item.get('metadata'):
            try:
                item['metadata'] = json.loads(item['metadata'])
            except Exception:
                item['metadata'] = {}
        results.append(item)
        
    return jsonify({
        "success": True,
        "count": len(results),
        "data": results
    })

@automation_bp.route('/content/<int:id>', methods=['GET'])
def get_content_by_id(id):
    conn = get_db()
    row = conn.execute('SELECT * FROM ai_generated_content WHERE id = ?', (id,)).fetchone()
    
    if not row:
        return jsonify({"success": False, "message": "Content not found"}), 404
        
    item = dict(row)
    if item.get('metadata'):
        try:
            item['metadata'] = json.loads(item['metadata'])
        except Exception:
            item['metadata'] = {}
            
    return jsonify({"success": True, "data": item})

@automation_bp.route('/content/<int:id>', methods=['DELETE'])
def delete_content(id):
    conn = get_db()
    conn.execute('DELETE FROM ai_generated_content WHERE id = ?', (id,))
    conn.commit()
    return jsonify({"success": True, "message": "Content deleted"})
