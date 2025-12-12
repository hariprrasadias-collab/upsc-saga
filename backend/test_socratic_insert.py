import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app import create_app, db

def test_socratic_insert():
    print("🧪 Testing Socratic Insert Logic...")
    app = create_app()
    with app.app_context():
        try:
            conn = db.get_db()
            
            # Test Data
            topic = "Test Topic"
            user_id = 1
            dialogue = json.dumps([{"speaker": "Socrates", "text": "Why?"}])
            verdict = {"winner": "Socrates"}
            
            # The corrected insert statement
            print("🚀 Attempting INSERT...")
            conn.execute('INSERT INTO socratic_conversations (topic, user_id, dialogue, insight) VALUES (?, ?, ?, ?)',
                        (topic, user_id, dialogue, json.dumps(verdict)))
            conn.commit()
            
            print("✅ INSERT Successful!")
            
            # Verify retrieval
            row = conn.execute("SELECT * FROM socratic_conversations WHERE topic = ?", (topic,)).fetchone()
            if row:
                print(f"✅ Retrieved Row ID: {row['id']}")
                print(f"   Dialogue: {row['dialogue']}")
                print(f"   Insight: {row['insight']}")
            else:
                print("❌ Retrieval Failed")
                
        except Exception as e:
            print(f"❌ INSERT Failed: {e}")

if __name__ == "__main__":
    test_socratic_insert()
