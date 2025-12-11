
from app.services.model_manager import model_manager

print(f"Checking API Key via ModelManager...")

if not model_manager.is_configured:
    print("❌ ERROR: ModelManager not configured")
    exit(1)

print(f"✅ ModelManager Configured")

try:
    print("Sending test prompt (fast tier)...")
    
    response = model_manager.generate_content("Hello, are you working?", model_type='fast')
    print(f"✅ Response received: {response.text}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
