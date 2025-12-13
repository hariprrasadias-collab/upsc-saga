import os
import sys
import importlib

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def check_imports():
    print("🔎 Checking service imports for Circular Dependencies or Syntax Errors...")

    services = [
        'app.services.model_manager',
        'app.services.brain_service',
        'app.services.socratic_service',
        'app.services.essay_evaluator',
        'app.services.answer_evaluator',
        'app.services.foresight_engine',
        'app.services.hephaestus_service',
        'app.services.night_watchman',
        'app.services.study_planner',
        'app.services.game_engine',
        'app.services.analytics_service',
        'app.services.content_recommender',
        'app.services.goal_service',
        'app.services.challenge_service',
        'app.services.pomodoro_service',
        'app.services.compilation_service',
        'app.services.interview_service',
        'app.services.visualizations',
        'app.services.weak_area_service',
        'app.services.autonomy_manager',
        'app.services.outcome_tracker',
        'app.services.panopticon_service',
        'app.services.shop_service',
        'app.services.badge_service',
        'app.services.auto_corrector',
        'app.services.self_review',
        'app.services.upsc_summarizer'
    ]

    # We need a valid flask app context for some of these imports if they access `current_app` or `db` at module level
    # (Though most are designed to be lazy)

    errors = []

    for service in services:
        try:
            importlib.import_module(service)
            print(f"✅ Imported: {service}")
        except Exception as e:
            print(f"❌ FAILED: {service} -> {e}")
            errors.append((service, str(e)))

    if errors:
        print(f"\n🚨 FOUND {len(errors)} IMPORT ERRORS!")
        sys.exit(1)
    else:
        print("\n✨ All services imported successfully. System Integrity: 100%")

if __name__ == "__main__":
    check_imports()
