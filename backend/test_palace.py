import sys, os
sys.path.append(os.getcwd())
from app import create_app
from app.services.brain_service import brain_service

app = create_app()
with app.app_context():
    print("Executing CONSTRUCT_PALACE...")
    res = brain_service.execute_action("CONSTRUCT_PALACE", {"topic": "The Revolt of 1857"})
    print(res)
