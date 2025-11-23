from flask import Blueprint, request, jsonify
from app.db import get_db

bp = Blueprint('mimir', __name__, url_prefix='/api/mimir')

@bp.route('/history', methods=['GET'])
def mimir_hist():
    conn = get_db()
    c = conn.execute('SELECT * FROM mimir_history WHERE user_id=1 ORDER BY id ASC').fetchall()
    return jsonify([dict(x) for x in c])

@bp.route('/ask', methods=['POST'])
def mimir_ask():
    d = request.get_json()
    msg = d.get('message', '')
    conn = get_db()
    
    # Check for Upgrade
    has_head = conn.execute("SELECT 1 FROM inventory WHERE user_id=1 AND item_id='mimir_head'").fetchone()
    
    conn.execute("INSERT INTO mimir_history (user_id, sender, message) VALUES (1, 'user', ?)", (msg,))
    
    # Brain Logic
    lower = msg.lower()
    resp = "I do not know that yet, Brother. (Check your API Key if you want real answers)"
    if "polity" in lower: resp = "The Constitution is the supreme law."
    elif "history" in lower: resp = "The past defines the future."
    
    if has_head:
        resp += " (Mimir's Head Upgrade Active: Deeper Insight Unlocked)"
        
    conn.execute("INSERT INTO mimir_history (user_id, sender, message) VALUES (1, 'mimir', ?)", (resp,))
    conn.commit()
    return jsonify({"response": resp})

@bp.route('/clear', methods=['DELETE'])
def mimir_clear():
    conn = get_db()
    conn.execute('DELETE FROM mimir_history WHERE user_id=1')
    conn.commit()
    return jsonify({"msg": "cleared"})
