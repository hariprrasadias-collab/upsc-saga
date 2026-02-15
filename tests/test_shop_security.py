import os
import pytest
import sqlite3

# Set environment variable BEFORE importing app to ensure DB path is picked up
TEST_DB = 'test_shop_security.db'
# Ensure we use an absolute path for the test DB
TEST_DB_PATH = os.path.abspath(TEST_DB)
os.environ['DATABASE_PATH'] = TEST_DB_PATH

from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True

    # Initialize the database
    with app.app_context():
        init_db()

    with app.test_client() as client:
        yield client

    # Cleanup
    if os.path.exists(TEST_DB_PATH):
        try:
            # Close any lingering connections?
            # In SQLite, checking if file is locked might be needed but for now just try remove.
            os.remove(TEST_DB_PATH)
        except Exception as e:
            print(f"Cleanup failed: {e}")

def init_db():
    # create_app() already initializes tables via init_core_tables()
    # We only need to seed the test user
    conn = sqlite3.connect(TEST_DB_PATH)

    # Insert test user
    conn.execute('INSERT OR REPLACE INTO users (id, hacksilver, username) VALUES (1, 1000, "test_user")')
    conn.commit()
    conn.close()

def test_shop_exploit_prevention(client):
    # Try to buy Leviathan Axe (cost 200) for 1 hacksilver
    # This item is from the frontend catalog which we want to support securely
    response = client.post('/api/shop/buy', json={
        'item_id': 'leviathan_axe',
        'item_name': 'Leviathan Axe',
        'cost': 1 # Malicious cost
    })

    # Let's check the user balance in DB to be sure.
    conn = sqlite3.connect(TEST_DB_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT hacksilver FROM users WHERE id = 1').fetchone()
    conn.close()

    print(f"User balance after purchase: {user['hacksilver']}")

    # If vulnerable: balance would be 999.
    # If fixed (and charges real price): balance would be 800.

    if user['hacksilver'] == 999:
        pytest.fail("Security vulnerability: User was charged only 1 hacksilver!")

    assert user['hacksilver'] == 800, f"User should be charged the correct amount (200), but has {user['hacksilver']}"
