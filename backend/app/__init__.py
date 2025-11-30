from app import cgi_fix
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.secret_key = 'dev_secret_key_upsc_saga'  # Required for session
    CORS(app, resources={r"/*": {"origins": "*"}})

    from . import db
    db.init_app(app)

    # Initialize DB tables
    from app.db_models.study_plan import init_study_plan_tables
    with app.app_context():
        init_study_plan_tables()

    # Import blueprints
    from .routes import (
        dashboard, tasks, quests, battles, shop, codex, lore, mimir, 
        seer, ravens, anki, warmap, answer_writing, mock_tests, pyq, 
        syllabus, flashcards, analytics, essay, csat, badges, challenges, 
        shop_new, weak_areas, admin, predictive, pomodoro, timebox, planner, 
        templates, revision, heatmap, model_answers, issue_mapping, scheduler,
        mindmap, study_plan
    )
    
    # Register blueprints
    app.register_blueprint(dashboard.bp)
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
    app.register_blueprint(mock_tests.mock_tests)
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

    return app
