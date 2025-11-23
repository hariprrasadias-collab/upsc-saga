from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    from . import db
    db.init_app(app)

    from .routes import dashboard, tasks, quests, battles, shop, codex, lore, mimir, seer, ravens, anki
    
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

    return app
