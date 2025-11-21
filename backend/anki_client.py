# /backend/anki_client.py
import requests
import json

# AnkiConnect default URL
ANKI_CONNECT_URL = 'http://127.0.0.1:8765'

def fetch_due_cards(deck_name="UPSC"):
    """
    Connects to local Anki instance via AnkiConnect to get due card count.
    Returns Total Due (New + Learn + Review).
    Returns 0 if Anki is not running or deck not found.
    """
    # Payload to get detailed stats for a specific deck
    payload = {
        "action": "getDeckStats",
        "params": {"decks": [deck_name]},
        "version": 6
    }

    try:
        # Send POST request to AnkiConnect
        response = requests.post(ANKI_CONNECT_URL, json=payload, timeout=2)
        response_data = response.json()

        if response_data.get("error"):
            print(f"AnkiConnect Error: {response_data['error']}")
            return 0

        # Extract stats for the requested deck
        # --- THE FIX IS HERE ---
        # AnkiConnect's getDeckStats returns a dictionary where keys are deck IDs
        # and values are the stats objects. We need to iterate or find the correct one.
        # The easiest way is to get the first (and only) deck's stats from the 'result'
        # as we only requested one deck in params.
        
        decks_stats_by_id = response_data.get("result", {})
        
        # Check if any stats were returned.
        if not decks_stats_by_id:
            print(f"No stats returned for deck '{deck_name}'. It might not exist or be empty.")
            return 0

        # Since we requested stats for only one deck (by name), we expect only one entry.
        # However, the key is the deck ID, not the name.
        # So we just grab the first value in the dictionary.
        deck_stat = next(iter(decks_stats_by_id.values()), None)

        if not deck_stat:
            print(f"Stats object not found for deck '{deck_name}' in AnkiConnect response.")
            return 0
        # --- END OF FIX ---

        # Calculate total cards due today
        total_due = (
            deck_stat.get("new_count", 0) +
            deck_stat.get("learn_count", 0) +
            deck_stat.get("review_count", 0)
        )
        
        return total_due

    except requests.exceptions.ConnectionError:
        print("Could not connect to Anki. Is the app running with AnkiConnect?")
        return 0
    except Exception as e:
        print(f"Unexpected error communicating with Anki: {e}")
        return 0
if __name__ == '__main__':
    print("--- DEBUGGING ANKI CONNECTION ---")
    
    # 1. Ask Anki what decks it actually sees
    try:
        debug_payload = {
            "action": "deckNames",
            "version": 6
        }
        print("Asking Anki for list of deck names...")
        debug_response = requests.post(ANKI_CONNECT_URL, json=debug_payload, timeout=2)
        decks_found = debug_response.json().get("result", [])
        print(f"Anki found these decks: {decks_found}")

        target_deck = "UPSC"
        if target_deck in decks_found:
            print(f"\nSuccess! '{target_deck}' is in the list.")
        else:
            print(f"\nFAILURE: '{target_deck}' is NOT exactly matching anything in the list above.")
            print("Please check for exact case sensitivity and trailing spaces in Anki.")

    except Exception as e:
        print(f"Debug connection failed: {e}")

    print("\n--- RUNNING ORIGINAL TEST ---")
    # 2. Run the original test function
    due_count = fetch_due_cards()
    print(f"Total cards due in 'UPSC' deck: {due_count}")