from flask import Blueprint, request, jsonify, g
from app.db import get_db
import json
import time

visual_bp = Blueprint('visual_bp', __name__)

@visual_bp.route('/save', methods=['POST'])
def save_visual():
    try:
        data = request.json
        url = data.get('url')
        prompt = data.get('prompt', '')
        seed = data.get('seed', 0)
        model = data.get('model', 'flux')
        meta_tags = json.dumps(data.get('tags', []))

        if not url:
            return jsonify({"success": False, "message": "URL is required"}), 400

        conn = get_db()
        conn.execute('''
            INSERT INTO visual_gallery (url, prompt, seed, model, meta_tags)
            VALUES (?, ?, ?, ?, ?)
        ''', (url, prompt, seed, model, meta_tags))
        conn.commit()

        return jsonify({"success": True, "message": "Image saved to gallery"})
    
    except Exception as e:
        print(f"Visual Save Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@visual_bp.route('/history', methods=['GET'])
def get_visual_history():
    try:
        conn = get_db()
        # Fetch last 50 images
        cursor = conn.execute('''
            SELECT url, prompt, seed, model, timestamp, meta_tags 
            FROM visual_gallery 
            ORDER BY id DESC LIMIT 50
        ''')
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            history.append({
                "url": row['url'],
                "prompt": row['prompt'],
                "seed": row['seed'],
                "model": row['model'],
                "timestamp": row['timestamp'], # SQLite returns string or None usually
                "tags": json.loads(row['meta_tags']) if row['meta_tags'] else []
            })

        return jsonify({"success": True, "data": history})

    except Exception as e:
        print(f"Visual History Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
