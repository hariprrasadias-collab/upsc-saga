import sys
import os
import json
import time

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app
from app.services.neural_hash_service import NeuralHashService
from app.services.flashcard_service import FlashcardService
from app.services.mimir_service import mimir_service
from app.services.answer_evaluator import evaluator as answer_evaluator
from app.services.essay_evaluator import EssayEvaluator
from app.services.hephaestus_service import hephaestus
from app.services.mock_test_service import MockTestService
from app.services.issue_mapper import map_article_to_syllabus
from app.services.mindmap_service import MindMapService
from app.services.model_manager import model_manager
from app.services.night_watchman import night_watchman
from app.services.self_review import self_review_service
from app.services.foresight_engine import foresight_engine
from app.services.socratic_service import generate_autonomous_debate

def test_service(name, func, *args, **kwargs):
    print(f"\n🧪 Testing {name}...", end=" ", flush=True)
    try:
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        print(f"✅ PASSED ({duration:.2f}s)")
        print(f"   Output Preview: {str(result)[:100]}...")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    app = create_app()
    with app.app_context():
        print("🚀 Starting Quota Compliance Verification...")
        print(f"   Current Model Manager Config: Fast={model_manager.FAST_MODELS}, Pro={model_manager.PRO_MODELS}")
        
        success_count = 0
        total_tests = 0

        # 1. Neural Hash
        total_tests += 1
        nh = NeuralHashService()
        if test_service("NeuralHashService.decode_text", nh.decode_text, "Democracy in India", "political"):
            success_count += 1
            
        # 2. Flashcards
        total_tests += 1
        if test_service("FlashcardService.generate_from_topic", FlashcardService.generate_from_topic, "Preamble", 2):
            success_count += 1

        # 3. Mimir Chat (Evaluate Answer)
        total_tests += 1
        # Mock Mimir eval
        if test_service("MimirService.evaluate_answer", mimir_service.evaluate_answer, "What is GDP?", "Gross Domestic Product."):
            success_count += 1

        # 4. Answer Evaluator
        total_tests += 1
        if test_service("AnswerEvaluator.evaluate_answer", answer_evaluator.evaluate_answer, "Explain Secularism.", "Separation of religion and state.", 100):
            success_count += 1
            
        # 5. Essay Evaluator
        total_tests += 1
        ee = EssayEvaluator()
        if test_service("EssayEvaluator.evaluate_essay", ee.evaluate_essay, "Climate Change", "It is getting hot."):
            success_count += 1
            
        # 6. Mock Test
        total_tests += 1
        if test_service("MockTestService.generate_from_topic", MockTestService.generate_from_topic, "Mughal Empire", 3):
            success_count += 1
            
        # 7. Mind Map
        total_tests += 1
        if test_service("MindMapService.generate_mindmap", MindMapService.generate_mindmap, "Solar System"):
            success_count += 1

        # 8. Night Watchman (Synthesize Briefing - Mock Data)
        total_tests += 1
        mock_articles = [{'title': 'Test News', 'source': 'The Hindu', 'summary': 'India launches new satellite.'}]
        # Access protected method for testing
        if test_service("NightWatchman._synthesize_briefing", night_watchman._synthesize_briefing, mock_articles):
            success_count += 1
            
        # 9. Self Review (Perform Review)
        total_tests += 1
        if test_service("SelfReviewService.perform_review", self_review_service.perform_review, 7):
            success_count += 1
            
        # 10. Foresight Engine (Mock Analysis)
        total_tests += 1
        # Mocking methods to avoid DB hits
        if test_service("ForesightEngine._critic_review", foresight_engine._critic_review, [{'question': 'Test Q', 'type': 'MCQ'}]):
            success_count += 1

        # 11. Socratic Debate (Autonomous)
        total_tests += 1
        if test_service("SocraticService.generate_autonomous_debate", generate_autonomous_debate, "Ethics", 2):
            success_count += 1
            
        # Hephaestus and IssueMapper require more complex setup (DB/Files), skipping for quick check
        
        print(f"\n🏁 Verification Complete: {success_count}/{total_tests} Services Passed.")
        
if __name__ == "__main__":
    main()
