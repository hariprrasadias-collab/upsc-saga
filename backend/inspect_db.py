import os
import sys
from flask import Flask
from dotenv import load_dotenv
import datetime

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db import get_db

# Load environment variables
load_dotenv()

app = Flask(__name__)

def inspect_db():
    with app.app_context():
        conn = get_db()
        
        print("\n--- Study Plans ---")
        plans = conn.execute('SELECT * FROM study_plans').fetchall()
        for p in plans:
            print(dict(p))
            
        print("\n--- Tasks for Today (All Plans) ---")
        today = datetime.date.today().isoformat()
        tasks = conn.execute('SELECT * FROM study_tasks WHERE date = ?', (today,)).fetchall()
        for t in tasks:
            print(dict(t))

if __name__ == "__main__":
    inspect_db()
