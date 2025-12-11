import os
import google.generativeai as genai
from dotenv import load_dotenv

# Fix path to .env
from pathlib import Path
env_path = Path(__file__).parent / 'backend' / '.env'
load_dotenv(dotenv_path=env_path)

api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    # Try finding it in current dir
    load_dotenv()
    api_key = os.environ.get('GEMINI_API_KEY')

print(f"DEBUG: API Key loaded: {'Yes' if api_key else 'No'}")
genai.configure(api_key=api_key)

MODEL_LIST = [
    "gemma-3-12b-it"
]

def test_unlimited_models():
    print("🚀 Testing 'Unlimited' Models for Text Generation...", flush=True)
    
    for model_name in MODEL_LIST:
        print(f"\n🧪 Attempting: {model_name}", flush=True)
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello, this is a test.", request_options={"timeout": 10})
            
            # Print Raw parts to debug
            print(f"   -> Raw Candidates: {len(response.candidates)}", flush=True)
            if response.text:
                print(f"✅ SUCCESS: {model_name} responded.", flush=True)
        except Exception as e:
            print(f"❌ FAILED: {model_name} -> {e}", flush=True)

if __name__ == "__main__":
    test_unlimited_models()
