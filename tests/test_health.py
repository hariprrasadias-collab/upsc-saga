import pytest
import json
import os
import tempfile

temp_db_fd, temp_db_path = tempfile.mkstemp(suffix='.db')
os.environ['DATABASE_PATH'] = temp_db_path

from app import create_app
from app.db import get_db
import app.db

app.db.DATABASE = temp_db_path

@pytest.fixture
def app():
    # Setup test app
    app = create_app()
    app.config.update({
        "TESTING": True,
        # In-memory DB for tests
        "DATABASE": ":memory:"
    })
    
    with app.app_context():
        conn = get_db()
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS pyq_questions (id INTEGER PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS flashcards (id INTEGER PRIMARY KEY);
        ''')
        conn.commit()
        
    # DB is initialized by app_context automatically
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert data['db'] == 'ok'
    assert 'timestamp' in data

def test_metrics(client):
    response = client.get('/metrics')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert 'total_questions' in data
    assert 'total_users' in data
    assert data['total_questions'] >= 0
    assert data['total_users'] >= 0
    assert data['uptime_seconds'] >= 0
