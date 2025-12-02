from flask import Blueprint, request, jsonify
from app.db import get_db
import sqlite3

mind_palace_bp = Blueprint('mind_palace', __name__)

# --- Locations ---

@mind_palace_bp.route('/locations', methods=['GET'])
def get_locations():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM mind_palace_locations ORDER BY created_at DESC')
    locations = [dict(row) for row in cursor.fetchall()]
    return jsonify(locations)

@mind_palace_bp.route('/locations', methods=['POST'])
def create_location():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO mind_palace_locations (name, description, image_url, layout_type)
            VALUES (?, ?, ?, ?)
        ''', (data['name'], data.get('description', ''), data.get('image_url', ''), data.get('layout_type', 'grid')))
        conn.commit()
        return jsonify({'message': 'Location created', 'id': cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mind_palace_bp.route('/locations/<int:id>', methods=['DELETE'])
def delete_location(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM mind_palace_locations WHERE id = ?', (id,))
    conn.commit()
    return jsonify({'message': 'Location deleted'})

# --- Artifacts ---

@mind_palace_bp.route('/locations/<int:location_id>/artifacts', methods=['GET'])
def get_artifacts(location_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM mind_palace_artifacts WHERE location_id = ?', (location_id,))
    artifacts = [dict(row) for row in cursor.fetchall()]
    return jsonify(artifacts)

@mind_palace_bp.route('/artifacts', methods=['POST'])
def create_artifact():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO mind_palace_artifacts (location_id, title, content, type, x_position, y_position, color, icon)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['location_id'], 
            data['title'], 
            data.get('content', ''), 
            data.get('type', 'note'),
            data.get('x_position', 0),
            data.get('y_position', 0),
            data.get('color', '#ffffff'),
            data.get('icon', '📝')
        ))
        conn.commit()
        return jsonify({'message': 'Artifact placed', 'id': cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mind_palace_bp.route('/artifacts/<int:id>', methods=['PUT'])
def update_artifact(id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    try:
        # Dynamic update based on provided fields
        fields = []
        values = []
        for key in ['title', 'content', 'x_position', 'y_position', 'color', 'icon']:
            if key in data:
                fields.append(f"{key} = ?")
                values.append(data[key])
        
        if not fields:
            return jsonify({'message': 'No fields to update'}), 400
            
        values.append(id)
        query = f"UPDATE mind_palace_artifacts SET {', '.join(fields)} WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        return jsonify({'message': 'Artifact updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mind_palace_bp.route('/artifacts/<int:id>', methods=['DELETE'])
def delete_artifact(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM mind_palace_artifacts WHERE id = ?', (id,))
    conn.commit()
    return jsonify({'message': 'Artifact removed'})
