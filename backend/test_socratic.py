import requests
import json

url = "http://localhost:5000/api/socratic/debate"

payload = {
    "topic": "Universal Basic Income",
    "history": [
        {
            "speakerId": "idealist",
            "text": "UBI is a moral imperative. Every citizen deserves a life of dignity regardless of their economic utility.",
            "type": "ARGUMENT"
        }
    ],
    "user_input": "But where will the money come from?"
}

try:
    print("Sending request to Socratic Debate API...")
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("\n✅ API Success!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"\n❌ API Failed: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"\n❌ Connection Error: {e}")
    print("Ensure the backend server is running on port 5000.")
