import pytest
from unittest.mock import patch, MagicMock
from app.services.pyq_analytics import get_topic_trend

@patch('app.services.pyq_analytics.get_db')
def test_get_topic_trend(mock_get_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock row factory behaviour somewhat
    mock_cursor.fetchall.return_value = [
        {'year': 2020, 'count': 5},
        {'year': 2021, 'count': 3},
        {'year': 2022, 'count': 8}
    ]

    result = get_topic_trend('History')

    # Check that SQL execution happens
    mock_cursor.execute.assert_called_once()

    # Verify the SQL query formatting (approximately)
    call_args = mock_cursor.execute.call_args
    query = call_args[0][0]
    params = call_args[0][1]

    assert "SELECT year, COUNT(*) as count" in query
    assert "FROM pyq_questions" in query
    assert "WHERE topic = ?" in query
    assert "GROUP BY year ORDER BY year" in query
    assert params == ['History']

    # Verify results
    assert len(result) == 3
    assert result[0]['year'] == 2020
    assert result[0]['count'] == 5
    assert result[2]['year'] == 2022
    assert result[2]['count'] == 8

    mock_conn.close.assert_called_once()

@patch('app.services.pyq_analytics.get_db')
def test_get_topic_trend_with_paper(mock_get_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [
        {'year': 2020, 'count': 2}
    ]

    # Although paper isn't actively filtered in the current SQL query implementation,
    # we test that calling it with the argument doesn't break and passes the same query.
    result = get_topic_trend('History', paper='GS1')

    mock_cursor.execute.assert_called_once()

    call_args = mock_cursor.execute.call_args
    query = call_args[0][0]
    params = call_args[0][1]

    assert "SELECT year, COUNT(*) as count" in query
    assert "WHERE topic = ?" in query
    assert params == ['History']

    assert len(result) == 1
    assert result[0]['year'] == 2020
    assert result[0]['count'] == 2

    mock_conn.close.assert_called_once()
