import requests
import json
import sqlite3
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:5000/api/syllabus'


def test_revision_flow():
    print("Testing Revision Flow...")

    # Reset revisions table to ensure clean state
    conn = sqlite3.connect('backend/upsc_saga.db')
    conn.execute('DELETE FROM topic_revisions')
    conn.commit()
    conn.close()

    try:
        # 1. Get all topics
        res = requests.get(f"{BASE_URL}/")
        print(f"Status: {res.status_code}")
        try:
            topics = res.json()
        except Exception:
            print(f"Failed to decode JSON. Body: {res.text}")
            return
        if not topics:
            print("No topics found. Skipping test.")
            return

        topic_id = topics[0]['id']
        print(f"Testing with Topic ID: {topic_id}")

        # 2. Mark as revised
        print(f"Marking topic {topic_id} as revised...")
        res = requests.post(f"{BASE_URL}/{topic_id}/revise")
        if res.status_code != 200:
            print(f"Failed to mark revised: {res.text}")
            return
        data = res.json()
        print(f"Revision Response: {json.dumps(data, indent=2)}")

        # Verify next date based on revision count
        rev_count = data['revision_count']
        next_date = datetime.fromisoformat(data['next_revision_date']).date()
        today = datetime.now().date()
        if rev_count == 1:
            expected_date = today + timedelta(days=1)
        elif rev_count == 2:
            expected_date = today + timedelta(days=3)
        elif rev_count == 3:
            expected_date = today + timedelta(days=7)
        elif rev_count == 4:
            expected_date = today + timedelta(days=21)
        else:
            expected_date = today + timedelta(days=30)
        if next_date == expected_date:
            print(f"✅ Next revision date is correct (+{rev_count} revision(s))")
        else:
            print(f"❌ Next revision date incorrect. Got {next_date}, expected {expected_date}")

        # 3. Check Due List
        print("Checking Due List...")
        res = requests.get(f"{BASE_URL}/due")
        due_topics = res.json()
        print(f"Found {len(due_topics)} due topics.")

    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    test_revision_flow()
