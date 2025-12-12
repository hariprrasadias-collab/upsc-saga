
import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.services.answer_evaluator import evaluator
from app.services.upsc_summarizer import summarize_for_upsc

class TestSecondaryServices(unittest.TestCase):
    
    @patch('app.services.answer_evaluator.model_manager')
    def test_evaluator_robust_parsing(self, mock_mm):
        # Mock various bad outputs
        bad_outputs = [
            "```json\n{\"overall_score\": 7.5}```",
            "Here is the JSON:\n```json\n{\"overall_score\": 7.5}\n```",
            "```\n{\"overall_score\": 7.5}\n```",
            "Sure! {\"overall_score\": 7.5}"
        ]
        
        for text in bad_outputs:
            mock_response = MagicMock()
            mock_response.text = text
            mock_mm.generate_content.return_value = mock_response
            mock_mm.is_configured = True
            
            result = evaluator.evaluate_answer("Q", "A", 100)
            self.assertEqual(result['overall_score'], 7.5, f"Failed to parse: {text}")

    @patch('app.services.upsc_summarizer.model_manager')
    def test_summarizer_robust_parsing(self, mock_mm):
        # Mock various bad outputs
        bad_outputs = [
            "```json\n{\"papers\": [\"GS1\"], \"subjects\": [\"History\"]}\n```",
            "Analysis:\n```json\n{\"papers\": [\"GS1\"], \"subjects\": [\"History\"]}\n```",
             "{\"papers\": [\"GS1\"], \"subjects\": [\"History\"]}  <-- Hope this helps!"
        ]
        
        for text in bad_outputs:
            mock_response = MagicMock()
            mock_response.text = text
            mock_mm.generate_content.return_value = mock_response
            
            # Mock find_related_pyqs to avoid DB calls
            with patch('app.services.upsc_summarizer.find_related_pyqs', return_value=[]):
                # Also patch extract_image_from_article
                with patch('app.services.upsc_summarizer.extract_image_from_article', return_value=None):
                    result = summarize_for_upsc("Title", "Content", "Link")
                
            self.assertEqual(result['papers'], ["GS1"], f"Failed to parse: {text}")

if __name__ == '__main__':
    unittest.main()
