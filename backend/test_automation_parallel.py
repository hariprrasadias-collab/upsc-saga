import sys
import os
import time
import threading

# Ensure backend directory is in path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app import create_app, db
from app.services.brain_service import brain_service

def verify_parallel_automation():
    print("🧪 Testing Parallel Automation Execution...")
    
    app = create_app()
    with app.app_context():
        # 1. Define Test Data
        fake_task = {
            "id": 99999,
            "topic": "Parallel Processing in Computing", # Unique topic to track
            "subject": "Science & Tech",
            "user_id": 1,
            "plan_id": 1
        }
        
        # 2. Trigger "Task Complete" (Simulating the Thread logic from study_plan.py)
        # Note: In the real app, study_plan.py spawns a thread. 
        # Here we call it directly to wait for it, but relying on BrainService's internal parallelism.
        
        print(f"🚀 Triggering Automation for: {fake_task['topic']}")
        start_time = time.time()
        
        brain_service.process_task_completion(fake_task)
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"⏱️ Total Execution Time: {duration:.2f}s")
        
        # 3. Validation
        print("\n🔍 Validating Artifact Creation...")
        conn = db.get_db()
        
        # Check Flashcards
        cards = conn.execute("SELECT count(*) FROM flashcards WHERE front LIKE ?", ('%Parallel Processing%',)).fetchone()[0]
        print(f"Flashcards Created: {cards} (Expected > 0)")
        
        # Check Mock Test
        tests = conn.execute("SELECT count(*) FROM mock_tests WHERE title LIKE ?", ('Test: Parallel Processing%',)).fetchone()[0]
        print(f"Mock Tests Created: {tests} (Expected > 0)")
        
        # Check Predictions
        preds = conn.execute("SELECT count(*) FROM foresight_predictions WHERE topic = ?", ('Parallel Processing in Computing',)).fetchone()[0]
        print(f"Predictions Created: {preds} (Expected > 0)")

        # Check Socratic
        debate = conn.execute("SELECT count(*) FROM socratic_conversations WHERE topic = ?", ('Parallel Processing in Computing',)).fetchone()[0]
        print(f"Socratic Debates Created: {debate} (Expected > 0)")

        # Check Linkages
        linkages = conn.execute("SELECT count(*) FROM neural_hashes WHERE topic = ?", ('Parallel Processing in Computing',)).fetchone()[0]
        print(f"Linkages Created: {linkages} (Expected > 0)")

        # Check Podcasts
        podcasts = conn.execute("SELECT count(*) FROM ai_generated_content WHERE topic = ? AND content_type='podcast'", ('Parallel Processing in Computing',)).fetchone()[0]
        print(f"Podcasts Created: {podcasts} (Expected > 0)")
        
        if cards > 0 and tests > 0 and preds > 0 and debate > 0 and linkages > 0 and podcasts > 0:
            print("\n✅ SUCCESS: All 6 automation artifacts generated!")
        else:
            print("\n❌ FAILURE: Missing artifacts.")

if __name__ == "__main__":
    verify_parallel_automation()
