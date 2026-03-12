from flask import Blueprint, request, jsonify, session
from app.db import get_db

bp = Blueprint('lore', __name__, url_prefix='/api/lore')

@bp.route('', methods=['GET', 'POST'])
def handle_lore():
    user_id = session.get('user_id') or 1
    conn = get_db()
    if request.method == 'GET':
        n = conn.execute('SELECT * FROM lore_tablets WHERE user_id=? ORDER BY id DESC', (user_id,)).fetchall()
        return jsonify([dict(x) for x in n])
    elif request.method == 'POST':
        d = request.get_json()
        conn.execute('INSERT INTO lore_tablets (user_id, title, content) VALUES (?, ?, ?)', (user_id, d.get('title'), d.get('content')))
        conn.commit()
        return jsonify({"msg": "ok"})

@bp.route('/<int:nid>', methods=['PUT', 'DELETE'])
def mod_lore(nid):
    user_id = session.get('user_id') or 1
    conn = get_db()
    # verify ownership before mod
    existing = conn.execute('SELECT * FROM lore_tablets WHERE id=? AND user_id=?', (nid, user_id)).fetchone()
    if not existing:
        return jsonify({"error": "Unauthorized"}), 403

    if request.method == 'PUT':
        d = request.get_json()
        conn.execute('UPDATE lore_tablets SET title=?, content=? WHERE id=? AND user_id=?', (d['title'], d['content'], nid, user_id))
    else:
        conn.execute('DELETE FROM lore_tablets WHERE id=? AND user_id=?', (nid, user_id))
    conn.commit()
    return jsonify({"msg": "ok"})
