import sqlite3
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def backdate_revision():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
    
    print(f"Updating next_review to {yesterday} for item 999...")
    c.execute('''
        UPDATE revision_schedules 
        SET next_review = ?
        WHERE item_id = 999
    ''', (yesterday,))
    
    conn.commit()
    conn.close()
    print("Update completed.")

if __name__ == '__main__':
    backdate_revision()
