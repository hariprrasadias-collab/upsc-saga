import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import create_app
from app.services.brain_service import BrainService

def verify_new_actions():
    app = create_app()
    with app.app_context():
        bs = BrainService()
        print("🧠 Brain Service Initialized.")
        
        actions = [
            ("EXPLAIN_SYLLABUS_NODE", {"topic": "Preamble"}),
            ("FIND_COMMON_PITFALLS", {"topic": "Monetary Policy"}),
            ("TRIANGULATE_TOPIC", {"topic": "Fundamental Rights"})
        ]
        
        for action, payload in actions:
            print(f"\n--- Testing {action} ---")
            try:
                result = bs.execute_action(action, payload)
                # Parse if result is string (should not be, but safe check)
                print(f"Result keys: {result.keys() if isinstance(result, dict) else result}")
                
                if result.get("success"):
                    print("✅ SUCCESS")
                else:
                    print(f"⚠️ FAILED: {result.get('message')}")
                    # Accept 'Quota Exceeded' as partial success (logic passed)
                    if "Quota" in str(result.get('message')):
                         print("✅ (Logic verified, Quota Hit)")
                         
                if result.get("message") == "Unknown action":
                    print("❌ CRITICAL FAILURE: Action not registered!")
                    # We continue to test others
                    
            except Exception as e:
                print(f"❌ EXCEPTION: {e}")

if __name__ == "__main__":
    verify_new_actions()
