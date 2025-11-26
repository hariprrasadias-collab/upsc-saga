import requests

def test_revision_features():
    print("Testing Revision Features...\n")
    
    # Test 1: Generate One-Liner
    print("1. Testing One-Liner Generation...")
    response = requests.post('http://localhost:5000/api/revision/one-liner', json={
        'title': 'Preamble of Indian Constitution',
        'content': 'The Preamble declares India as a sovereign, socialist, secular, democratic republic. It outline the objectives of the Constitution and highlights the source of its authority - the people of India.'
    })
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"✅ One-Liner Generated:")
            print(f"   Title: {data['card']['title']}")
            print(f"   Summary: {data['card']['one_liner']}\n")
        else:
            print("❌ Failed\n")
    else:
        print(f"❌ HTTP Error: {response.status_code}\n")
    
    # Test 2: Get Revision Cards
    print("2. Fetching all revision cards...")
    response = requests.get('http://localhost:5000/api/revision/cards')
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"✅ Found {len(data['cards'])} cards\n")
        else:
            print("❌ Failed\n")
    else:
        print(f"❌ HTTP Error: {response.status_code}\n")
    
    # Test 3: Generate Mnemonic
    print("3. Testing Mnemonic Generation (Facts type)...")
    response = requests.post('http://localhost:5000/api/revision/mnemonic', json={
        'text': 'Supreme Court powers: Original Jurisdiction, Appellate Jurisdiction, Advisory Jurisdiction, Court of Record, Power of Judicial Review',
        'type': 'list'
    })
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"✅ Mnemonic Generated:")
            print(f"   Type: {data['type']}")
            print(f"   Mnemonic: {data['mnemonic']}\n")
        else:
            print("❌ Failed\n")
    else:
        print(f"❌ HTTP Error: {response.status_code}\n")

    print("4. Testing Mnemonic Generation (Dates type)...")
    response = requests.post('http://localhost:5000/api/revision/mnemonic', json={
        'text': '1857 - First War of Independence, 1885 - Formation of Indian National Congress, 1947 - Independence of India',
        'type': 'dates'
    })
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"✅ Mnemonic Generated:")
            print(f"   Mnemonic: {data['mnemonic']}\n")
        else:
            print("❌ Failed\n")
    else:
        print(f"❌ HTTP Error: {response.status_code}\n")

if __name__ == "__main__":
    test_revision_features()
