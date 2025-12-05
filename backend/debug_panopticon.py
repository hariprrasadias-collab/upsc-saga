import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from flask import Flask
from app.services.brain_service import BrainService

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def test_panopticon():
    with app.app_context():
        print("Initializing BrainService...")
        brain = BrainService()
        print("Checking Bio Status...")
        status = brain.check_bio_status()
        print(f"Status: {status}")

if __name__ == "__main__":
    test_panopticon()
