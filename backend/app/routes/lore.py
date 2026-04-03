from flask import Blueprint, request, jsonify
from app.db import get_db
from app.utils.session import get_current_user_id

bp = Blueprint('lore', __name__, url_prefix='/api/lore')

@bp.route('', methods=['GET', 'POST'])
def handle_lore():
    conn = get_db()
    user_id = get_current_user_id()
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
    conn = get_db()
    user_id = get_current_user_id()
    if request.method == 'PUT':
        d = request.get_json()
        conn.execute('UPDATE lore_tablets SET title=?, content=? WHERE id=? AND user_id=?', (d['title'], d['content'], nid, user_id))
    else:
        conn.execute('DELETE FROM lore_tablets WHERE id=? AND user_id=?', (nid, user_id))
    conn.commit()
    return jsonify({"msg": "ok"})
