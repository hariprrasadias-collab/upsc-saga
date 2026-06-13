import pytest
from app import create_app
from app.db import get_db

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_subject_wise(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1
    response = client.get('/api/analytics/subject-wise')
    assert response.status_code == 200
    data = response.json
    if 'data' in data:
        data = data['data']
    assert type(data) is list
    assert len(data) == 6
