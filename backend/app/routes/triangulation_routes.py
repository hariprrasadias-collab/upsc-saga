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

        # Pagination & Filtering
        limit = request.args.get('limit', 20)
        search = request.args.get('search', '')

        query = 'SELECT * FROM triangulation_reports'
        params = []

        if search:
            query += ' WHERE topic LIKE ?'
            params.append(f'%{search}%')

        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)

        rows = conn.execute(query, params).fetchall()

        data = []
        for row in rows:
            d = dict(row)
            try:
                # This could be the full report OR just the way_forward dict (legacy)
                parsed_json = json.loads(d['way_forward'])

                # Check if it's the new Full Report format
                if 'way_forward' in parsed_json or 'core_topic' in parsed_json:
                     d['full_report'] = parsed_json
                     # For backward compatibility with simpler views, ensure way_forward exists
                     d['way_forward'] = parsed_json.get('way_forward', {})
                else:
                    # Legacy: It IS the way_forward dict
                    d['full_report'] = {} # Indicate no full report
                    d['way_forward'] = parsed_json

            except:
                d['full_report'] = {}
                d['way_forward'] = {}

            data.append(d)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
