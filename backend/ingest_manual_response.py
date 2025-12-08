from app import create_app
from app.services.brain_service import brain_service
from app.db import get_db
import json
import os
import traceback

def ingest_manual_response():
    app = create_app()
    with app.app_context():
        print("🧠 Ingesting Manual Response...")

        # 1. Read Task Context
        try:
            with open('backend/pending_manual_task.json', 'r') as f:
                task_data = json.load(f)
        except FileNotFoundError:
            print("❌ Error: 'backend/pending_manual_task.json' not found. Cannot associate response with a task.")
            return

        # 2. Read Manual Response
        try:
            with open('backend/paste_response_here.json', 'r') as f:
                response_data = json.load(f)
        except FileNotFoundError:
            print("❌ Error: 'backend/paste_response_here.json' not found.")
            return
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in 'backend/paste_response_here.json': {e}")
            return

        # 3. Apply Completion
        try:
            brain_service.apply_manual_completion(task_data, response_data)
            print("✅ Manual Completion Processed Successfully!")

            # Optional: Clear the pending task file to prevent double ingestion?
            # os.remove('backend/pending_manual_task.json')

        except Exception as e:
            print(f"❌ Error during processing: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    ingest_manual_response()
