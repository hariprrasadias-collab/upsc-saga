
import unittest
from unittest.mock import MagicMock, patch, ANY
import json
import sys
import os
from flask import Flask

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app.services.brain_service import BrainService

class TestBrainVault(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.brain = BrainService()
        
        # Mock dependencies
        self.patcher_db = patch('app.db.get_db')
        self.mock_get_db = self.patcher_db.start()
        
        self.patcher_mm = patch('app.services.brain_service.model_manager')
        self.mock_model_manager = self.patcher_mm.start()
        
        self.patcher_auto = patch('app.services.brain_service.BrainService.execute_action')
        self.mock_execute = self.patcher_auto.start()

    def tearDown(self):
        self.patcher_db.stop()
        self.patcher_mm.stop()
        self.patcher_auto.stop()

    def test_brain_vault_parallel_execution(self):
        """Verify that process_task_completion triggers all 15 actions"""
        
        # Setup mocks
        mock_conn = MagicMock()
        self.mock_get_db.return_value = mock_conn
        
        # Mock execute_action to just return success so we don't actually run LLM
        # We want to test that the ORCHESTRATOR submits the tasks
        self.mock_execute.return_value = {"success": True, "message": "Mock Success", "script": "Podcast content", "prompt": "Visual Prompt"}

        # Simulate task completion
        task_data = {"topic": "Democracy", "subject": "Polity", "user_id": 1}
        
        with self.app.app_context():
            # We need to patch ThreadPoolExecutor to run synchronously or check calls
            # Use a real executor but wait for it? Or mock it? 
            # BrainService uses concurrent.futures.ThreadPoolExecutor
            # Let's mock the executor to verify submit calls
            
            with patch('concurrent.futures.ThreadPoolExecutor') as MockExecutor:
                mock_executor_instance = MockExecutor.return_value
                mock_executor_instance.__enter__.return_value = mock_executor_instance
                
                self.brain.process_task_completion(task_data)
                
                # Verify that submit was called for all expected actions
                # We expect ~16 calls now (added Mind Map)
                expected_actions = [
                    "CREATE_FLASHCARDS", "CREATE_MOCK_TEST", "GENERATE_ELI5", 
                    "GENERATE_CHEAT_SHEET", "PREDICT_QUESTIONS", 
                    "GENERATE_TOPIC_LINKAGES", "GENERATE_TIMELINE", 
                    "GENERATE_MAP_WORK", "GENERATE_PODCAST_SCRIPT", 
                    "GENERATE_SOCRATIC_DIALOGUE", "GENERATE_ROLEPLAY_SCENARIO", 
                    "GENERATE_VISUAL_PROMPT", "GENERATE_ESSAY_PROMPT", 
                    "GENERATE_QUOTE_BANK", "FIND_COMMON_PITFALLS",
                    "GENERATE_MIND_MAP" 
                ]
                
                # Get all args passed to submit
                submitted_actions = []
                for call in mock_executor_instance.submit.call_args_list:
                    # call.args[0] is run_action_safe
                    # call.args[1] is action_name
                    if len(call.args) > 1:
                        submitted_actions.append(call.args[1])
                
                # Check coverage
                for action in expected_actions:
                    self.assertIn(action, submitted_actions, f"Action {action} was not submitted!")
                
                print(f"Verified {len(submitted_actions)} actions submitted.")

    def test_run_action_safe_persistence(self):
        """
        Verify that run_action_safe correctly saves results to DB.
        This extracts the inner function logic or we act as if we are the thread.
        Since run_action_safe is defined INSIDE process_task_completion, we can't unit test it directly easily.
        Instead, we will perform an integration-like test where we allow the real ThreadPool to run
        but mock execute_action to return data, and verify DB calls.
        """
        mock_conn = MagicMock()
        self.mock_get_db.return_value = mock_conn
        
        # Setup mock return values for different actions
        def side_effect(action, payload):
            if action == "GENERATE_ESSAY_PROMPT":
                return {"success": True, "prompt": "Essay Content"}
            if action == "GENERATE_MAP_WORK":
                return {"success": True, "locations": [{"name": "Delhi"}]}
            if action == "GENERATE_MIND_MAP":
                return {"success": True, "mind_map": "graph TD; A-->B"}
            if action == "GENERATE_TOPIC_LINKAGES":
                return {"success": True, "data": {"core_themes": ["A"], "cross_linkages": ["B"]}}
            return {"success": True}
            
        self.mock_execute.side_effect = side_effect

        task_data = {"topic": "Democracy", "subject": "Polity"}

        with self.app.app_context():
            # Allow real executor to run (don't mock ThreadPoolExecutor)
            # But we mocked execute_action so no API calls happen.
            
            self.brain.process_task_completion(task_data)
            
            # Verify DB inserts
            found_essay = False
            found_map = False
            found_mind_map = False
            found_neural_log = False
            
            for call in mock_conn.execute.call_args_list:
                args = call.args
                # Check for table names in SQL
                sql = args[0]
                if 'INSERT INTO ai_generated_content' in sql:
                    params = args[1]
                    if params[0] == 'essay_prompt' and params[2] == 'Essay Content':
                        found_essay = True
                    if params[0] == 'map_work' and 'Delhi' in params[2]:
                        found_map = True
                    if params[0] == 'mind_map' and 'graph TD' in params[2]:
                        found_mind_map = True
                
                if 'INSERT INTO neural_hash_logs' in sql:
                    params = args[1]
                    # (topic, 'brain_vault', json_str)
                    if params[0] == 'Democracy' and params[1] == 'brain_vault':
                        found_neural_log = True
            
            self.assertTrue(found_essay, "Essay Prompt was not saved to DB")
            self.assertTrue(found_map, "Map Work was not saved to DB")
            self.assertTrue(found_mind_map, "Mind Map was not saved to DB")
            self.assertTrue(found_neural_log, "Neural Hash Log was not saved to DB")

if __name__ == '__main__':
    unittest.main()
