import pytest
import sqlite3
import os
import tempfile
from unittest.mock import patch, MagicMock

temp_db_fd, temp_db_path = tempfile.mkstemp(suffix='.db')
os.environ['DATABASE_PATH'] = temp_db_path

from app import create_app
from app.db import get_db
import app.db

app.db.DATABASE = temp_db_path
from app.services.game_engine import trigger_event, calculate_and_apply_rewards

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
        # Let create_app initialize the DB correctly using its own schemas.
        # We don't need to manually create tables that might conflict or be incomplete.
        pass

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def setup_db(app):
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()
        # Create a test user
        try:
            cursor.execute('''
                INSERT INTO users (id, username, password, current_xp, level, max_xp, hacksilver, strength_stat, runic_stat, vitality_stat, luck_stat)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (1, 'TestUser', 'password', 50, 1, 100, 20, 5, 5, 5, 5))
            conn.commit()
        except sqlite3.IntegrityError:
            pass # User already exists
        except sqlite3.OperationalError:
            pass # Ignore if table definition differs during test setup

        yield conn

def test_trigger_event_known_event(app, setup_db):
    with app.app_context():
        with patch('app.services.game_engine.calculate_and_apply_rewards') as mock_calc:
            mock_calc.return_value = {
                "xp_gained": 100,
                "hs_gained": 50,
                "is_crit": False,
                "leveled_up": False,
                "lore": None,
                "new_balance": 70
            }
            result = trigger_event('STRATEGY_COMMIT', 1)

            mock_calc.assert_called_once_with(1, 100, 50)

            assert result['success'] is True
            assert result['message'] == 'Strategic Directive Committed!'
            assert result['rewards']['xp_gained'] == 100

def test_trigger_event_unknown_event(app, setup_db):
    with app.app_context():
        result = trigger_event('UNKNOWN_EVENT', 1)
        assert result['success'] is False
        assert result['message'] == 'Unknown Event'

def test_calc_apply_missing_user(app, setup_db):
    with app.app_context():
        # Call with user id 999 which does not exist initially
        result = calculate_and_apply_rewards(999, 10, 5)

        # Default user should be created
        conn = get_db()
        cursor = conn.cursor()
        user = cursor.execute('SELECT * FROM users WHERE id = ?', (999,)).fetchone()

        assert user is not None
        assert user['username'] == 'Hero_999'
        assert user['level'] == 1

        # Verify rewards applied properly to default user (who has 5 luck)
        # XP calculation: Base XP (10) * multipliers (1.0). If crit, x2.
        # So xp_gained is either 10 or 20.
        assert result['xp_gained'] in [10, 20]
        # HS calculation: Base HS (5). Variance is 10% of 5 = 0. Range 5 to 5. So hs_gained is 5 or 10.
        assert result['hs_gained'] in [5, 10]

def test_calc_apply_item_buffs(app, setup_db):
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()

        # Add a user id 2
        cursor.execute('''
            INSERT INTO users (id, username, current_xp, level, max_xp, hacksilver, strength_stat, runic_stat, vitality_stat, luck_stat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (2, 'BuffUser', 0, 1, 100, 0, 1, 1, 1, 0)) # luck 0 means 0% crit chance

        # Add items to user 2
        cursor.execute("INSERT INTO inventory (user_id, item_id) VALUES (?, ?)", (2, 'leviathan_axe'))
        cursor.execute("INSERT INTO inventory (user_id, item_id) VALUES (?, ?)", (2, 'chaos_blades'))
        conn.commit()

        # Test leviathan axe buff
        result_axe = calculate_and_apply_rewards(2, 100, 0, tags=['history'])
        assert result_axe['xp_gained'] == 120 # 100 * 1.20

        # Test chaos blades buff
        result_blades = calculate_and_apply_rewards(2, 100, 0, tags=['polity'])
        assert result_blades['xp_gained'] == 120 # 100 * 1.20

        # Test both buffs (the multipliers are added: 1.0 + 0.20 + 0.20 = 1.40)
        result_both = calculate_and_apply_rewards(2, 100, 0, tags=['history', 'polity'])
        assert result_both['xp_gained'] == 140 # 100 * 1.40

        # Test no matching tags
        result_none = calculate_and_apply_rewards(2, 100, 0, tags=['geography'])
        assert result_none['xp_gained'] == 100 # 100 * 1.0

def test_calc_apply_luck_critical(app, setup_db):
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()

        # Add user id 3 with high luck
        cursor.execute('''
            INSERT INTO users (id, username, current_xp, level, max_xp, hacksilver, strength_stat, runic_stat, vitality_stat, luck_stat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (3, 'LuckyUser', 0, 1, 100, 0, 1, 1, 1, 10)) # luck 10 = 20% crit chance
        conn.commit()

        # Mock random.randint to force a critical hit (roll 1)
        with patch('app.services.game_engine.random.randint', return_value=1):
            result_crit = calculate_and_apply_rewards(3, 100, 50)
            # Critical hits double the final xp and hacksilver
            assert result_crit['is_crit'] is True
            assert result_crit['xp_gained'] == 200 # 100 * 2
            # Base hs is 50. Variance is 10% (5).
            # random.randint(45, 55) is called for HS. Since we mocked it to return 1,
            # final_hs = 1 * 2 = 2. Wait, the mock returns 1 for BOTH calls!
            # Let's use side_effect to return 50 for hs, and 1 for roll.

        with patch('app.services.game_engine.random.randint', side_effect=[50, 1]):
            # First call: random.randint(max(1, base_hs - variance), base_hs + variance)
            # Second call: random.randint(1, 100) -> roll
            result_crit2 = calculate_and_apply_rewards(3, 100, 50)
            assert result_crit2['is_crit'] is True
            assert result_crit2['xp_gained'] == 200
            assert result_crit2['hs_gained'] == 100 # 50 * 2

        # Test NO critical hit
        with patch('app.services.game_engine.random.randint', side_effect=[50, 99]):
            result_no_crit = calculate_and_apply_rewards(3, 100, 50)
            assert result_no_crit['is_crit'] is False
            assert result_no_crit['xp_gained'] == 100
            assert result_no_crit['hs_gained'] == 50

def test_calc_apply_level_up(app, setup_db):
    with app.app_context():
        conn = get_db()
        cursor = conn.cursor()

        # Add user id 4 very close to leveling up
        cursor.execute('''
            INSERT INTO users (id, username, current_xp, level, max_xp, hacksilver, strength_stat, runic_stat, vitality_stat, luck_stat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (4, 'LevelUpUser', 90, 1, 100, 10, 5, 5, 5, 5))
        conn.commit()

        # Mock luck stat so we don't accidentally get a crit, and hs variance
        with patch('app.services.game_engine.random.randint', side_effect=[10, 99]):
            # Mock model_manager
            with patch('app.services.model_manager.model_manager') as mock_model:
                mock_model.is_configured = True

                # Setup a mock response object
                mock_response = MagicMock()
                mock_response.text = "You have evolved to a mighty administrator."
                mock_model.generate_content.return_value = mock_response

                # 90 + 20 = 110 XP. Max is 100, so leveled up to level 2 with 10 leftover XP
                result = calculate_and_apply_rewards(4, 20, 10)

                assert result['leveled_up'] is True
                assert result['lore'] == "You have evolved to a mighty administrator."

                # Fetch updated user
                user = cursor.execute('SELECT * FROM users WHERE id = ?', (4,)).fetchone()

                assert user['level'] == 2
                assert user['current_xp'] == 10
                assert user['max_xp'] == 120 # round(100 * 1.2)
                assert user['strength_stat'] == 6
                assert user['runic_stat'] == 6
                assert user['vitality_stat'] == 6
                assert user['luck_stat'] == 6

        # Test level up when model is not configured
        cursor.execute('''
            INSERT INTO users (id, username, current_xp, level, max_xp, hacksilver, strength_stat, runic_stat, vitality_stat, luck_stat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (5, 'FallbackLoreUser', 90, 1, 100, 10, 5, 5, 5, 5))
        conn.commit()

        with patch('app.services.game_engine.random.randint', side_effect=[10, 99]):
            with patch('app.services.model_manager.model_manager') as mock_model:
                mock_model.is_configured = False

                result_fallback = calculate_and_apply_rewards(5, 20, 10)

                assert result_fallback['leveled_up'] is True
                # No lore generation
                assert result_fallback['lore'] is None

        # Test level up when model throws an exception
        cursor.execute('''
            INSERT INTO users (id, username, current_xp, level, max_xp, hacksilver, strength_stat, runic_stat, vitality_stat, luck_stat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (6, 'ExceptionLoreUser', 90, 1, 100, 10, 5, 5, 5, 5))
        conn.commit()

        with patch('app.services.game_engine.random.randint', side_effect=[10, 99]):
            with patch('app.services.model_manager.model_manager') as mock_model:
                mock_model.is_configured = True
                mock_model.generate_content.side_effect = Exception("API Error")

                result_exception = calculate_and_apply_rewards(6, 20, 10)

                assert result_exception['leveled_up'] is True
                # Lore generation exception
                assert result_exception['lore'] == "Level 2 Reached! Power Overwhelming!"
