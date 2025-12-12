
import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.services.triangulation_service import analyze_topic_triangulation
from app.services.essay_evaluator import EssayEvaluator
from app.services.hephaestus_service import HephaestusService
from app.services.self_review import SelfReviewService
from app.services.night_watchman import NightWatchman
from app.services.mindmap_service import MindMapService
from app.services.mimir_service import MimirService
from app.services.issue_mapper import map_article_to_syllabus

class TestTertiaryServices(unittest.TestCase):

    @patch('app.services.triangulation_service.model_manager')
    @patch('app.services.triangulation_service.get_db')
    def test_triangulation(self, mock_db, mock_mm):
        # Mock Response
        text = "Analysis:\n```json\n{\"core_topic\": " + json.dumps("Test Topic") + "}\n```"
        mock_mm.generate_content.return_value = MagicMock(text=text)
        mock_db.return_value.execute.return_value.fetchall.return_value = []
        
        result = analyze_topic_triangulation("Test Text")
        self.assertEqual(result['topic'], "Test Topic")

    @patch('app.services.essay_evaluator.model_manager')
    def test_essay_evaluator(self, mock_mm):
        evaluator = EssayEvaluator()
        text = "Evaluation:\n```json\n{\"score\": 120}\n```"
        mock_mm.generate_content.return_value = MagicMock(text=text)
        
        result = evaluator.evaluate_essay("Topic", "Content")
        self.assertEqual(result['score'], 120)

    @patch('app.services.hephaestus_service.model_manager')
    def test_hephaestus(self, mock_mm):
        h = HephaestusService()
        text = "Here is the fix:\n```python\nprint('fixed')\n```"
        
        code = h._extract_code_block(text)
        self.assertEqual(code, "print('fixed')")
        
        # Test fallback
        text_fallback = "```\nprint('fixed_fallback')\n```"
        code_fb = h._extract_code_block(text_fallback)
        self.assertEqual(code_fb, "print('fixed_fallback')")

    @patch('app.services.self_review.model_manager')
    @patch('app.services.self_review.get_db')
    def test_self_review(self, mock_db, mock_mm):
        sr = SelfReviewService()
        text = "Plan:\n```json\n{\"plan\": [\"Sleep\"]}\n```"
        mock_mm.generate_content.return_value = MagicMock(text=text)
        
        # Mock DB calls
        mock_conn = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.execute.return_value.fetchone.return_value = {'total_actions': 10, 'successes': 8, 'avg_impact': 0.5, 'failures': 2, 'count': 0}
        mock_conn.execute.return_value.fetchall.return_value = []
        
        result = sr.perform_review()
        self.assertEqual(result['improvement_plan']['plan'], ["Sleep"])

    @patch('app.services.night_watchman.model_manager')
    @patch('app.services.night_watchman.NightWatchman._gather_intelligence')
    @patch('app.services.night_watchman.save_briefing')
    def test_night_watchman(self, mock_save, mock_gather, mock_mm):
        nw = NightWatchman()
        mock_gather.return_value = [{'title': 'News', 'summary': '...', 'link': '...', 'source': '...'}]
        text = "Briefing:\n```json\n{\"summary\": \"Good Morning\"}\n```"
        mock_mm.generate_content.return_value = MagicMock(text=text)
        
        # Avoid REM sleep recursion
        with patch.object(nw, 'perform_rem_sleep_cycle'):
            result = nw.perform_nightly_watch(force=True)
            self.assertTrue(result['success'])
            mock_save.assert_called()

    @patch('app.services.mindmap_service.model_manager')
    def test_mindmap(self, mock_mm):
        text = "Map:\n```json\n{\"name\": \"Root\"}\n```"
        mock_mm.generate_content.return_value = MagicMock(text=text)
        result = MindMapService.generate_mindmap("Topic")
        self.assertEqual(result['name'], "Root")

    @patch('app.services.mimir_service.model_manager')
    def test_mimir(self, mock_mm):
        m = MimirService()
        text = "Evaluation:\n```json\n{\"score\": 10}\n```"
        mock_mm.generate_content.return_value = MagicMock(text=text)
        result = m.evaluate_answer("Q", "A")
        self.assertEqual(result['score'], 10)

    @patch('app.services.issue_mapper.model_manager')
    @patch('app.services.issue_mapper.get_db')
    def test_issue_mapper(self, mock_db, mock_mm):
        text = "Mapping:\n```json\n[{\"subject\": \"k\"}]\n```"
        mock_mm.generate_content.return_value = MagicMock(text=text)
        
        # Mock DB
        mock_cursor = MagicMock()
        mock_db.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'title': 'T', 'upsc_summary': 'S'}
        
        result = map_article_to_syllabus(1)
        self.assertEqual(result[0]['subject'], "k")

if __name__ == '__main__':
    unittest.main()
