import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    print("Checking upsc_summarizer...")
    from app.services import upsc_summarizer
    print("upsc_summarizer imported successfully.")
    
    print("Checking ravens route...")
    from app.routes import ravens
    print("ravens route imported successfully.")
    
except Exception as e:
    print(f"Syntax Error: {e}")
    import traceback
    traceback.print_exc()
