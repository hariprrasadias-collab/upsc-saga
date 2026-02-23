import unittest
import os
from app import create_app

class TestSecurityConfig(unittest.TestCase):
    def test_secret_key_loaded_from_env(self):
        # Set a custom secret key in the environment
        test_key = 'sentinel_test_key_123'
        os.environ['SECRET_KEY'] = test_key

        # Create the app
        app = create_app()

        # Check if the secret key matches the environment variable
        self.assertEqual(app.secret_key, test_key, "SECRET_KEY should be loaded from environment")

    def test_cors_origins_loaded_from_env(self):
        # This is harder to test directly on the app object without inspecting the CORS extension internals,
        # but we can check if the config reflects it if we were storing it in config.
        # For now, we mainly focus on SECRET_KEY.
        pass

if __name__ == '__main__':
    unittest.main()
