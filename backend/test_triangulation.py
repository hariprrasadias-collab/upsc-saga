import requests
import json

def test_triangulation():
    print("Testing Triangulation API...")
    url = "http://localhost:5000/api/triangulation/analyze"
    
    payload = {
        "text": "The Governor of Tamil Nadu has reserved the bill for the President's consideration. This raises questions about federalism and the discretionary powers of the Governor under the Constitution."
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ API Success!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ API Failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_triangulation()
