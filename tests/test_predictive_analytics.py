import pytest
from unittest.mock import patch, MagicMock

# Assuming backend is part of PYTHONPATH in tests
import sys
import os

# Adjusting path so that app can be imported properly if it's not already
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.services.predictive_analytics import calculate_success_probability


def test_calculate_success_probability_less_than_3_mocks():
    with patch('app.services.predictive_analytics.get_db_connection') as mock_get_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Only 2 mock tests
        mock_cursor.fetchall.return_value = [
            {'score': 80, 'created_at': '2023-10-02'},
            {'score': 70, 'created_at': '2023-10-01'}
        ]

        result = calculate_success_probability()

        assert result == {
            'probability': 0,
            'confidence': 'low',
            'message': 'Take at least 3 mock tests for accurate prediction'
        }
        mock_cursor.execute.assert_called_once()
        mock_conn.close.assert_not_called() # Note: conn.close is not called if returning early

def test_calculate_success_probability_improving_trend():
    with patch('app.services.predictive_analytics.get_db_connection') as mock_get_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # 5 mock tests, improving trend chronologically.
        # Query uses ORDER BY submitted_at DESC, so the first element is the latest (highest score).
        # We will use scores: 50, 60, 70, 80, 90 (oldest to newest)
        # Avg score = 70.
        # Reversed list inside function: [50, 60, 70, 80, 90]
        # x_mean = 2
        # Numerator = (-2)*(-20) + (-1)*(-10) + 0*0 + 1*10 + 2*20 = 40 + 10 + 0 + 10 + 40 = 100
        # Denominator = 4 + 1 + 0 + 1 + 4 = 10
        # slope = 10
        # trend_adjustment = 10 * 5 = 50
        # base_prob = 70
        # probability = min(100, 70 + 50) = 100
        # score_variance = (400 + 100 + 0 + 100 + 400) / 5 = 200 (medium confidence)

        mock_cursor.fetchall.return_value = [
            {'score': 90, 'created_at': '2023-10-05'},
            {'score': 80, 'created_at': '2023-10-04'},
            {'score': 70, 'created_at': '2023-10-03'},
            {'score': 60, 'created_at': '2023-10-02'},
            {'score': 50, 'created_at': '2023-10-01'}
        ]

        result = calculate_success_probability()

        assert result == {
            'probability': 100.0,
            'confidence': 'medium',
            'trend': 'improving',
            'avg_mock_score': 70.0,
            'message': 'Based on 5 mock tests with medium confidence'
        }
        mock_cursor.execute.assert_called_once()
        mock_conn.close.assert_called_once()

def test_calculate_success_probability_declining_trend():
    with patch('app.services.predictive_analytics.get_db_connection') as mock_get_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # 5 mock tests, declining trend.
        # Reversed list inside function: [90, 80, 70, 60, 50]
        # x_mean = 2
        # y_mean = 70
        # Numerator = (-2)*(20) + (-1)*(10) + 0*0 + 1*(-10) + 2*(-20) = -40 - 10 + 0 - 10 - 40 = -100
        # Denominator = 10
        # slope = -10
        # trend_adjustment = -10 * 5 = -50
        # base_prob = 70
        # probability = max(0, 70 - 50) = 20
        # score_variance = 200 (medium confidence)

        mock_cursor.fetchall.return_value = [
            {'score': 50, 'created_at': '2023-10-05'},
            {'score': 60, 'created_at': '2023-10-04'},
            {'score': 70, 'created_at': '2023-10-03'},
            {'score': 80, 'created_at': '2023-10-02'},
            {'score': 90, 'created_at': '2023-10-01'}
        ]

        result = calculate_success_probability()

        assert result == {
            'probability': 20.0,
            'confidence': 'medium',
            'trend': 'declining',
            'avg_mock_score': 70.0,
            'message': 'Based on 5 mock tests with medium confidence'
        }
        mock_cursor.execute.assert_called_once()
        mock_conn.close.assert_called_once()

def test_calculate_success_probability_constant_trend():
    with patch('app.services.predictive_analytics.get_db_connection') as mock_get_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # 5 mock tests, constant scores.
        # Reversed list inside function: [70, 70, 70, 70, 70]
        # slope = 0, trend_adjustment = 0
        # base_prob = 70
        # probability = 70
        # score_variance = 0 (high confidence)

        mock_cursor.fetchall.return_value = [
            {'score': 70, 'created_at': '2023-10-05'},
            {'score': 70, 'created_at': '2023-10-04'},
            {'score': 70, 'created_at': '2023-10-03'},
            {'score': 70, 'created_at': '2023-10-02'},
            {'score': 70, 'created_at': '2023-10-01'}
        ]

        result = calculate_success_probability()

        assert result == {
            'probability': 70.0,
            'confidence': 'high',
            'trend': 'declining', # Due to `slope > 0 else 'declining'` logic
            'avg_mock_score': 70.0,
            'message': 'Based on 5 mock tests with high confidence'
        }
        mock_cursor.execute.assert_called_once()
        mock_conn.close.assert_called_once()

def test_calculate_success_probability_database_error():
    with patch('app.services.predictive_analytics.get_db_connection') as mock_get_db:
        # Simulate an exception in database connection
        mock_get_db.side_effect = Exception("Database connection failed")

        result = calculate_success_probability()

        assert result == {
            'probability': 0,
            'confidence': 'low',
            'message': 'Unable to calculate probability due to missing data'
        }

def test_calculate_success_probability_variance_thresholds():
    with patch('app.services.predictive_analytics.get_db_connection') as mock_get_db:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Test low variance: variance < 100
        # Scores: 75, 70, 75, 70, 70. Avg = 72. Variance = (9+4+9+4+4)/5 = 6.
        mock_cursor.fetchall.return_value = [
            {'score': 75, 'created_at': '2023-10-05'},
            {'score': 70, 'created_at': '2023-10-04'},
            {'score': 75, 'created_at': '2023-10-03'},
            {'score': 70, 'created_at': '2023-10-02'},
            {'score': 70, 'created_at': '2023-10-01'}
        ]
        result_low = calculate_success_probability()
        assert result_low['confidence'] == 'high' # variance < 100 -> high

        # Test high variance: variance >= 300
        # Scores: 100, 40, 100, 40, 70. Avg = 70. Variance = (900+900+900+900+0)/5 = 720.
        mock_cursor.fetchall.return_value = [
            {'score': 100, 'created_at': '2023-10-05'},
            {'score': 40, 'created_at': '2023-10-04'},
            {'score': 100, 'created_at': '2023-10-03'},
            {'score': 40, 'created_at': '2023-10-02'},
            {'score': 70, 'created_at': '2023-10-01'}
        ]
        result_high = calculate_success_probability()
        assert result_high['confidence'] == 'low' # variance >= 300 -> low
