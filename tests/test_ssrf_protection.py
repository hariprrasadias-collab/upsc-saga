
import unittest
from unittest.mock import patch, MagicMock
from app.services.upsc_summarizer import fetch_article_content
import socket

class TestSSRFProtection(unittest.TestCase):

    @patch('requests.get')
    @patch('socket.gethostbyname')
    def test_ssrf_protection(self, mock_gethostbyname, mock_get):
        # --- Test Case 1: Internal IP (Vulnerability Check) ---
        # Mock DNS resolution to loopback
        mock_gethostbyname.return_value = '127.0.0.1'

        # Mock response (if fetched, which it shouldn't be)
        mock_response_vuln = MagicMock()
        mock_response_vuln.content = b"<html><body><p>Secret Admin Data</p></body></html>"
        mock_response_vuln.status_code = 200
        mock_response_vuln.is_redirect = False

        mock_get.return_value = mock_response_vuln

        # Attempt to fetch internal URL
        print("Testing Internal URL Block...")
        content_vuln = fetch_article_content("http://internal.local/admin")

        # Assertion: Content should be empty because it was blocked
        self.assertEqual(content_vuln, "", "Internal URL should be blocked (returned empty string)")

        # Verify requests.get was NOT called (because validation happens before)
        mock_get.assert_not_called()

        # --- Test Case 2: External IP (Safe Usage Check) ---
        # Reset mock
        mock_get.reset_mock()

        # Mock DNS resolution to public IP
        mock_gethostbyname.return_value = '8.8.8.8'

        # Mock response
        mock_response_safe = MagicMock()
        mock_response_safe.content = b"<html><body><p>Public News Article</p></body></html>"
        mock_response_safe.status_code = 200
        mock_response_safe.is_redirect = False

        mock_get.return_value = mock_response_safe

        # Attempt to fetch external URL
        print("Testing External URL Allow...")
        content_safe = fetch_article_content("http://google.com/news")

        # Assertion: Content should NOT be empty
        self.assertIn("Public News Article", content_safe, "External URL should be fetched")

        # Verify requests.get WAS called
        mock_get.assert_called()

if __name__ == '__main__':
    unittest.main()
