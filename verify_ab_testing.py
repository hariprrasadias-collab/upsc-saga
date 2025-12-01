import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.optimization_engine import OptimizationEngine
from app.services.brain_service import BrainService
from app.services.ab_tester import ab_tester
from app.db import get_db
import json
import flask

# Mock AutonomyManager
from unittest.mock import MagicMock

def verify_ab_loop():
    print("🧪 Verifying A/B Testing Loop...")
    
    # 1. Setup
    oe = OptimizationEngine()
    bs = BrainService()
    bs.autonomy.log_action = MagicMock(return_value=1)
    bs.autonomy.update_action_outcome = MagicMock()
    
    conn = get_db()
    
    # Clear existing test to ensure fresh run
    conn.execute("DELETE FROM brain_ab_tests WHERE test_name = 'OptimalStudyTime'")
    conn.execute("DELETE FROM brain_optimization_opportunities WHERE type = 'schedule'")
    conn.commit()
    
    # 2. Generate Suggestion (Triggers Test Creation)
    print("Generating suggestions...")
    opportunities = oe._check_schedule_gaps()
    
    if not opportunities:
        print("❌ FAILURE: No opportunities generated.")
        return
        
    opp = opportunities[0]
    payload = opp['payload']
    if isinstance(payload, str):
        payload = json.loads(payload)
    print(f"Generated Opportunity: {opp['description']}")
    print(f"Payload: {payload}")
    
    if 'ab_test_id' not in payload:
        print("❌ FAILURE: ab_test_id missing in payload.")
        return
        
    test_name = payload['ab_test_id']
    
    # 3. Verify Test Creation
    test = conn.execute("SELECT * FROM brain_ab_tests WHERE test_name = ?", (test_name,)).fetchone()
    if not test:
        print("❌ FAILURE: A/B Test not found in DB.")
        return
    print(f"✅ A/B Test Created: {test['test_name']} (Active Strategy: {test['active_strategy']})")
    
    # 4. Execute Action (Triggers Result Logging)
    print("Executing action...")
    # We need to pass the payload exactly as it is in the opportunity
    # The payload in DB is a JSON string, but here we parsed it.
    # BrainService expects a dict payload.
    
    # Note: BrainService.execute_action expects 'action_type' and 'payload'.
    # The opportunity payload has 'action' key which is the type.
    action_type = payload.pop('action')
    
    result = bs.execute_action(action_type, payload)
    print(f"Action Result: {result}")
    
    # 5. Verify Result Logging
    test_after = conn.execute("SELECT * FROM brain_ab_tests WHERE test_name = ?", (test_name,)).fetchone()
    results = json.loads(test_after['results']) if test_after['results'] else {}
    
    strategy = test['active_strategy']
    if strategy in results and len(results[strategy]) > 0:
        print(f"✅ Result Logged for Strategy {strategy}: {results[strategy]}")
    else:
        print(f"❌ FAILURE: No results logged for Strategy {strategy}. Results: {results}")

if __name__ == "__main__":
    app = flask.Flask(__name__)
    app.config['DATABASE'] = 'd:/upsc-second-brain/backend/upsc_saga.db'
    
    with app.app_context():
        verify_ab_loop()
