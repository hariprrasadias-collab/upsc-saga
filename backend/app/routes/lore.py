from flask import Blueprint, request, jsonify
from app.db import get_db

bp = Blueprint('lore', __name__, url_prefix='/api/lore')

@bp.route('', methods=['GET', 'POST'])
def handle_lore():
    conn = get_db()
    if request.method == 'GET':
        n = conn.execute('SELECT * FROM lore_tablets WHERE user_id=1 ORDER BY id DESC').fetchall()
        return jsonify([dict(x) for x in n])
    elif request.method == 'POST':
        d = request.get_json()
        conn.execute('INSERT INTO lore_tablets (user_id, title, content) VALUES (1, ?, ?)', (d.get('title'), d.get('content')))
        conn.commit()
        return jsonify({"msg": "ok"})

@bp.route('/<int:nid>', methods=['PUT', 'DELETE'])
def mod_lore(nid):
    conn = get_db()
    if request.method == 'PUT':
        d = request.get_json()
        conn.execute('UPDATE lore_tablets SET title=?, content=? WHERE id=?', (d['title'], d['content'], nid))
    else:
        conn.execute('DELETE FROM lore_tablets WHERE id=?', (nid,))
    conn.commit()
    return jsonify({"msg": "ok"})
