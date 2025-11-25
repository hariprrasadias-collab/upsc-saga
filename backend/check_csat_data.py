import sqlite3
import os

DB_PATH = 'd:/upsc-second-brain/backend/upsc_saga.db'

def check_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Checking 'Time & Work' questions...")
    cursor.execute("SELECT count(*) FROM csat_questions WHERE category='Quant' AND topic='Time & Work'")
    count = cursor.fetchone()[0]
    print(f"Count in DB: {count}")
    
    conn.close()

if __name__ == "__main__":
    check_data()
