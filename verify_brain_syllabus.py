import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.brain_service import BrainService
from app.db import get_db

# Mock AutonomyManager to avoid complex setup
from unittest.mock import MagicMock

def verify_integration():
    print("Verifying Brain -> Syllabus Integration...")
    
    # 1. Setup
    bs = BrainService()
    # Mock autonomy to return a dummy action_id
    bs.autonomy.log_action = MagicMock(return_value=1)
    bs.autonomy.update_action_outcome = MagicMock()
    
    # 2. Reset Topic
    conn = get_db()
    topic = "World wars"
    conn.execute("UPDATE syllabus_topics SET status = 'Not Started' WHERE topic = ?", (topic,))
    conn.commit()
    
    # 3. Execute Action
    print(f"Executing COMPLETE_MOCK_TEST for '{topic}'...")
    payload = {'subject': 'History', 'topics': [topic]}
    result = bs.execute_action('COMPLETE_MOCK_TEST', payload)
    
    # 4. Verify Result
    print(f"Action Result: {result}")
    
    # 5. Verify DB Update
    row = conn.execute("SELECT status FROM syllabus_topics WHERE topic = ?", (topic,)).fetchone()
    if row and row['status'] == 'Completed':
        print("✅ SUCCESS: BrainService correctly updated Syllabus.")
    else:
        print(f"❌ FAILURE: Topic status is {row['status'] if row else 'None'}")

if __name__ == "__main__":
    # Need app context for DB
    import flask
    app = flask.Flask(__name__)
    app.config['DATABASE'] = os.path.join(os.getcwd(), 'backend', 'upsc_saga.db')
    
    with app.app_context():
        verify_integration()
