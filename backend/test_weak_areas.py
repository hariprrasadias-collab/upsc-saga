import requests
import json

def test_weak_areas():
    url = 'http://localhost:5000/api/weak-areas/practice'
    headers = {'Content-Type': 'application/json'}
    data = {'count': 10}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_weak_areas()
