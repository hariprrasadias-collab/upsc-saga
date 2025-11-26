import sqlite3

def create_table():
    try:
        conn = sqlite3.connect('upsc_saga.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mnemonics_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mnemonic_text TEXT NOT NULL,
                original_text TEXT NOT NULL,
                mnemonic_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        print("Created mnemonics_history table successfully.")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_table()
