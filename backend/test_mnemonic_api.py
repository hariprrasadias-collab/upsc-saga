from app.services.model_manager import model_manager
import os
from dotenv import load_dotenv

load_dotenv()

print("🧪 Testing Mnemonic API via ModelManager...")

try:
    # Use 'fast' model for simple test
    response = model_manager.generate_content("Say hello in one word", model_type='fast')
    print(f"\n✅ SUCCESS! Model response: {response.text}")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nCheck ModelManager logs for details.")
