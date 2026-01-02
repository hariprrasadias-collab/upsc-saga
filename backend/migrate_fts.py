import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def optimize_search():
    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Check if FTS table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pyq_questions_fts'")
    if cursor.fetchone():
        print("FTS table already exists. Rebuilding...")
        # Optional: Rebuild to ensure data sync
        cursor.execute("INSERT INTO pyq_questions_fts(pyq_questions_fts) VALUES('rebuild')")
    else:
        print("Creating FTS5 table 'pyq_questions_fts'...")
        # Create Virtual Table
        cursor.execute('''
            CREATE VIRTUAL TABLE pyq_questions_fts USING fts5(
                question_text,
                explanation,
                content='pyq_questions',
                content_rowid='id'
            )
        ''')

        # Initial Population
        print("Populating FTS table...")
        cursor.execute("INSERT INTO pyq_questions_fts(pyq_questions_fts) VALUES('rebuild')")

        # Create Triggers for Auto-Sync
        print("Creating triggers...")
        cursor.execute('''
            CREATE TRIGGER pyq_ai AFTER INSERT ON pyq_questions BEGIN
              INSERT INTO pyq_questions_fts(rowid, question_text, explanation) VALUES (new.id, new.question_text, new.explanation);
            END;
        ''')
        cursor.execute('''
            CREATE TRIGGER pyq_ad AFTER DELETE ON pyq_questions BEGIN
              INSERT INTO pyq_questions_fts(pyq_questions_fts, rowid, question_text, explanation) VALUES('delete', old.id, old.question_text, old.explanation);
            END;
        ''')
        cursor.execute('''
            CREATE TRIGGER pyq_au AFTER UPDATE ON pyq_questions BEGIN
              INSERT INTO pyq_questions_fts(pyq_questions_fts, rowid, question_text, explanation) VALUES('delete', old.id, old.question_text, old.explanation);
              INSERT INTO pyq_questions_fts(rowid, question_text, explanation) VALUES (new.id, new.question_text, new.explanation);
            END;
        ''')

    conn.commit()
    print("Optimization Complete: FTS5 Enabled.")

    # Verify
    res = cursor.execute("SELECT count(*) FROM pyq_questions_fts").fetchone()
    print(f"Indexed {res[0]} documents.")
    conn.close()

if __name__ == "__main__":
    optimize_search()
