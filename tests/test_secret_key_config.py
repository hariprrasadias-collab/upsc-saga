
import sys
import os
import logging

# Add the backend directory to sys.path so we can import 'app'
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend'))
sys.path.append(backend_path)

# Set the environment variable BEFORE importing the app
test_key = 'test_secret_key'
os.environ['SECRET_KEY'] = test_key
# Ensure FLASK_ENV is not production so we don't trigger the warning (or we could test the warning too)
os.environ['FLASK_ENV'] = 'development'

try:
    from app import create_app

    # Initialize app
    app = create_app()

    # Check the secret key
    current_key = app.secret_key
    print(f"Current app.secret_key: {current_key}")

    # Assert that it is the env var value
    if current_key == test_key:
        print("✅ Verification successful: SECRET_KEY is correctly loaded from environment variable.")
    elif current_key == 'dev_secret_key_upsc_saga':
        print("❌ Verification failed: SECRET_KEY is still hardcoded.")
        sys.exit(1)
    else:
        print(f"❌ Verification failed: Unexpected secret key: {current_key}")
        sys.exit(1)

except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
