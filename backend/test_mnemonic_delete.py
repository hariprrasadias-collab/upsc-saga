import requests
import json

BASE_URL = 'http://localhost:5000/api/revision'

def test_mnemonic_lifecycle():
    print("Testing Mnemonic Lifecycle...")
    
    # 1. Create a mnemonic
    print("\n1. Creating mnemonic...")
    payload = {
        'text': 'Mercury Venus Earth Mars Jupiter Saturn Uranus Neptune',
        'type': 'list'
    }
    try:
        response = requests.post(f'{BASE_URL}/mnemonic', json=payload)
        data = response.json()
        
        if data['success']:
            print(f"SUCCESS: Created mnemonic: {data['mnemonic']}")
        else:
            print(f"FAILURE: Could not create mnemonic: {data.get('error')}")
            return
    except Exception as e:
        print(f"ERROR: {e}")
        return

    # 2. Get history to find the ID
    print("\n2. Fetching history...")
    try:
        response = requests.get(f'{BASE_URL}/mnemonic/history')
        data = response.json()
        
        if data['success']:
            history = data['history']
            if not history:
                print("FAILURE: History is empty")
                return
            
            # Get the most recent one (should be the one we just created)
            latest = history[0]
            mnemonic_id = latest['id']
            print(f"SUCCESS: Found latest mnemonic ID: {mnemonic_id}")
        else:
            print(f"FAILURE: Could not fetch history: {data.get('error')}")
            return
    except Exception as e:
        print(f"ERROR: {e}")
        return

    # 3. Delete the mnemonic
    print(f"\n3. Deleting mnemonic ID {mnemonic_id}...")
    try:
        response = requests.delete(f'{BASE_URL}/mnemonic/history/{mnemonic_id}')
        data = response.json()
        
        if data['success']:
            print("SUCCESS: Mnemonic deleted")
        else:
            print(f"FAILURE: Could not delete mnemonic: {data.get('error')}")
            return
    except Exception as e:
        print(f"ERROR: {e}")
        return

    # 4. Verify deletion
    print("\n4. Verifying deletion...")
    try:
        response = requests.get(f'{BASE_URL}/mnemonic/history')
        data = response.json()
        
        if data['success']:
            history = data['history']
            found = any(item['id'] == mnemonic_id for item in history)
            if not found:
                print("SUCCESS: Mnemonic no longer in history")
            else:
                print("FAILURE: Mnemonic still exists in history")
        else:
            print(f"FAILURE: Could not fetch history: {data.get('error')}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_mnemonic_lifecycle()
