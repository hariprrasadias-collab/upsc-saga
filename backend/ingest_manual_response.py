import json
import os
import sys
from app.services.brain_service import brain_service
from app import create_app

def process_manual_response():
    """
    Script to manually trigger the ingestion of the AI response from paste_response_here.json.
    """
    app = create_app()
    with app.app_context():
        # 1. Check for Pending Task Context
        pending_path = os.path.join(os.getcwd(), 'backend', 'pending_manual_task.json')
        if not os.path.exists(pending_path):
            print("❌ No pending task found. Run a task completion first.")
            return

        with open(pending_path, 'r', encoding='utf-8') as f:
            task_data = json.load(f)

        # 2. Check for Manual Response
        response_path = os.path.join(os.getcwd(), 'backend', 'paste_response_here.json')
        if not os.path.exists(response_path):
            print("❌ No response file found at backend/paste_response_here.json")
            return

        try:
            with open(response_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
        except json.JSONDecodeError:
            print("❌ Invalid JSON in backend/paste_response_here.json")
            return

        print(f"🚀 Processing Manual Response for: {task_data.get('topic')}")

        # 3. Process
        success = brain_service.process_manual_completion_artifact(json_data, task_data)

        if success:
            print("✅ Ingestion Successful!")
            # Optional: Clean up pending file
            # os.remove(pending_path)
            # We keep it for safety/debugging unless explicitly deleted
        else:
            print("❌ Ingestion Failed. Check logs.")

if __name__ == "__main__":
    process_manual_response()
