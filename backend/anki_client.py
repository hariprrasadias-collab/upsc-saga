# /backend/anki_client.py
import requests
import json

ANKI_CONNECT_URL = 'http://127.0.0.1:8765'

def invoke(action, **params):
    """Generic wrapper to call AnkiConnect."""
    requestJson = json.dumps({'action': action, 'params': params, 'version': 6})
    try:
        response = requests.post(ANKI_CONNECT_URL, data=requestJson, timeout=1).json()
        if len(response) != 2:
            raise Exception('response has an unexpected number of fields')
        if 'error' not in response:
            raise Exception('response is missing required error field')
        if 'result' not in response:
            raise Exception('response is missing required result field')
        if response['error'] is not None:
            raise Exception(response['error'])
        return response['result']
    except Exception as e:
        # We print the specific error but don't crash the app
        print(f"AnkiConnect Error ({action}): {e}. Using Mock Data.")
        return mock_invoke(action, **params)

def mock_invoke(action, **params):
    """Returns mock data for testing/development when Anki is not available."""
    if action == 'findCards':
        # Return a list of mock card IDs
        return [101, 102, 103]

    if action == 'cardsInfo':
        cards = params.get('cards', [])
        return [{
            'cardId': card_id,
            'question': f'<h3>Mock Question {card_id}</h3><p>What is the capital of France?</p>',
            'answer': f'<h3>Mock Answer {card_id}</h3><p>Paris</p>',
            'deckName': 'UPSC',
            'modelName': 'Basic'
        } for card_id in cards]

    if action == 'answerCards':
        return [True] * len(params.get('answers', []))

    if action == 'getDeckStats':
        # Return mock stats
        return {'1': {'new_count': 5, 'learn_count': 2, 'review_count': 3}}

    return None

def get_due_card_ids(deck_name="UPSC"):
    """Gets a list of card IDs that are due for review OR new cards ready to learn."""
    # Modified query: Find cards in deck that are due OR new
    # 'is:new' catches cards that have never been studied
    # 'is:due' catches cards that are due for review
    # 'is:learn' catches cards currently in learning phase
    query = f'deck:"{deck_name}" (is:new OR is:due OR is:learn)'
    return invoke('findCards', query=query)

def get_cards_info(card_ids):
    """Gets details (Question/Answer HTML) for specific card IDs."""
    return invoke('cardsInfo', cards=card_ids)

def answer_card(card_id, ease):
    """Submits an answer to Anki (1=Again, 2=Hard, 3=Good, 4=Easy)."""
    return invoke('answerCards', answers=[{'cardId': card_id, 'ease': ease}])

def fetch_due_count(deck_name="UPSC"):
    """Gets the total number of due cards for the sidebar."""
    stats = invoke('getDeckStats', decks=[deck_name])
    if stats:
        # Anki returns a dict where keys are deck IDs. We just take the first value.
        d = list(stats.values())[0]
        return d['new_count'] + d['learn_count'] + d['review_count']
    return 0

# --- TEST BLOCK (Runs only when you type 'python anki_client.py') ---
if __name__ == '__main__':
    print("\n--- 🔍 TESTING ANKI CONNECTION ---")
    
    # Test 1: Check connection and Deck Count
    try:
        print("Attempting to contact AnkiConnect...")
        count = fetch_due_count("UPSC")
        print(f"✅ SUCCESS: Connected to Anki.")
        print(f"📊 Cards due in 'UPSC' deck: {count}")
    except Exception as e:
        print(f"❌ FAILURE: Could not connect. Is Anki open? Error: {e}")

    # Test 2: Fetch Specific Card IDs
    try:
        ids = get_due_card_ids("UPSC")
        if ids:
            print(f"🆔 Found {len(ids)} cards ready to study.")
            print(f"📝 First 3 Card IDs: {ids[:3]}")
            
            # Test 3: Fetch Content for the first card
            if len(ids) > 0:
                print("\n--- FETCHING CARD CONTENT ---")
                info = get_cards_info([ids[0]])
                if info:
                    # We use .get() to avoid crashing if fields are missing
                    q_text = info[0].get('question', 'No Question Found')
                    a_text = info[0].get('answer', 'No Answer Found')
                    print(f"❓ Question Sample: {q_text[:100]}...")
                    print(f"💡 Answer Sample: {a_text[:100]}...")
        else:
            print("⚠️ No cards are currently available (or deck 'UPSC' is empty).")
            
    except Exception as e:
        print(f"❌ Error fetching cards: {e}")
        
    print("----------------------------------\n")