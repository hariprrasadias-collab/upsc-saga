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

            except Exception:
                d['full_report'] = {}
                d['way_forward'] = {}

            data.append(d)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@triangulation_bp.route('/extract-actionables', methods=['POST'])
def extract_actionables():
    try:
        data = request.json
        topic = data.get('topic')
        way_forward = data.get('way_forward', {})
        
        if not topic or not way_forward:
             return jsonify({'success': False, 'error': 'Topic and way_forward are required'}), 400
             
        from app.db import get_db
        from datetime import datetime, timedelta
        conn = get_db()
        
        # Calculate due date: tomorrow
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        actions = []
        if isinstance(way_forward, dict):
            for timeframe, action in way_forward.items():
                if action and isinstance(action, str):
                    actions.append(f"[{timeframe.upper()}] {action}")
        elif isinstance(way_forward, list):
            actions = [str(a) for a in way_forward]
        elif isinstance(way_forward, str):
            actions = [way_forward]
            
        inserted = 0
        action_params = []
        for action in actions:
            action_str = str(action)
            title = f"Tactical Payload ({topic}): {action_str[:80]}..."
            action_params.append((1, title, 30, 'intelligence', tomorrow))
            inserted += 1

        if action_params:
            conn.executemany('''
                INSERT INTO tasks (user_id, title, xp_reward, associated_stat, due_date, isCompleted, is_quest)
                VALUES (?, ?, ?, ?, ?, 0, 0)
            ''', action_params)
            
        conn.commit()
        return jsonify({'success': True, 'inserted': inserted})
        
    except Exception as e:
        print(f"Extraction Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
