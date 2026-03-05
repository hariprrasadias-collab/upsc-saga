import sys, os, json
sys.path.append(os.getcwd())
from app import create_app
from app.services.brain_service import brain_service

app = create_app()
with app.app_context():
    print("Executing CONSTRUCT_PALACE...")
    res = brain_service.execute_action("CONSTRUCT_PALACE", {"topic": "The Revolt of 1857"})
    print("CONSTRUCT_PALACE RESULT:", json.dumps(res, indent=2))

    print("\nExecuting GENERATE_MIND_MAP...")
    res2 = brain_service.execute_action("GENERATE_MIND_MAP", {"topic": "The Revolt of 1857"})
    if res2.get('mindmap'):
        print("MIND_MAP SUCCESS. Keys:", res2['mindmap'].keys())
    else:
        print("GENERATE_MIND_MAP RESULT:", json.dumps(res2, indent=2))
