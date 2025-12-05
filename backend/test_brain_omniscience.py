
import pytest
import sqlite3
import threading
import time
import os
import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from flask import Flask

def test_brain_automation_omniscience_flow():
    # 1. Setup minimal Flask app and DB
    from app import create_app
    from app.db import get_db

    # Manually initialize DB tables
    def init_db_tables():
        conn = get_db()
        # Study Plan Table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS study_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                user_id INTEGER DEFAULT 1
            )
        ''')
        # Study Tasks Table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS study_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER,
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                subject TEXT NOT NULL,
                topic TEXT NOT NULL,
                resource_link TEXT,
                status TEXT DEFAULT 'pending',
                google_event_id TEXT,
                FOREIGN KEY (plan_id) REFERENCES study_plans (id)
            )
        ''')
        # Tasks (generic tasks)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                due_date TEXT,
                xp_reward INTEGER,
                associated_stat TEXT,
                isCompleted BOOLEAN DEFAULT 0,
                is_quest BOOLEAN DEFAULT 0,
                start_time TEXT,
                end_time TEXT
            )
        ''')
        # Flashcards Decks
        conn.execute('''
            CREATE TABLE IF NOT EXISTS decks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                subject TEXT
            )
        ''')
        # Flashcards
        conn.execute('''
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id INTEGER,
                front TEXT,
                back TEXT,
                source TEXT
            )
        ''')
        # Mock Tests
        conn.execute('''
            CREATE TABLE IF NOT EXISTS mock_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                subject TEXT,
                total_questions INTEGER,
                duration_minutes INTEGER,
                test_type TEXT,
                total_marks INTEGER
            )
        ''')
        # Custom Bosses
        conn.execute('''
            CREATE TABLE IF NOT EXISTS custom_bosses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                filters TEXT,
                is_active BOOLEAN
            )
        ''')
        # Syllabus Topics (for tracking)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS syllabus_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                topic TEXT,
                status TEXT DEFAULT 'Not Started',
                last_updated TEXT
            )
        ''')
        # Users (for XP)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                current_xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                max_xp INTEGER DEFAULT 100,
                hacksilver INTEGER DEFAULT 0,
                strength_stat INTEGER DEFAULT 5,
                runic_stat INTEGER DEFAULT 5,
                vitality_stat INTEGER DEFAULT 5,
                luck_stat INTEGER DEFAULT 5
            )
        ''')
        # Inventory (for game engine checks)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                item_id TEXT
            )
        ''')
        # Mind Maps
        conn.execute('''
            CREATE TABLE IF NOT EXISTS mind_maps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                root_node TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Issue Mappings
        conn.execute('''
            CREATE TABLE IF NOT EXISTS issue_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER,
                subject TEXT,
                syllabus_topic TEXT,
                paper TEXT,
                relevance_score REAL,
                key_linkages TEXT,
                exam_utility TEXT,
                created_at TEXT
            )
        ''')
        # Neural Logs
        conn.execute('''
            CREATE TABLE IF NOT EXISTS neural_hash_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_text_hash TEXT,
                context_type TEXT,
                decoded_data TEXT,
                created_at TEXT
            )
        ''')
        # Badges (simplified)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                icon TEXT,
                unlock_criteria TEXT,
                xp_reward INTEGER,
                category TEXT,
                rarity TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                badge_id INTEGER,
                unlocked_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS badge_progress (
                user_id INTEGER,
                badge_id INTEGER,
                current_value INTEGER,
                target_value INTEGER,
                last_updated TEXT,
                PRIMARY KEY (user_id, badge_id)
            )
        ''')

        # Seed user
        conn.execute("INSERT OR IGNORE INTO users (id, username, current_xp) VALUES (1, 'Hero', 0)")

        # Seed syllabus topic
        conn.execute("INSERT INTO syllabus_topics (subject, topic, status) VALUES ('Economy', 'Inflation', 'Not Started')")

        conn.commit()

    # Use a test database
    db_path = 'test_automation_omniscience.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    # Patch DATABASE constant
    with patch('app.db.DATABASE', db_path):
        app = create_app()

        with app.app_context():
            init_db_tables()
            conn = get_db()

            # Create a dummy study plan and task
            cursor = conn.execute("INSERT INTO study_plans (start_date, end_date, is_active) VALUES ('2023-01-01', '2023-12-31', 1)")
            plan_id = cursor.lastrowid

            cursor = conn.execute("""
                INSERT INTO study_tasks (plan_id, date, start_time, end_time, subject, topic, status)
                VALUES (?, '2023-01-01', '09:00', '10:00', 'Economy', 'Inflation', 'pending')
            """, (plan_id,))
            task_id = cursor.lastrowid
            conn.commit()

            # Mock External Services
            with patch('app.services.brain_service.brain_service.execute_action') as mock_action, \
                 patch('app.services.mindmap_service.MindMapService.generate_mindmap') as mock_mindmap_gen, \
                 patch('app.services.syllabus_tracker.SyllabusTracker.update_topic_progress') as mock_syllabus_update, \
                 patch('app.services.game_engine.trigger_event') as mock_trigger_event, \
                 patch('app.services.ravens_service.RavensService.search_articles') as mock_ravens_search, \
                 patch('app.services.brain_service.BrainService._identify_book_for_topic') as mock_book_id, \
                 patch('app.services.badge_service.badge_service.check_and_unlock_badges') as mock_badge_unlock, \
                 patch('app.services.syllabus_tracker.SyllabusTracker.get_recently_completed') as mock_recent_topics:

                # Configure Mocks
                def side_effect(action_type, payload):
                    if action_type == 'GENERATE_TOPIC_LINKAGES':
                        return {"success": True, "linkages": ["Link 1", "Link 2"]}
                    return {"success": True, "explanation": "Mock", "script": "Mock Script", "prompt": "Mock Prompt", "content": "Mock Content", "quotes": "Q", "data": "D"}

                mock_action.side_effect = side_effect

                mock_mindmap_gen.return_value = {"name": "Inflation", "children": []}
                mock_syllabus_update.return_value = {'success': True}
                mock_trigger_event.return_value = {'success': True}
                mock_ravens_search.return_value = []
                mock_book_id.return_value = None
                mock_badge_unlock.return_value = []
                mock_recent_topics.return_value = [{'topic': 'Monetary Policy'}, {'topic': 'Fiscal Policy'}]

                # Simulate the request
                with app.test_client() as client:
                    response = client.put(f'/api/planner/task/{task_id}/status', json={'status': 'Completed'})
                    assert response.status_code == 200

                    # Wait for background thread
                    time.sleep(2)

                    # Verify Brain Actions
                    action_calls = [c[0][0] for c in mock_action.call_args_list]
                    print(f"Brain actions called: {action_calls}")

                    assert "GENERATE_TOPIC_LINKAGES" in action_calls
                    assert "GENERATE_CHEAT_SHEET" in action_calls
                    assert "GENERATE_QUOTE_BANK" in action_calls

                    # Verify Linkage logic
                    link_call = [c for c in mock_action.call_args_list if c[0][0] == "GENERATE_TOPIC_LINKAGES"][0]
                    assert "Monetary Policy" in link_call[0][1]['related_topics']

                    print("\nTest Passed: All omniscience brain automation steps triggered.")

if __name__ == "__main__":
    test_brain_automation_omniscience_flow()
