
import sqlite3
import os
from datetime import datetime

db_path = os.path.join('backend', 'upsc_saga.db')
print(f"Connecting to {db_path}")

try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables: {tables}")

    if 'flashcards' in tables:
        cursor.execute("SELECT COUNT(*) FROM flashcards")
        count = cursor.fetchone()[0]
        print(f"Total Flashcards: {count}")
        
        cursor.execute("SELECT * FROM flashcards LIMIT 5")
        rows = cursor.fetchall()
        print("Sample Flashcards:")
        for row in rows:
            print(dict(row))

    if 'review_sessions' in tables:
        cursor.execute("SELECT COUNT(*) FROM review_sessions")
        count = cursor.fetchone()[0]
        print(f"Total Reviews: {count}")
        
        cursor.execute("SELECT * FROM review_sessions ORDER BY reviewed_at DESC LIMIT 5")
        rows = cursor.fetchall()
        print("Recent Reviews:")
        for row in rows:
            print(dict(row))

    # Check analytics logic
    print("\n--- Analytics Logic Check ---")
    
    all_cards = conn.execute('''
        SELECT f.id, rs.halflife, rs.alpha, rs.beta
        FROM flashcards f
        LEFT JOIN (
            SELECT flashcard_id, halflife, alpha, beta
            FROM review_sessions
            WHERE (flashcard_id, reviewed_at) IN (
                SELECT flashcard_id, MAX(reviewed_at)
                FROM review_sessions
                GROUP BY flashcard_id
            )
        ) rs ON f.id = rs.flashcard_id
    ''').fetchall()
    
    print(f"Total cards fetched for analytics: {len(all_cards)}")
    
    maturity_counts = {'new': 0, 'learning': 0, 'young': 0, 'mature': 0, 'mastered': 0}
    for card in all_cards:
        if card['halflife'] is None:
            maturity_counts['new'] += 1
        else:
            hl = card['halflife']
            if hl < 1: maturity = 'new'
            elif hl < 7: maturity = 'learning'
            elif hl < 30: maturity = 'young'
            elif hl < 180: maturity = 'mature'
            else: maturity = 'mastered'
            maturity_counts[maturity] += 1
            
    print(f"Maturity Counts: {maturity_counts}")

except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
