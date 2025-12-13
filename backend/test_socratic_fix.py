
import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

# We need to import the function. It's in app/services/socratic_service.py
# But we might need to mock model_manager before importing if it does init stuff?
# Looking at the file, it imports model_manager but doesn't use it at module level.

from app.services.socratic_service import generate_debate_verdict

class TestSocraticParsing(unittest.TestCase):

    @patch('app.services.socratic_service.model_manager')
    def test_verdict_parsing_messy_json(self, mock_mm):
        """Test that generate_debate_verdict handles conversational wrappers"""
        
        # Simulate a "Chatty" LLM response
        messy_response = """
        Here is the verdict you asked for:
        
        ```json
        {
            "winner": "Socrates",
            "key_concepts": ["Elenchus", "Justice"],
            "synthesis": "Socrates dismantled the argument.",
            "best_quote": "Know thyself.",
            "mental_models": ["Dialectic"]
        }
        ```
        
        Hope this helps!
        """
        
        mock_mm.generate_content.return_value.text = messy_response
        
        # Dummy history
        history = [{"speakerId": "skeptic", "text": "Why?"}]
        
        result = generate_debate_verdict("Justice", history)
        
        self.assertEqual(result['winner'], "Socrates")
        self.assertEqual(result['key_concepts'], ["Elenchus", "Justice"])
        print("✅ Parsed Messy JSON Successfully")

    @patch('app.services.socratic_service.model_manager')
    def test_verdict_parsing_no_markdown(self, mock_mm):
        """Test parsing when no code blocks are used but text surrounds JSON"""
        
        messy_response = """
        Sure, here is the JSON:
        {
            "winner": "Plato",
            "key_concepts": ["Forms"],
            "synthesis": "Idealism wins.",
            "best_quote": "The Good.",
            "mental_models": []
        }
        """
        
        mock_mm.generate_content.return_value.text = messy_response
        
        history = [{"speakerId": "idealist", "text": "The Good!"}]
        
        result = generate_debate_verdict("Virtue", history)
        
        self.assertEqual(result['winner'], "Plato")
        print("✅ Parsed Bare JSON Successfully")

if __name__ == '__main__':
    unittest.main()
