from flask import Blueprint, request, jsonify
from app.services.triangulation_service import analyze_topic_triangulation

triangulation_bp = Blueprint('triangulation', __name__)

@triangulation_bp.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        text = data.get('text')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
            
        result = analyze_topic_triangulation(text)
        return jsonify(result)
    except Exception as e:
        print(f"Triangulation Route Error: {e}")
        return jsonify({'error': str(e)}), 500

@triangulation_bp.route('/history', methods=['GET'])
def get_history():
    try:
        from app.db import get_db
        import json
        conn = get_db()
        limit = request.args.get('limit', 20)
        rows = conn.execute('SELECT * FROM triangulation_reports ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
        data = []
        for row in rows:
            d = dict(row)
            try:
                d['way_forward'] = json.loads(d['way_forward'])
            except:
                d['way_forward'] = {}
            data.append(d)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
