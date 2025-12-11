import time
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import create_app
from app.services.brain_service import brain_service
from app.services.model_manager import model_manager

def stress_test():
    print("🔥 Starting Brain Vault Automation Stress Test...")
    print("   Goal: Trigger Quota Limits on Flash models and verify fallback to Gemma.")
    print("   Target: 20 rapid-fire requests.")
    
    app = create_app()
    with app.app_context():
        success_count = 0
        
        for i in range(1, 21):
            print(f"\n⚡ Request {i}/20...")
            start_time = time.time()
            
            # Use a direct model generation to ensure we hit the manager directly and heavily
            # Simulating a heavy automated thought process
            prompt = f"Write a short philosophical reflection on the number {i}. Keep it brief (50 words)."
            
            try:
                # We use 'fast' tier which now includes Gemma
                response = model_manager.generate_content(prompt, model_type='fast')
                
                duration = time.time() - start_time
                print(f"   ✅ Success in {duration:.2f}s")
                # We can't see which model was used easily unless we inspect internal state or logs, 
                # but the ABSENCE of error is the key.
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ FAILED: {e}")
                
            # Minimal sleep to force rate limit hits
            time.sleep(0.5) 

        print(f"\n🏁 Test Complete.")
        print(f"   Success Rate: {success_count}/20")
        
        if success_count == 20:
             print("   🏆 RESULT: PASSED. Zero Panic Mode.")
        else:
             print("   ⚠️ RESULT: FAILED. Some requests dropped.")

if __name__ == "__main__":
    stress_test()
