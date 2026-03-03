from flask import Blueprint, jsonify, request
from app.services.mindmap_service import MindMapService

bp = Blueprint('mindmap', __name__, url_prefix='/api/mindmap')

@bp.route('/generate', methods=['POST'])
def generate_mindmap():
    """Generate a mind map for a given topic"""
    data = request.get_json()
    topic = data.get('topic')
    
    if not topic:
        return jsonify({'error': 'Topic is required'}), 400

    try:
        mindmap_data = MindMapService.generate_mindmap(topic)
        return jsonify(mindmap_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/deepdive', methods=['POST'])
def deepdive_mindmap():
    """Generate deeper child nodes for a specific node in a mind map"""
    data = request.get_json()
    topic = data.get('topic')
    node_name = data.get('node_name')
    
    if not topic or not node_name:
        return jsonify({'error': 'Topic and node_name are required'}), 400

    try:
        children_data = MindMapService.deep_dive(topic, node_name)
        return jsonify({'success': True, 'children': children_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/save', methods=['POST'])
def save_mindmap():
    """Save a mind map"""
    data = request.get_json()
    title = data.get('title')
    root_node = data.get('root_node')
    
    if not title or not root_node:
        return jsonify({'error': 'Title and root_node are required'}), 400

    try:
        map_id = MindMapService.save_mindmap(title, root_node)
        return jsonify({'id': map_id, 'message': 'Mind map saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/list', methods=['GET'])
def list_mindmaps():
    """List all saved mind maps"""
    try:
        maps = MindMapService.get_all_mindmaps()
        return jsonify(maps)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:map_id>', methods=['GET'])
def get_mindmap(map_id):
    """Get a specific mind map"""
    try:
        mindmap = MindMapService.get_mindmap(map_id)
        if mindmap:
            return jsonify(mindmap)
        return jsonify({'error': 'Mind map not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:map_id>', methods=['DELETE'])
def delete_mindmap(map_id):
    """Delete a specific mind map"""
    try:
        success = MindMapService.delete_mindmap(map_id)
        if success:
            return jsonify({'message': 'Mind map deleted successfully'})
        return jsonify({'error': 'Mind map not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
