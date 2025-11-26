import requests
import json

def seed_revision():
    url = 'http://localhost:5000/api/scheduler/schedule'
    data = {
        'item_type': 'note',
        'item_id': 999,
        'rating': 3
    }
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    seed_revision()
