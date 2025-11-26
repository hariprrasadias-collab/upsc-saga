import requests
import json
import time

url = "http://localhost:5000/api/scribe/evaluate"
payload = {
    "question": "Analyze the major reasons for the limited effectiveness of Citizens' Charters and suggest concrete measures to make them meaningful. (250 words)",
    "answer": "Citizens' Charters were introduced to make public service delivery more transparent, accountable, and citizen-centric. However, their effectiveness has been limited due to top-down drafting, lack of consultation, and vague standards. To improve them, we need legal enforceability, decentralized drafting, and robust grievance redressal mechanisms."
}

print(f"Sending POST request to {url}...")
start_time = time.time()

try:
    response = requests.post(url, json=payload, timeout=60)
    elapsed = time.time() - start_time
    print(f"Response received in {elapsed:.2f} seconds")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text[:500]}...") # Print first 500 chars
except Exception as e:
    print(f"Request failed: {e}")
