import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import unittest
from unittest.mock import patch, MagicMock
from app.services.upsc_summarizer import summarize_for_upsc

class TestUPSCSummarizer(unittest.TestCase):

    def setUp(self):
        self.title = "Test Article"
        self.content = "This is a test article content for the UPSC summarizer."
        self.link = "http://example.com/test-article"

    @patch('app.services.upsc_summarizer.get_gemini_text')
    @patch('app.services.upsc_summarizer.model_manager.generate_content')
    def test_successful_summary(self, mock_generate_content, mock_get_gemini_text):
        # Setup mocks
        mock_generate_content.return_value = MagicMock()
        mock_get_gemini_text.return_value = '{"upsc_summary": "Test summary", "papers": ["GS1"], "subjects": ["History & Culture"]}'

        # Execute
        result = summarize_for_upsc(self.title, self.content, self.link)

        # Assertions
        self.assertEqual(result.get('upsc_summary'), "Test summary")
        self.assertEqual(result.get('papers'), ["GS1"])
        self.assertEqual(result.get('subjects'), ["History & Culture"])

    @patch('app.services.upsc_summarizer.get_gemini_text')
    @patch('app.services.upsc_summarizer.model_manager.generate_content')
    def test_empty_response_fallback(self, mock_generate_content, mock_get_gemini_text):
        # Setup mocks
        mock_generate_content.return_value = MagicMock()
        mock_get_gemini_text.return_value = "" # Empty response triggers fallback

        # Execute
        result = summarize_for_upsc(self.title, self.content, self.link)

        # Assertions
        self.assertEqual(result.get('upsc_summary'), self.content)

    @patch('app.services.upsc_summarizer.get_gemini_text')
    @patch('app.services.upsc_summarizer.model_manager.generate_content')
    def test_invalid_json_fallback(self, mock_generate_content, mock_get_gemini_text):
        # Setup mocks
        mock_generate_content.return_value = MagicMock()
        mock_get_gemini_text.return_value = "This is not a JSON response." # Invalid JSON triggers fallback

        # Execute
        result = summarize_for_upsc(self.title, self.content, self.link)

        # Assertions
        self.assertEqual(result.get('upsc_summary'), self.content)

    @patch('app.services.upsc_summarizer._infer_tags')
    @patch('app.services.upsc_summarizer.get_gemini_text')
    @patch('app.services.upsc_summarizer.model_manager.generate_content')
    def test_generic_tags_fallback(self, mock_generate_content, mock_get_gemini_text, mock_infer_tags):
        # Setup mocks
        mock_generate_content.return_value = MagicMock()
        # Return generic tags which triggers _infer_tags fallback
        mock_get_gemini_text.return_value = '{"upsc_summary": "Test summary", "papers": ["GS2"], "subjects": ["Current Affairs"]}'
        mock_infer_tags.return_value = (['GS3'], ['Economics'])

        # Execute
        result = summarize_for_upsc(self.title, self.content, self.link)

        # Assertions
        self.assertEqual(result.get('papers'), ['GS3'])
        self.assertEqual(result.get('subjects'), ['Economics'])

    @patch('app.services.upsc_summarizer.model_manager.generate_content')
    def test_exception_handling(self, mock_generate_content):
        # Setup mocks to raise Exception
        mock_generate_content.side_effect = Exception("API error")

        # Execute
        result = summarize_for_upsc(self.title, self.content, self.link)

        # Assertions
        self.assertEqual(result.get('upsc_summary'), self.content)

if __name__ == '__main__':
    unittest.main()
