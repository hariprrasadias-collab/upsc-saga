from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.secret_key = 'dev_secret_key_upsc_saga' # Required for session
    CORS(app, resources={r"/*": {"origins": "*"}})

    from . import db
    db.init_app(app)

    from .routes import dashboard, tasks, quests, battles, shop, codex, lore, mimir, seer, ravens, anki, warmap, answer_writing, mock_tests, pyq, syllabus, flashcards, analytics
    
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(tasks.bp)
    app.register_blueprint(quests.bp)
    app.register_blueprint(battles.bp)
    app.register_blueprint(shop.bp)
    app.register_blueprint(codex.bp)
    app.register_blueprint(lore.bp)
    app.register_blueprint(mimir.bp)
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

    return app
