import pytest
from app import create_app
import tempfile
import os
import json

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DATABASE": db_path
    })

    yield app
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

def test_update_autonomy_settings_invalid_input(client):
    response = client.post('/api/autonomy/settings', json={'autonomy_level': 'invalid_level'})

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert "Invalid autonomy level: invalid_level" in data['error']
