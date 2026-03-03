import pytest
import json
import time
import os
import tempfile
from flask import jsonify, Blueprint

# Force rate limiter to use a temp file for tests BEFORE importing app
temp_rl_fd, temp_rl_path = tempfile.mkstemp(suffix='.json')
temp_db_fd, temp_db_path = tempfile.mkstemp(suffix='.db')
os.environ['RATE_LIMIT_FILE'] = temp_rl_path
os.environ['DATABASE_PATH'] = temp_db_path

from app import create_app
from app.db import get_db
import app.db
import app.middleware as app_middleware

app.db.DATABASE = temp_db_path
app.middleware.RATE_LIMIT_FILE = temp_rl_path

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "TESTING_RATE_LIMITER": True,
        "DATABASE": temp_db_path
    })
    
    # We create a dummy test blueprint under /api/ to test the middleware
    test_bp = Blueprint('test_routes', __name__, url_prefix='/api/test')
    
    @test_bp.route('/success', methods=['GET'])
    def test_success():
        return jsonify({"message": "Hello World", "data_point": 42})
        
    @test_bp.route('/error', methods=['GET'])
    def test_error():
        # Even if route returns a simple dict, envelope wraps it
        return jsonify({"error": "Something went wrong"}), 400
        
    app.register_blueprint(test_bp)

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_request_id_injected(client):
    response = client.get('/api/test/success')
    assert response.status_code == 200
    assert 'X-Request-ID' in response.headers
    
    data = json.loads(response.data)
    assert 'request_id' in data
    assert response.headers['X-Request-ID'] == data['request_id']

def test_response_enveloping_success(client):
    response = client.get('/api/test/success')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check envelope structure
    assert data['success'] is True
    assert 'data' in data
    assert data['data']['message'] == 'Hello World'
    assert data['data']['data_point'] == 42
    assert 'error' not in data

def test_response_enveloping_error(client):
    response = client.get('/api/test/error')
    assert response.status_code == 400
    data = json.loads(response.data)
    
    # Check envelope structure
    assert data['success'] is False
    assert 'error' in data
    assert data['error'] == 'Something went wrong'
    assert 'data' not in data

def test_rate_limiter(client):
    # Clear the in-memory global state before the test
    app_middleware._rate_limits = {}

    # Reset limit file so we get exactly 60 clean requests
    with open(temp_rl_path, 'w') as f:
        json.dump({}, f)
        
    # The default max is 60. We will hit it exactly 60 times.
    for _ in range(60):
        res = client.get('/api/test/success')
        assert res.status_code == 200
        
    # The 61st should be rate-limited (429)
    res = client.get('/api/test/success')
    assert res.status_code == 429
    data = json.loads(res.data)
    
    assert data['success'] is False
    assert "Rate limit exceeded" in data['error']
