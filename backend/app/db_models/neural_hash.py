from app.db import get_db
import json
from datetime import datetime

def init_neural_hash_tables():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS neural_hash_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_text TEXT,
            context_type TEXT,
            decoded_data TEXT, -- JSON string
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

def save_neural_hash_log(input_text, context_type, decoded_data):
    conn = get_db()
    cursor = conn.execute('''
        INSERT INTO neural_hash_logs (input_text, context_type, decoded_data)
        VALUES (?, ?, ?)
    ''', (input_text, context_type, json.dumps(decoded_data)))
    conn.commit()
    return cursor.lastrowid

def get_neural_hash_history(limit=20):
    conn = get_db()
    cursor = conn.execute('''
        SELECT id, input_text, context_type, decoded_data, created_at
        FROM neural_hash_logs
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    
    history = []
    for row in cursor.fetchall():
        try:
            data = json.loads(row['decoded_data'])
        except:
            data = {}
            
        history.append({
            'id': row['id'],
            'input_text_preview': row['input_text'][:100] + '...',
            'context_type': row['context_type'],
            'decoded_data': data,
            'created_at': row['created_at']
        })
    return history
