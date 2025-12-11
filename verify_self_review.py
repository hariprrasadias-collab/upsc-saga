import sys
import os
import json
import sqlite3
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import create_app
from app.db import get_db
from app.services.self_review import self_review_service

def verify_self_review():
    print("🧪 Verifying SelfReviewService...")
    app = create_app()
    with app.app_context():
        conn = get_db()
        
        # 1. Inject Dummy Data into brain_action_log
        print("   -> Injecting dummy action logs...")
        conn.execute("DELETE FROM brain_action_log WHERE executed_by = 'test_injector'")
        
        actions = [
            ('success', 0.8, 'test_injector'),
            ('success', 0.9, 'test_injector'),
            ('failure', -0.5, 'test_injector'),
            ('corrected', 0.5, 'test_injector'), # TEST CORRECTION
            ('success', 0.7, 'test_injector')
        ]
        
        for status, impact, user in actions:
            conn.execute('''
                INSERT INTO brain_action_log (action_type, outcome_status, impact_score, executed_by)
                VALUES (?, ?, ?, ?)
            ''', ('TEST_ACTION', status, impact, user))
        conn.commit()
        
        # 2. Trigger Review
        print("   -> Triggering perform_review(lookback_days=1)...")
        try:
            result = self_review_service.perform_review(lookback_days=1)
            
            print(f"   -> Review Result: {json.dumps(result, indent=2)}")
            
            if result['stats']['total'] >= 4:
                print("   ✅ Stats Calculation Correct")
            else:
                print(f"   ❌ Stats Calculation Failed (Count: {result['stats']['total']})")
                
            if 'plan' in result['improvement_plan']:
                print("   ✅ Improvement Plan Generated (JSON Parsed)")
            else:
                print("   ❌ Improvement Plan missing 'plan' key")
                
        except Exception as e:
            print(f"   ❌ Execution Failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    verify_self_review()
