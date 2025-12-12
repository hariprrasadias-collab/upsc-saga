import sys
import os

# Ensure backend directory is in path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app import create_app
from app.services.panopticon_service import panopticon
from app.services.model_manager import model_manager

def verify_fixes():
    print("🔍 Verifying Fixes...")
    
    app = create_app()
    with app.app_context():
        # 1. Test Panopticon DB Connection
        print("\n--- Testing PanopticonService.get_db_connection ---")
        try:
            conn = panopticon.get_db_connection()
            if conn:
                print("✅ Panopticon DB Connection Successful")
                conn.close()
            else:
                print("❌ Panopticon DB Connection returned None")
        except AttributeError:
             print("❌ AttributeError: get_db_connection not found!")
        except Exception as e:
            print(f"❌ Panopticon Error: {e}")

        # 2. Test ModelManager PRO Model (was failing with 404)
        print("\n--- Testing ModelManager PRO Model (Gemini) ---")
        try:
            # This forces usage of GEMINI_PRO_MODELS[0] which should now be valid
            response = model_manager.generate_content("Hello", model_type='pro', provider='google')
            if "Error" not in response.text:
                print("✅ PRO Model Generation Successful")
                print(f"Response: {response.text[:50]}...")
            else:
                print(f"❌ PRO Model Generation Failed: {response.text}")
        except Exception as e:
            print(f"❌ ModelManager Error: {e}")

if __name__ == "__main__":
    verify_fixes()
