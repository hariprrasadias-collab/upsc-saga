import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.services.model_manager import model_manager

def test_provider(provider_name, model_name):
    # Regression Check
    if not model_manager.is_configured:
        print("❌ CRITICAL: model_manager.is_configured is False!")
        return False
        
    print(f"\n--- Testing Provider: {provider_name} with Model: {model_name} ---")
    try:
        start_time = time.time()
        response = model_manager.generate_content(
            "Hello, current time is " + str(time.time()), 
            model_name=model_name,
            provider=provider_name
        )
        duration = time.time() - start_time
        print(f"✅ Success ({duration:.2f}s)")
        print(f"Response Preview: {response.text[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

import time

if __name__ == "__main__":
    
    print("🔍 Diagnostic Run: AI Provider Integration")
    
    # 1. Test Google (Baseline)
    test_provider('google', 'gemini-2.5-flash')
    
    # 2. Test OpenRouter
    test_provider('openrouter', 'openai/gpt-3.5-turbo') # Cheap/Fast test
    
    # 3. Test Nvidia
    test_provider('nvidia', 'meta/llama-3.1-70b-instruct')
    
    # 4. Test Efficiency Tiers
    print("\n--- Testing OpenRouter Efficiency Tiers ---")
    
    print("Testing Free Tier Rotation...")
    # Try a few free models to see if at least one works
    for model in model_manager.OPENROUTER_FREE[:3]:
        print(f"Trying {model}...")
        if test_provider('openrouter', model):
            break 
            
    # test_provider('openrouter', model_manager.OPENROUTER_ECONOMY[0]) # Test Economy
    test_provider('openrouter', model_manager.OPENROUTER_PREMIUM[0]) # Test Premium
