# Check available Gemini models
import google.generativeai as genai
import os

# os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')  # Use env variable
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

print("Listing available models...")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✓ {model.name}")
