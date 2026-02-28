from flask import Blueprint, jsonify, request
from app.db import get_db

bp = Blueprint('automation', __name__, url_prefix='/api/automation')

@bp.route('/content', methods=['GET'])
def get_automation_content():
    """Fetches AI-generated content for the Brain Vault."""
    try:
        conn = get_db()
        filter_type = request.args.get('type', 'all')
        
        if filter_type == 'all':
            # Note: Fetching recently generated robust items.
            rows = conn.execute(
                'SELECT id, content_type, topic, content, metadata, created_at FROM ai_generated_content ORDER BY created_at DESC LIMIT 100'
            ).fetchall()
        else:
            rows = conn.execute(
                'SELECT id, content_type, topic, content, metadata, created_at FROM ai_generated_content WHERE content_type = ? ORDER BY created_at DESC LIMIT 100',
                (filter_type,)
            ).fetchall()
            
        data = []
        for r in rows:
            data.append({
                'id': r['id'],
                'content_type': r['content_type'],
                'topic': r['topic'],
                'content': r['content'],
                'metadata': r['metadata'],
                'created_at': r['created_at']
            })
            
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        print(f"Error fetching automation content: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/content/<int:id>', methods=['DELETE'])
def delete_automation_content(id):
    """Deletes an artifact from the Neural Storage."""
    try:
        conn = get_db()
        conn.execute('DELETE FROM ai_generated_content WHERE id = ?', (id,))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
