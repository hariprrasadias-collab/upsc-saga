from flask import Blueprint, request, jsonify
from app.db import get_db
from app.utils.session import get_current_user_id

bp = Blueprint('codex', __name__, url_prefix='/api/codex')


@bp.route('/progress', methods=['GET'])
def get_codex_p():
    user_id = get_current_user_id()
    conn = get_db()
    rows = conn.execute('SELECT node_id, status FROM user_progress WHERE user_id=?', (user_id,)).fetchall()
    return jsonify({r['node_id']: r['status'] for r in rows})


@bp.route('/update', methods=['POST'])
def upd_codex():
    user_id = get_current_user_id()
    d = request.get_json()
    conn = get_db()
    conn.execute(
        'INSERT INTO user_progress (user_id, node_id, status) VALUES (?, ?, ?) '
        'ON CONFLICT(user_id, node_id) DO UPDATE SET status=excluded.status',
        (user_id, d['node_id'], d['status'])
    )
    conn.commit()
    return jsonify({"msg": "ok"})
