import sqlite3
import pytest
from app import create_app
from app.db import get_db

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_progress_trend_optimization(client, app):
    pass
