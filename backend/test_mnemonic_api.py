import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
print(f"API Key loaded: {'Yes' if GEMINI_API_KEY else 'No'}")
print(f"API Key (first 10 chars): {GEMINI_API_KEY[:10] if GEMINI_API_KEY else 'None'}...")

genai.configure(api_key=GEMINI_API_KEY)

# Test simple generation
try:
    model = genai.GenerativeModel('gemini-flash-latest')
    response = model.generate_content("Say hello in one word")
    print(f"\n✅ SUCCESS! Model response: {response.text}")
    print("\nMnemonic Generator should work now after Flask restart!")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nTrying to list available models...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"  - {m.name}")
    except Exception as e2:
        print(f"Could not list models: {e2}")
