from . import cgi_fix
from flask import Flask
from flask_cors import CORS
from flask_compress import Compress
from flask_caching import Cache
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import os
import threading
import time

# Load environment variables explicitly
load_dotenv()

cache = Cache()

def create_app():
    app = Flask(__name__)
    # Secure: Load SECRET_KEY from environment, fallback only for dev
    app.secret_key = os.getenv('SECRET_KEY', 'dev_secret_key_upsc_saga')
    CORS(app, resources={r"/*": {"origins": "*"}})
    Compress(app) # Enable Gzip compression

    # --- LOGGING & AUTONOMOUS REPAIR SETUP ---
    if not os.path.exists('logs'):
        os.makedirs('logs', exist_ok=True)

    file_handler = RotatingFileHandler('logs/app.log', maxBytes=1024*1024, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.ERROR)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO) # Ensure we capture info too if needed

    # Global Error Handler for Hephaestus
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Pass through HTTP exceptions (404, 403, etc.)
        if hasattr(e, 'code'):
            return e

        # Log the full traceback to file
        app.logger.error(f"CRITICAL EXCEPTION: {e}", exc_info=True)

        # Trigger Autonomous Repair (Background)
        try:
            from app.services.hephaestus_service import hephaestus
            hephaestus.start_background_repair(e)
            print(f"🔥 Hephaestus dispatched for error: {e}")
        except Exception as h_err:
            print(f"❌ Hephaestus Dispatch Failed: {h_err}")

        # Return generic error
        return {"success": False, "error": "Internal Server Error. The System is attempting self-repair."}, 500

    # Startup Log Scan (Background)
    def run_startup_scan():
        time.sleep(3) # Wait for app to fully initialize
        try:
            from app.services.hephaestus_service import hephaestus
            hephaestus.scan_logs_and_repair('logs/app.log')
        except Exception as e:
            print(f"❌ Startup Log Scan Failed: {e}")

    threading.Thread(target=run_startup_scan, daemon=True).start()

    # Configure Caching (Simple Local Memory Cache for speed)
    app.config['CACHE_TYPE'] = 'NullCache' # Changed from SimpleCache to fix AttributeError
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300 # 5 minutes default
    cache.init_app(app)

    # Static Asset Caching (Cache-Control Headers)
    @app.after_request
    def add_header(response):
        if 'Cache-Control' not in response.headers:
            # Cache static assets for 1 year (31536000 seconds)
            if response.mimetype.startswith('image/') or \
               response.mimetype.startswith('text/css') or \
               response.mimetype.startswith('application/javascript'):
                response.headers['Cache-Control'] = 'public, max-age=31536000'
        return response

    from . import db
    db.init_app(app)
    app.config['DATABASE'] = db.DATABASE

    # Initialize DB tables
    from app.db_models.study_plan import init_study_plan_tables
    from app.db_models.autonomous_brain import init_autonomous_brain_tables
    from app.db_models.gamification import init_gamification_tables
    from app.db_models.core import init_core_tables
    from app.db_models.tasks import init_tasks_table
    from app.db_models.indexes import init_indexes
    
    # Extra modules
    from app.db_models.flashcards import init_flashcard_tables
    from app.db_models.answer_writing import init_answer_writing_tables
    from app.db_models.revision import init_revision_tables
    from app.db_models.syllabus import init_syllabus_tables

    with app.app_context():
        init_core_tables() # Core first (users)
        init_tasks_table() # Ensure tasks table exists
        init_study_plan_tables()
        init_autonomous_brain_tables()
        init_gamification_tables()
        
        # Initialize Automation Tables (Socratic, Triangulation, etc.)
        from app.db_models.automation_storage import init_automation_tables
        init_automation_tables()
        
        init_indexes() # Ensure performance indexes

    # Import blueprints
    from .routes import (
        dashboard, tasks, quests, battles, shop, codex, lore, mimir, 
        seer, ravens, anki, warmap, answer_writing, mock_tests, pyq, 
        syllabus, flashcards, analytics, essay, csat, badges, challenges, 
        shop_new, weak_areas, admin, predictive, pomodoro, timebox, planner, 
        templates, revision, heatmap, model_answers, issue_mapping, scheduler,
        mindmap, study_plan, golden_path, watchman
    )
    
    # Register blueprints
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(golden_path.golden_path_bp, url_prefix='/api/golden-path')
    app.register_blueprint(tasks.bp)
    app.register_blueprint(quests.bp)
    app.register_blueprint(battles.bp)
    app.register_blueprint(shop.bp)
    app.register_blueprint(codex.bp)
    app.register_blueprint(lore.bp)
    app.register_blueprint(mimir.mimir_bp)
    app.register_blueprint(seer.bp)
    app.register_blueprint(ravens.bp)
    app.register_blueprint(anki.bp)
    app.register_blueprint(warmap.warmap)
    app.register_blueprint(answer_writing.answer_writing)
    
    # Night Watchman Registration (Explicit)
    print("🦉 Registering Night Watchman Blueprint...")
    app.register_blueprint(watchman.watchman_bp, url_prefix='/night-watchman')
    
    app.register_blueprint(mock_tests.mock_tests_bp)
    app.register_blueprint(pyq.bp)
    app.register_blueprint(syllabus.bp)
    app.register_blueprint(flashcards.flashcards)
    app.register_blueprint(analytics.analytics)
    app.register_blueprint(essay.essay_bp)
    app.register_blueprint(csat.csat_bp)
    app.register_blueprint(badges.badges_bp)
    app.register_blueprint(challenges.challenges_bp)
    app.register_blueprint(shop_new.shop_bp_new)
    app.register_blueprint(weak_areas.bp)
    app.register_blueprint(admin.admin_bp)
    app.register_blueprint(predictive.predictive_bp)
    app.register_blueprint(pomodoro.pomodoro_bp)
    app.register_blueprint(timebox.timebox_bp)
    app.register_blueprint(planner.bp)
    app.register_blueprint(scheduler.bp)
    app.register_blueprint(templates.bp)
    app.register_blueprint(revision.bp)
    app.register_blueprint(heatmap.bp)
    app.register_blueprint(model_answers.bp)
    app.register_blueprint(issue_mapping.bp)
    app.register_blueprint(mindmap.bp)
    app.register_blueprint(study_plan.study_plan_bp)
    
    from app.routes import compilation
    app.register_blueprint(compilation.bp)

    from app.routes.scribe import scribe_bp
    app.register_blueprint(scribe_bp, url_prefix='/api/scribe')

    from app.routes.arena import arena_bp
    app.register_blueprint(arena_bp, url_prefix='/api/arena')

    from app.routes.socratic_routes import socratic_bp
    app.register_blueprint(socratic_bp, url_prefix='/api/socratic')

    from app.routes.triangulation_routes import triangulation_bp
    app.register_blueprint(triangulation_bp, url_prefix='/api/triangulation')

    from app.routes.brain_routes import brain_bp
    app.register_blueprint(brain_bp, url_prefix='/api/brain')

    from app.routes.autonomy_routes import autonomy_bp
    app.register_blueprint(autonomy_bp, url_prefix='/api/autonomy')

    from app.routes.automation_routes import automation_bp
    app.register_blueprint(automation_bp, url_prefix='/api/automation')

    from app.routes.mind_palace import mind_palace_bp
    app.register_blueprint(mind_palace_bp, url_prefix='/api/mind_palace')

    from app.routes.foresight import foresight_bp
    app.register_blueprint(foresight_bp, url_prefix='/api/foresight')

    # Removed duplicate watchman registration from here

    from app.routes.panopticon import panopticon_bp
    app.register_blueprint(panopticon_bp)

    from app.routes.neural_hash import neural_hash_bp
    app.register_blueprint(neural_hash_bp, url_prefix='/api/neural_hash')

    from app.routes.interview import interview_bp
    app.register_blueprint(interview_bp, url_prefix='/api/interview')

    # Initialize Tables
    from app.db_models.mind_palace import init_mind_palace_tables
    from app.db_models.night_watchman import init_watchman_tables
    from app.db_models.panopticon import init_panopticon_tables
    from app.db_models.foresight import init_foresight_tables
    from app.db_models.neural_hash import init_neural_hash_tables
    from app.db import DATABASE
    
    with app.app_context():
        init_mind_palace_tables()
        init_watchman_tables()
        init_panopticon_tables(DATABASE)
        init_foresight_tables()
        init_neural_hash_tables()

    return app
