import requests
import json

BASE_URL = "http://localhost:5000/api/analytics/predictive"

def test_endpoints():
    endpoints = [
        "/exam-readiness",
        "/success-probability",
        "/optimal-study-time",
        "/burnout-detection",
        "/all"
    ]

    print("Testing Predictive Analytics Endpoints...")
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        try:
            response = requests.get(url)
            print(f"\nGET {endpoint}")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("Response:", json.dumps(response.json(), indent=2))
            else:
                print("Error:", response.text)
        except Exception as e:
            print(f"Failed to connect to {url}: {e}")

if __name__ == "__main__":
    test_endpoints()
