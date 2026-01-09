from flask import Blueprint, request, jsonify
from app.db import get_db
import anki_client

bp = Blueprint('anki', __name__, url_prefix='/api/anki')

@bp.route('/queue', methods=['GET'])
def get_anki_queue():
    # Get all due cards
    ids = anki_client.get_due_card_ids("UPSC") # Change "UPSC" to your actual deck name in Anki
    if ids is None:
        return jsonify([]) # Anki not running
    return jsonify(ids)

@bp.route('/card', methods=['POST'])
def get_anki_card():
    data = request.get_json()
    card_id = data.get('card_id')
    info_list = anki_client.get_cards_info([card_id])
    
    if info_list and len(info_list) > 0:
        card = info_list[0]

        # Sanitize HTML from Anki cards to prevent XSS
        from app.utils.security import sanitize_html
        safe_question = sanitize_html(card.get('question', ''))
        safe_answer = sanitize_html(card.get('answer', ''))

        # Extract just what we need. Anki CSS usually comes in the 'css' field if needed.
        return jsonify({
            'id': card['cardId'],
            'question': safe_question,
            'answer': safe_answer,
            'deckName': card['deckName'],
            'modelName': card['modelName']
        })
    return jsonify({"error": "Card not found"}), 404

@bp.route('/answer', methods=['POST'])
def answer_anki_card():
    data = request.get_json()
    card_id = data.get('card_id')
    ease = data.get('ease') # 1, 2, 3, 4
    
    result = anki_client.answer_card(card_id, ease)
    
    # Give XP for studying!
    user_id = 1
    xp_gain = 10 # Small consistent XP
    
    from app.services.game_engine import calculate_and_apply_rewards
    rewards = calculate_and_apply_rewards(user_id, xp_gain, 0, ['anki', 'memory'])
    
    return jsonify({"success": True, "xp_gained": rewards['xp_gained'], "leveled_up": rewards['leveled_up']})
