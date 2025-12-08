import sqlite3
from flask import g

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE = os.path.join(BASE_DIR, 'upsc_saga.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, timeout=30.0)
        # Performance Optimizations
        db.execute('PRAGMA journal_mode=WAL')   # Write-Ahead Logging for concurrency
        db.execute('PRAGMA synchronous=NORMAL') # Faster writes, safe enough for this app
        db.execute('PRAGMA cache_size=-64000')  # ~64MB memory cache
        db.execute('PRAGMA temp_store=MEMORY')  # Store temp tables in RAM
        db.row_factory = sqlite3.Row
    return db

def close_db(e=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)
