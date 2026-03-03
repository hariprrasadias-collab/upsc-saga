import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add backend directory to sys.path to allow importing app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from app.services.upsc_summarizer import retry_with_backoff
from google.api_core import exceptions as google_exceptions

class TestRetryWithBackoff:

    def test_success_first_try(self):
        """Test that a function succeeding on the first try is not retried and returns correctly."""
        mock_func = MagicMock(return_value="Success")

        result = retry_with_backoff(mock_func, "arg1", kwarg1="val1")

        assert result == "Success"
        mock_func.assert_called_once_with("arg1", kwarg1="val1")

    @patch("app.services.upsc_summarizer.time.sleep")
    def test_success_after_retries(self, mock_sleep):
        """Test that if the function raises ResourceExhausted, it is retried with backoff."""
        # Function raises ResourceExhausted on first 2 calls, succeeds on 3rd
        mock_func = MagicMock(side_effect=[
            google_exceptions.ResourceExhausted("Rate limit 1"),
            google_exceptions.ResourceExhausted("Rate limit 2"),
            "Success"
        ])

        result = retry_with_backoff(mock_func)

        assert result == "Success"
        assert mock_func.call_count == 3

        # Verify backoff values: base_delay = 10
        # Attempt 0: 10 * 2^0 = 10 seconds
        # Attempt 1: 10 * 2^1 = 20 seconds
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(10)
        mock_sleep.assert_any_call(20)

    @patch("app.services.upsc_summarizer.time.sleep")
    def test_failure_after_max_retries(self, mock_sleep):
        """Test that if it continues to fail, the exception is eventually re-raised."""
        # Function raises ResourceExhausted every time
        mock_func = MagicMock(side_effect=google_exceptions.ResourceExhausted("Persistent rate limit"))

        with pytest.raises(google_exceptions.ResourceExhausted) as exc_info:
            retry_with_backoff(mock_func)

        assert "Persistent rate limit" in str(exc_info.value)
        assert mock_func.call_count == 3

        # Verify backoff values: 10, 20
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(10)
        mock_sleep.assert_any_call(20)

    @patch("app.services.upsc_summarizer.time.sleep")
    def test_immediate_failure_on_other_exception(self, mock_sleep):
        """Test that exceptions other than ResourceExhausted are not retried."""
        mock_func = MagicMock(side_effect=ValueError("Some other error"))

        with pytest.raises(ValueError) as exc_info:
            retry_with_backoff(mock_func)

        assert "Some other error" in str(exc_info.value)
        assert mock_func.call_count == 1
        mock_sleep.assert_not_called()
