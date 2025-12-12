import requests
import json
import os

def fetch_openrouter_info():
    print("Fetching OpenRouter Model Data...")
    try:
        response = requests.get("https://openrouter.ai/api/v1/models")
        if response.status_code != 200:
            print(f"Failed to fetch: {response.status_code}")
            return

        data = response.json()['data']
        
        # Categories
        free_models = []
        cheap_models = [] # < $1 per M tokens input
        smart_models = [] # Known high performers (GPT-4, Claude 3, Llama 3 70B+)
        
        print(f"Total Models Available: {len(data)}")
        
        for model in data:
            mid = model['id']
            pricing = model.get('pricing', {})
            prompt_price = float(pricing.get('prompt', 0)) * 1000000 # Cost per 1M
            
            # Heuristic Categorization
            if prompt_price == 0:
                free_models.append(mid)
            elif prompt_price < 1.0:
                cheap_models.append(f"{mid} (${prompt_price:.2f}/M)")
                
            # Check for "Smart" keywords
            if any(x in mid.lower() for x in ['gpt-4', 'claude-3', 'llama-3.1-70b', 'llama-3.1-405b']):
                smart_models.append(f"{mid} (${prompt_price:.2f}/M)")

        output = {
            "free": sorted(free_models),
            "cheap_under_1_dollar": sorted(cheap_models),
            "smart_high_end": sorted(smart_models)
        }
        
        print("\n--- FREE MODELS (Efficiency Kings) ---")
        print(json.dumps(output['free'], indent=2))
        
        print("\n--- SMART MODELS (For Complex Tasks) ---")
        print(json.dumps(output['smart_high_end'][:10], indent=2))

        with open('openrouter_analysis.json', 'w') as f:
            json.dump(output, f, indent=2)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_openrouter_info()
