
try:
    from app.services.upsc_summarizer import summarize_for_upsc
    print("SUCCESS: app.services.upsc_summarizer imported successfully")
except ImportError as e:
    print(f"FAILURE: {e}")
except Exception as e:
    print(f"FAILURE: {e}")
