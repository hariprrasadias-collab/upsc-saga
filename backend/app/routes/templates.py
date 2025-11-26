from flask import Blueprint, jsonify
import json
import os

bp = Blueprint('templates', __name__, url_prefix='/api/templates')

# Load templates from JSON file
TEMPLATES_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'answer_templates.json')

def load_templates():
    """Load answer templates from JSON file"""
    try:
        with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['templates']
    except Exception as e:
        print(f"Error loading templates: {e}")
        return []

@bp.route('/list', methods=['GET'])
def get_templates():
    """Get all answer templates"""
    templates = load_templates()
    return jsonify({
        'success': True,
        'templates': templates
    })

@bp.route('/<template_id>', methods=['GET'])
def get_template(template_id):
    """Get a specific template by ID"""
    templates = load_templates()
    template = next((t for t in templates if t['id'] == template_id), None)
    
    if template:
        return jsonify({
            'success': True,
            'template': template
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Template not found'
        }), 404
