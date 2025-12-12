
import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os
from flask import Flask, jsonify

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app.routes.model_answers import search_model_answers, bp

class TestRogueRoute(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(bp)
        
        self.patcher_db = patch('app.routes.model_answers.get_db')
        self.mock_db = self.patcher_db.start()
        
        self.patcher_mm = patch('app.routes.model_answers.model_manager')
        self.mock_model_manager = self.patcher_mm.start()

    def tearDown(self):
        self.patcher_db.stop()
        self.patcher_mm.stop()

    def test_search_model_answers_success(self):
        # Setup DB
        mock_conn = MagicMock()
        self.mock_db.return_value = mock_conn
        # Make cursor() and execute() return self so fetchall() is always on mock_conn
        mock_conn.cursor.return_value = mock_conn
        mock_conn.execute.return_value = mock_conn
        mock_conn.fetchall.side_effect = [
            [
                {'id': 1, 'title': 'Democracy Essay', 'question_text': 'What is democracy?', 'tags': '["politics"]'},
                {'id': 2, 'title': 'Economy', 'question_text': 'What is inflation?', 'tags': '["eco"]'}
            ],
            [
                {'id': 1, 'title': 'Democracy Essay', 'question_text': 'What is democracy?', 'tags': '["politics"]'}
            ]
        ]

        # Setup AI Response
        mock_response = MagicMock()
        mock_response.text = "```json\n{\"answer_ids\": [1]}\n```" 
        self.mock_model_manager.generate_content.return_value = mock_response

        # Execute with request context
        with self.app.test_request_context(json={'query': 'democracy'}):
            response = search_model_answers()
            if isinstance(response, tuple):
                response = response[0]
            
            # response is a Response object
            data = response.get_json()
            
            self.assertEqual(data['success'], True)
            self.assertEqual(data['method'], 'ai_search')
            self.assertEqual(len(data['answers']), 1)
            self.assertEqual(data['answers'][0]['id'], 1)

    def test_search_model_answers_empty_db(self):
        mock_conn = MagicMock()
        self.mock_db.return_value = mock_conn
        # Simple empty return
        mock_conn.execute.return_value.fetchall.return_value = [] 
        # Also handle unification just in case
        mock_conn.execute.return_value = mock_conn
        mock_conn.fetchall.return_value = []

        with self.app.test_request_context(json={'query': 'test'}):
            response = search_model_answers()
            if isinstance(response, tuple):
                response = response[0]
            
            data = response.get_json()
            
            self.assertEqual(data['success'], True)
            self.assertEqual(data['method'], 'ai_search_empty')
            self.assertEqual(data['answers'], [])

    def test_search_model_answers_robust_parsing(self):
        mock_conn = MagicMock()
        self.mock_db.return_value = mock_conn
        
        mock_conn.cursor.return_value = mock_conn
        mock_conn.execute.return_value = mock_conn
        mock_conn.fetchall.side_effect = [
            [{'id': 1, 'title': 'A', 'question_text': 'Q', 'tags': '[]'}],
            [{'id': 1, 'title': 'A', 'question_text': 'Q', 'tags': '[]'}]
        ]

        mock_response = MagicMock()
        mock_response.text = "Sure!\n\n{ \"answer_ids\": [1] }\n\nValues."
        self.mock_model_manager.generate_content.return_value = mock_response

        with self.app.test_request_context(json={'query': 'democracy'}):
            response = search_model_answers()
            if isinstance(response, tuple):
                response = response[0]
            
            data = response.get_json()
            
            self.assertEqual(data['success'], True)
            self.assertEqual(len(data['answers']), 1)

if __name__ == '__main__':
    unittest.main()
