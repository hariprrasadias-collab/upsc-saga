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
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DATABASE": temp_db_path
    })
    
    with app.app_context():
        conn = get_db()
        
        # We MUST create the table because create_app() does not initialize pyq_questions automatically
        conn.executescript('''
            DROP TABLE IF EXISTS pyq_questions;
            CREATE TABLE pyq_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_text TEXT,
                option_a TEXT, option_b TEXT, option_c TEXT, option_d TEXT,
                correct_option TEXT, explanation TEXT,
                subject TEXT, topic TEXT, subtopic TEXT,
                difficulty TEXT, year INTEGER,
                is_favorite BOOLEAN DEFAULT 0
            );
        ''')
        
        # Clear existing data in case of re-use across tests
        conn.execute('DELETE FROM pyq_questions')
        
        # Seeding 10 questions
        for i in range(1, 11):
            conn.execute('''
                INSERT INTO pyq_questions (question_text, year, correct_option, explanation, subject, topic, difficulty) 
                VALUES (?, ?, 'A', 'Expl', 'History', 'Modern', 'Medium')
            ''', (f"Test Question {i}", 2020))
        conn.commit()

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_pyq_pagination(client):
    # Request 5 items
    response = client.get('/api/pyq/questions?per_page=5')
    assert response.status_code == 200, response.data
    data = json.loads(response.data)
    
    # Middleware wraps API responses!
    assert data.get('success') is True
    assert 'request_id' in data
    
    payload = data['data']
    assert 'total' in payload
    assert payload['total'] == 10
    assert payload['page'] == 1
    assert payload['per_page'] == 5
    assert len(payload['data']) == 5
    
def test_pyq_pagination_page_2(client):
    response = client.get('/api/pyq/questions?page=2&per_page=3')
    assert response.status_code == 200, response.data
    data = json.loads(response.data)['data']
    
    assert data['page'] == 2
    assert data['per_page'] == 3
    assert len(data['data']) == 3
    assert data['total'] == 10
    # ID order should be descending by year, asc by ID. Since year is same (2020), asc by ID.
    # Elements 4, 5, 6 (IDs 4, 5, 6)
    assert data['data'][0]['id'] == 4
