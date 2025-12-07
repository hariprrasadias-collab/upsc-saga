import sqlite3
import json
from app.db import get_db

def init_automation_tables():
    conn = get_db()
    
    # 1. Socratic Conversations
    conn.execute('''
        CREATE TABLE IF NOT EXISTS socratic_conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            topic TEXT,
            dialogue TEXT, -- The full script
            insight TEXT, -- Key takeaway or verdict JSON
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Triangulation Reports
    # Note: 'way_forward' column now stores the FULL JSON report for newer entries,
    # not just the way_forward section.
    conn.execute('''
        CREATE TABLE IF NOT EXISTS triangulation_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            synthesis TEXT,
            way_forward TEXT, -- JSON (Full Report)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Neural Hashes
    conn.execute('''
        CREATE TABLE IF NOT EXISTS neural_hashes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            core_themes TEXT, -- JSON
            examiner_pattern TEXT,
            cross_linkages TEXT, -- JSON
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 4. Foresight Predictions (if not exists)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS foresight_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            type TEXT,
            subject TEXT,
            topic TEXT,
            probability REAL,
            reasoning TEXT,
            is_favorite BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 5. Generic AI Outputs (for things like Podcasts, Essays, etc.)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS ai_generated_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT, -- 'podcast', 'essay', 'visual_prompt', 'roleplay', 'cheat_sheet', 'timeline', 'eli5', 'pitfalls', 'quote_bank', 'map_work'
            topic TEXT,
            content TEXT,
            metadata TEXT, -- JSON for extra fields
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    print("✅ Automation tables initialized.")

def save_socratic_dialogue(user_id, topic, dialogue, insight=""):
    conn = get_db()
    conn.execute('INSERT INTO socratic_conversations (user_id, topic, dialogue, insight) VALUES (?, ?, ?, ?)', 
                 (user_id, topic, dialogue, insight))
    conn.commit()

def save_triangulation(topic, synthesis, full_report_data):
    """
    Saves the triangulation report.
    'full_report_data' is the entire JSON dictionary from the AI.
    """
    conn = get_db()
    conn.execute('INSERT INTO triangulation_reports (topic, synthesis, way_forward) VALUES (?, ?, ?)', 
                 (topic, synthesis, json.dumps(full_report_data)))
    conn.commit()

def save_neural_hash(topic, data):
    conn = get_db()
    conn.execute('INSERT INTO neural_hashes (topic, core_themes, examiner_pattern, cross_linkages) VALUES (?, ?, ?, ?)', 
                 (topic, json.dumps(data.get('core_themes', [])), data.get('examiner_pattern', ''), json.dumps(data.get('cross_linkages', []))))
    conn.commit()

def save_foresight_prediction(pred):
    conn = get_db()
    conn.execute('''
        INSERT INTO foresight_predictions (question, type, subject, topic, probability, reasoning)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (pred['question'], pred['type'], pred.get('subject'), pred.get('topic'), pred.get('probability'), pred.get('reasoning')))
    conn.commit()

def save_ai_content(content_type, topic, content, metadata={}):
    conn = get_db()
    conn.execute('INSERT INTO ai_generated_content (content_type, topic, content, metadata) VALUES (?, ?, ?, ?)', 
                 (content_type, topic, content, json.dumps(metadata)))
    conn.commit()
