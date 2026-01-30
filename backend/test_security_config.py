import unittest
import os
import sys

# Ensure backend directory is in path so we can import app
# We assume this script is run from project root or backend/
if os.getcwd().endswith('backend'):
    sys.path.append(os.getcwd())
else:
    sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import create_app

class TestSecurityConfig(unittest.TestCase):
    def setUp(self):
        # Save original env vars
        self.orig_secret = os.environ.get('SECRET_KEY')
        self.orig_env = os.environ.get('FLASK_ENV')
        self.orig_cors = os.environ.get('CORS_ALLOWED_ORIGINS')

    def tearDown(self):
        # Restore env vars
        if self.orig_secret is not None:
            os.environ['SECRET_KEY'] = self.orig_secret
        else:
            os.environ.pop('SECRET_KEY', None)

        if self.orig_env is not None:
            os.environ['FLASK_ENV'] = self.orig_env
        else:
            os.environ.pop('FLASK_ENV', None)

        if self.orig_cors is not None:
            os.environ['CORS_ALLOWED_ORIGINS'] = self.orig_cors
        else:
            os.environ.pop('CORS_ALLOWED_ORIGINS', None)

    def test_default_dev_config(self):
        """Test that dev environment falls back to dev key."""
        os.environ.pop('SECRET_KEY', None)
        os.environ['FLASK_ENV'] = 'development'

        app = create_app()
        self.assertEqual(app.secret_key, 'dev_secret_key_upsc_saga')

    def test_prod_missing_secret(self):
        """Test that production environment generates a random key if SECRET_KEY is missing."""
        os.environ.pop('SECRET_KEY', None)
        os.environ['FLASK_ENV'] = 'production'

        app = create_app()
        self.assertIsNotNone(app.secret_key)
        self.assertNotEqual(app.secret_key, 'dev_secret_key_upsc_saga')
        self.assertNotEqual(app.secret_key, '')

    def test_prod_with_secret(self):
        """Test that production environment uses provided SECRET_KEY."""
        os.environ['SECRET_KEY'] = 'prod_secret_123'
        os.environ['FLASK_ENV'] = 'production'

        app = create_app()
        self.assertEqual(app.secret_key, 'prod_secret_123')

    def test_cors_config(self):
        """Test that CORS configuration doesn't crash app."""
        os.environ['CORS_ALLOWED_ORIGINS'] = 'http://site1.com,http://site2.com'
        app = create_app()
        self.assertTrue(app)

if __name__ == '__main__':
    unittest.main()
