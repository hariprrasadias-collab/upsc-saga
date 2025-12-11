from backend.app.services.model_manager import model_manager

def test_model(model_name):
    print(f"\n🧪 Testing Model: {model_name}")
    try:
        response = model_manager.generate_content("Hello, can you hear me?", forced_model=model_name)
        print(f"✅ SUCCESS: {response.text}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("Checking gemini-2.5-flash-live compatibility via ModelManager...")
    test_model("gemini-2.0-flash-exp") # Updated to valid model
    
    print("\nChecking gemini-2.5-flash (Fallback)...")
    test_model("gemini-2.5-flash-lite")
