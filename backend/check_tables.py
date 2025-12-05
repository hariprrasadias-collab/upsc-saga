import sqlite3

def check_tables():
    try:
        conn = sqlite3.connect('upsc_saga.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print("Tables found:", tables)

        required_tables = ['mnemonics_history', 'boss_battles', 'syllabus_topics', 'mock_tests', 'test_attempts', 'answer_writing_prompts', 'user_answers', 'answer_evaluations']
        missing = [t for t in required_tables if t not in tables]

        if missing:
            print("Missing tables:", missing)
        else:
            print("All required tables present.")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_tables()
