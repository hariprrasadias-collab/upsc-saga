import requests
import datetime
import json

def test_api():
    today = datetime.date.today().isoformat()
    url = f"http://localhost:5000/api/planner/current?start_date={today}&days=1"
    
    print(f"Testing URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Response JSON keys:", data.keys())
            if 'plan' in data:
                print(f"Plan length: {len(data['plan'])}")
                if len(data['plan']) > 0:
                    print("First day slots:", len(data['plan'][0]['slots']))
            else:
                print("Response:", data)
        else:
            print("Error Response:", response.text)
            
    except Exception as e:
        print(f"Connection Error: {e}")
        print("Is the backend server running?")

if __name__ == "__main__":
    test_api()
