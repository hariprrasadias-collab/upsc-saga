
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Force reload of .env
load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY")

print(f"Checking API Key...")
if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not found in environment variables")
    exit(1)

print(f"✅ API Key found (length: {len(api_key)})")

try:
    genai.configure(api_key=api_key)
    print("Configuring Gemini with gemini-2.0-flash...")
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    print("Sending test prompt...")
    
    response = model.generate_content("Hello, are you working?")
    print(f"✅ Response received: {response.text}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
