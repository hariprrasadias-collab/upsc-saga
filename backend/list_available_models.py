import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# Robust .env loading
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)
api_key = os.environ.get('GEMINI_API_KEY')

if not api_key:
    # Try finding it in current dir
    load_dotenv()
    api_key = os.environ.get('GEMINI_API_KEY')

print(f"DEBUG: API Key loaded: {'Yes' if api_key else 'No'}")
genai.configure(api_key=api_key)

def list_all_models():
    print("🔍 Querying Google API for Available Models...")
    try:
        count = 0
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"AVAILABLE: {m.name}")
                count += 1
            # else: skipped silent
        
        if count == 0:
            print("❌ No models found with 'generateContent' capability.")
            
    except Exception as e:
        print(f"❌ Error listing models: {e}")

if __name__ == "__main__":
    list_all_models()
