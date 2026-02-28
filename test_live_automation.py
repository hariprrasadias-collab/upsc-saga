import sys
import os
import json

# Add backend directory to sys path so we can import app modules
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app import create_app
from app.services.brain_service import BrainService
from app.db import get_db

app = create_app()

with app.app_context():
    print("Testing Brain Service Automation Engines with LIVE KEY...")
    brain = BrainService()
    
    # Simulate completing a study task
    test_task = {
        "id": 9998,
        "topic": "Directive Principles of State Policy",
        "subject": "Polity",
        "user_id": 1,
        "plan_id": 1
    }
    
    conn = get_db()
    
    try:
        # Trigger automation (this will spawn threads under the hood via process_task_completion)
        brain.process_task_completion(test_task)
        print("Triggers fired successfully. Processing via Gemini API...")
        
        # Wait a few seconds for the threads to finish fetching from Gemini
        import time
        for i in range(5):
            print(f"Waiting... {25 - i*5} seconds left")
            time.sleep(5)

        print("\n--- LIVE GENERATED RESULTS ---")
        
        # Check Mnemonics
        mnemonics = conn.execute("SELECT mnemonic_text FROM mnemonics_history WHERE original_text=? ORDER BY id DESC LIMIT 1", (test_task['topic'],)).fetchall()
        if mnemonics: 
            print(f"\n[ MNEMONIC / VISUAL PROMPT ]\n{mnemonics[0][0]}")

        # Check AI Content Table
        ai_content = conn.execute("SELECT content_type, content FROM ai_generated_content WHERE topic=? ORDER BY id ASC", (test_task['topic'],)).fetchall()
        for c in ai_content:
            text = c[1]
            if len(text) > 500:
                text = text[:500] + "\n... (truncated for preview)"
            print(f"\n[ {c[0].upper()} ]\n{text}")

    except Exception as e:
        print(f"Test Failed: {e}")
