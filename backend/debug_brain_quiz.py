import os
import sys
from flask import Flask
from dotenv import load_dotenv

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.brain_service import BrainService

# Load environment variables
load_dotenv()

app = Flask(__name__)

def debug_quiz_generation():
    print("--- Starting Debug Session ---")
    
    # Check API Key
    api_key = os.environ.get('GEMINI_API_KEY')
    print(f"API Key present: {bool(api_key)}")
    
    with app.app_context():
        brain = BrainService()
        user_input = "Generate a quiz on Ancient History"
        
        print(f"\nUser Input: {user_input}")
        print("Thinking...")
        
        try:
            # 1. Test Think
            response = brain.think(user_input)
            print("\n--- Brain Response ---")
            print(f"Thought Process: {response.get('thought_process')}")
            print(f"Response Text: {response.get('response_text')}")
            print(f"Suggested Actions: {response.get('suggested_actions')}")
            
            # 2. Test Execution if action exists
            if response.get('suggested_actions'):
                action = response['suggested_actions'][0]
                print(f"\n--- Executing Action: {action['type']} ---")
                result = brain.execute_action(action['type'], action['payload'])
                print(f"Execution Result: {result}")
            else:
                print("\n[ERROR] No action suggested by Brain.")
                
            # 3. Test Task Context
            from app.services.study_planner import get_todays_tasks_summary
            print("\n--- Checking Today's Tasks ---")
            tasks_summary = get_todays_tasks_summary()
            print(f"Tasks Summary: {tasks_summary}")

        except Exception as e:
            print(f"\n[EXCEPTION] {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_quiz_generation()
