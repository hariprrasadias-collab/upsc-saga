import requests
import json
import os
import sys

# Add backend to path to import BrainService directly for simulation
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def test_persistence():
    print("🚀 Starting Persistence Verification...")
    
    # 1. Define a dummy strategy
    dummy_strategy = [
        {"id": "test_node_1", "label": "Test Node 1", "yield": 10, "effort": 5},
        {"id": "test_node_2", "label": "Test Node 2", "yield": 20, "effort": 10}
    ]
    
    # 2. Send to API
    try:
        print("Sending strategy to API...")
        res = requests.post('http://localhost:5000/api/brain/directive', json={"path": dummy_strategy})
        if res.status_code == 200:
            print("✅ API accepted strategy.")
        else:
            print(f"❌ API failed: {res.text}")
            return
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return

    # 3. Check file existence
    file_path = os.path.join(os.getcwd(), 'backend', 'instance', 'current_strategy.json')
    # Note: The app runs in 'backend' dir usually, so instance might be in backend/instance
    # Let's check both likely locations relative to where this script runs (root)
    
    possible_paths = [
        os.path.join(os.getcwd(), 'backend', 'instance', 'current_strategy.json'),
        os.path.join(os.getcwd(), 'instance', 'current_strategy.json')
    ]
    
    found_path = None
    for p in possible_paths:
        if os.path.exists(p):
            found_path = p
            break
            
    if found_path:
        print(f"✅ Persistence file found at: {found_path}")
        with open(found_path, 'r') as f:
            data = json.load(f)
            if len(data) == 2 and data[0]['id'] == 'test_node_1':
                print("✅ File content matches sent strategy.")
            else:
                print(f"❌ File content mismatch: {data}")
    else:
        print(f"❌ Persistence file NOT found. Checked: {possible_paths}")

if __name__ == "__main__":
    test_persistence()
