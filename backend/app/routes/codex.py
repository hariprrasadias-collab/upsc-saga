from flask import Blueprint, request, jsonify
from app.db import get_db

bp = Blueprint('codex', __name__, url_prefix='/api/codex')

@bp.route('/progress', methods=['GET'])
def get_codex_p():
    conn = get_db()
    rows = conn.execute('SELECT node_id, status FROM user_progress WHERE user_id=1').fetchall()
    return jsonify({r['node_id']: r['status'] for r in rows})

@bp.route('/update', methods=['POST'])
def upd_codex():
    d = request.get_json()
    conn = get_db()
    conn.execute('INSERT INTO user_progress (user_id, node_id, status) VALUES (1, ?, ?) ON CONFLICT(user_id, node_id) DO UPDATE SET status=excluded.status', (d['node_id'], d['status']))
    conn.commit()
    return jsonify({"msg": "ok"})
