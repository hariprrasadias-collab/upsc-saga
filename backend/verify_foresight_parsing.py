import sys
from unittest.mock import MagicMock
import os
import json

# Ensure backend directory is in path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.services.foresight_engine import foresight_engine
from app.services.model_manager import model_manager, FallbackResponse

def test_json_parsing():
    print("🧪 Testing ForesightEngine JSON Parsing (Markdown Handling)...")
    
    # Mock Response with Markdown code blocks (Typical Llama output)
    mock_json = [
        {
            "question": "Test Question?",
            "type": "MCQ",
            "probability": 0.9,
            "reasoning": "Test",
            "subject": "Test",
            "topic": "Test"
        }
    ]
    
    # Simulate chatty response
    chatty_response_text = f"""
    Here is the JSON you requested:
    ```json
    {json.dumps(mock_json)}
    ```
    Hope this helps!
    """
    
    # Mock model_manager
    original_generate = model_manager.generate_content
    model_manager.generate_content = MagicMock(return_value=FallbackResponse(chatty_response_text))
    
    # Mock internal methods to skip DB/Analysis calls
    original_analyze = foresight_engine._analyze_pyq_patterns
    original_affairs = foresight_engine._get_recent_affairs
    original_save = foresight_engine._critic_review # Skip critic for this test
    
    foresight_engine._analyze_pyq_patterns = MagicMock(return_value="Pattern")
    foresight_engine._get_recent_affairs = MagicMock(return_value="News")
    foresight_engine._critic_review = MagicMock(return_value=mock_json) # Pass through
    
    try:
        # Run prediction
        print("\n1. Simulating Llama-style Markdown Output...")
        predictions = foresight_engine.predict_questions("Polity")
        
        if len(predictions) == 1 and predictions[0]['question'] == "Test Question?":
            print("✅ Parsing Successful! (Markdown stripped correctly)")
        else:
            print(f"❌ Parsing Failed. Result: {predictions}")

    except Exception as e:
        print(f"❌ Test Failed with Exception: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Restore methods
        model_manager.generate_content = original_generate
        foresight_engine._analyze_pyq_patterns = original_analyze
        foresight_engine._get_recent_affairs = original_affairs
        foresight_engine._critic_review = original_save

if __name__ == "__main__":
    test_json_parsing()
