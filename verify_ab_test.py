import requests
import json

url = "http://localhost:5000/api/autonomy/ab_tests"
data = {
    "test_name": "Flashcard_Timing_v2",
    "strategy_a": "Morning",
    "strategy_b": "Evening",
    "duration_days": 7
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print("Response:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
