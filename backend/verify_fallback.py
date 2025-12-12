import sys
from unittest.mock import MagicMock
import os

# Ensure backend directory is in path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.services.model_manager import model_manager

def test_fallback():
    print("🧪 Testing Fail-Proof Fallback Logic...")
    
    # Simulate Google Failure by mocking the _generate_google method to raise Exception
    original_generate_google = model_manager._generate_google
    model_manager._generate_google = MagicMock(side_effect=Exception("Simulated Google 500 Error"))

    try:
        print("\n1. Requesting Google PRO model (Should fail and fallback)...")
        # This asks for 'google' implicitly via 'pro' type logic usually, 
        # but we can check the logs to see it trying Google then switching.
        response = model_manager.generate_content("Say 'Fallback Works'", model_type='pro')
        
        print(f"Response: {response.text}")
        
        if "Fallback Works" in response.text:
            print("✅ Fallback Successful! (Content generated despite Google failure)")
        else:
            print(f"⚠️ Response received but content unexpected: {response.text}")

    except Exception as e:
        print(f"❌ Fallback Failed: {e}")
    finally:
        # Restore method
        model_manager._generate_google = original_generate_google

if __name__ == "__main__":
    test_fallback()
