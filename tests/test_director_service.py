import pytest
from unittest.mock import patch, MagicMock

from app.services.director_service import director_service
from app import create_app

@pytest.fixture
def app_context():
    app = create_app()
    with app.app_context():
        yield app

def test_check_user_velocity_error_path(capsys):
    """Test that check_user_velocity handles exceptions correctly."""
    with patch('app.services.director_service.get_db') as mock_get_db:
        # Make the database connection throw an exception
        mock_get_db.side_effect = Exception("Mocked DB Connection Error")

        result = director_service.check_user_velocity(user_id=1)

        # Verify the error dictionary is returned
        assert "error" in result
        assert result["error"] == "Mocked DB Connection Error"

        # Verify the error was printed
        captured = capsys.readouterr()
        assert "Director Error: Mocked DB Connection Error" in captured.out

def test_trigger_intervention_error_path_model(capsys):
    """Test that _trigger_intervention handles exceptions from model_manager correctly."""
    with patch('app.services.director_service.model_manager.generate_content') as mock_generate:
        # Make the content generation throw an exception
        mock_generate.side_effect = Exception("Mocked Model Error")

        # Call the intervention (it handles the error internally)
        director_service._trigger_intervention("STAGNATION", user_id=1)

        # Verify the error was caught and printed
        captured = capsys.readouterr()
        assert "Intervention Failed: Mocked Model Error" in captured.out

def test_trigger_intervention_error_path_db(app_context, capsys):
    """Test that _trigger_intervention handles exceptions from db insertion correctly."""
    with patch('app.services.director_service.model_manager.generate_content') as mock_generate:
        # Mock a successful generation
        mock_response = MagicMock()
        mock_response.text = "Read 1 page"
        mock_generate.return_value = mock_response

        with patch('app.db.get_db') as mock_get_db_module:
            # We patch app.db.get_db since the method imports it locally
            mock_get_db_module.side_effect = Exception("Mocked DB Insert Error")

            with patch('app.services.director_service.get_db') as mock_get_db_service:
                # We also patch the module-level import just in case
                mock_get_db_service.side_effect = Exception("Mocked DB Insert Error")

                # Call the intervention
                director_service._trigger_intervention("STAGNATION", user_id=1)

                # Verify the error was caught and printed
                captured = capsys.readouterr()
                assert "Intervention Failed: Mocked DB Insert Error" in captured.out
