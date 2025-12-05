import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from flask import Flask
from app.services.golden_path_service import golden_path

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def test_golden_path():
    with app.app_context():
        print("Building Golden Path Graph...")
        try:
            data = golden_path.get_graph_data()
            print("Graph Built Successfully!")
            print(f"Nodes: {len(data['nodes'])}")
            print(f"Edges: {len(data['edges'])}")
            
            if len(data['nodes']) > 0:
                print("Sample Node:", json.dumps(data['nodes'][0], indent=2))
        except Exception as e:
            print(f"Error building graph: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_golden_path()
