import os
import sys
from flask import Flask
from dotenv import load_dotenv
import datetime

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.study_planner import get_todays_tasks_summary

# Load environment variables
load_dotenv()

app = Flask(__name__)

def check_tasks():
    with app.app_context():
        print(f"Checking tasks for: {datetime.date.today().isoformat()}")
        summary = get_todays_tasks_summary()
        print(f"Summary:\n{summary}")

if __name__ == "__main__":
    check_tasks()
