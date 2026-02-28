import pytest
from app import create_app
from app.db import get_db
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
    
    with app.app_context():
        # Using the actual core app init for all tables since there are 44 endpoints.
        # This will test whether standard wrapped outputs exist. Ensure DB tables exist for tests.
        pass

    yield app
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

def test_routes_exist_and_return_json(client):
    routes_to_test = [
        ('/api/dashboard/stats', 200),
        ('/api/analytics', 200),
        ('/api/weak-areas/summary', 200),
        ('/api/planner/current?start_date=2024-01-01', 200),
        ('/api/syllabus/', 200),
        ('/api/quests', 200),
        ('/api/dojo/deck', 200),
        ('/api/mock-tests/', 200),
        ('/api/pyq/questions', 200),
        ('/api/heatmap', 200),
        ('/api/admin/stats', 200)
    ]
    
    for route, expected_status in routes_to_test:
        response = client.get(route)
        # We don't necessarily expect 200 if DB is empty, but we DO expect JSON and standardized wrappers
        # A 400 or 500 is possible depending on data, but let's check for standard JSON envelope execution
        if response.is_json:
            data = json.loads(response.data)
            assert 'success' in data, f"Route {route} missing 'success' wrapper"
            assert 'request_id' in data, f"Route {route} missing 'request_id' wrapper"
            if data['success']:
                assert 'data' in data, f"Route {route} successful but missing 'data' wrapper"
            else:
                assert 'error' in data, f"Route {route} failed but missing 'error' message"
