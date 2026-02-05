import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# We need to mock app.db.get_db because warmap imports it
sys.modules['app.db'] = MagicMock()

from app.routes.warmap import get_google_client_config

class TestWarmapConfig(unittest.TestCase):
    def test_config_missing_vars(self):
        # Clear specific env vars
        with patch.dict(os.environ, {}, clear=True):
             # We might have other env vars needed for imports, but warmap.py only checks specific ones in get_google_client_config
            config = get_google_client_config()
            self.assertIsNone(config)

    def test_config_valid_vars(self):
        env_vars = {
            'GOOGLE_CLIENT_ID': 'test_id',
            'GOOGLE_CLIENT_SECRET': 'test_secret',
            'GOOGLE_PROJECT_ID': 'test_project'
        }
        with patch.dict(os.environ, env_vars):
            config = get_google_client_config()
            self.assertIsNotNone(config)
            self.assertEqual(config['installed']['client_id'], 'test_id')
            self.assertEqual(config['installed']['client_secret'], 'test_secret')
            self.assertEqual(config['installed']['project_id'], 'test_project')

if __name__ == '__main__':
    unittest.main()
