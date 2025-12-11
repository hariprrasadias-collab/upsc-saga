import sys
import os
import json
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import create_app
from app.services.model_manager import model_manager

def verify_quota_logic():
    print("🔒 Verifying RPD Quota Logic...")
    
    # 1. Setup Mock Quota File (Near Limit)
    quota_file = "backend/daily_quota.json"
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    start_data = {'date': today_str, 'count': 1449}
    with open(quota_file, 'w') as f:
        json.dump(start_data, f)
        
    print(f"   Note: Set quota to {start_data['count']} (Limit: 1450)")
    
    app = create_app()
    with app.app_context():
        # Request #1: Should Pass (1449 -> 1450)
        print("\n⚡ Request 1 (Should Pass)...")
        res1 = model_manager.generate_content("Test 1", model_type='fast')
        print(f"   Result: {res1.text[:20]}...")
        
        # Read file
        with open(quota_file, 'r') as f:
            d = json.load(f)
            print(f"   Current Count: {d['count']}")
            
        # Request #2: Should Block (1450 -> Blocked)
        print("\n⚡ Request 2 (Should Block)...")
        res2 = model_manager.generate_content("Test 2", model_type='fast')
        print(f"   Result: {res2.text}")
        
        if "Daily Quota Limit" in res2.text:
            print("   ✅ SUCCESS: Request Blocked Correctly.")
        else:
            print("   ❌ FAILED: Request Leaked through.")

    # Cleanup
    with open(quota_file, 'w') as f:
        json.dump({'date': today_str, 'count': 100}, f) # Reset to safe low number
    print("\n🧹 Cleanup: Reset quota to 100.")

if __name__ == "__main__":
    verify_quota_logic()
