import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from app import create_app
from app.services.brain_service import BrainService
import time

app = create_app()
with app.app_context():
    brain = BrainService()
    print("Testing BrainService.process_task_completion...")
    task_data = {
        "id": 66299,
        "topic": "NCERT Cl 6: Our Pasts I - Ch 1",
        "subject": "History"
    }
    brain.process_task_completion(task_data)
    
    # Wait for parallel threads to finish
    print("Waiting 15 seconds for threads...")
    time.sleep(15)
    print("Done waiting.")
