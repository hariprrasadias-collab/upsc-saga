import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.environ.get("CHUTES_API_KEY")
url = "https://llm.chutes.ai/v1/models"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Accept": "application/json"
}

print(f"Fetching models from: {url}")
try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        models = response.json()
        print("✅ Success! Available Models:")
        data = models.get('data', [])
        for m in data:
            print(f"- {m['id']}")
            
        # Save to file for inspection
        with open('chutes_models.json', 'w') as f:
            json.dump(models, f, indent=2)
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Error: {e}")
