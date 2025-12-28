
import sqlite3
import os

DB_PATH = os.path.join('backend', 'upsc_saga.db')

def optimize_search():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("Creating FTS5 virtual table...")
        # Create FTS table
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS pyq_questions_fts
            USING fts5(question_text, explanation)
        ''')

        print("Populating FTS table...")
        # Populate with existing data
        # We assume pyq_questions.id maps to fts rowid
        cursor.execute('''
            INSERT INTO pyq_questions_fts (rowid, question_text, explanation)
            SELECT id, question_text, explanation FROM pyq_questions
        ''')

        print("Creating triggers...")
        # Create Triggers to keep them in sync
        triggers = [
            '''
            CREATE TRIGGER IF NOT EXISTS pyq_fts_insert AFTER INSERT ON pyq_questions
            BEGIN
                INSERT INTO pyq_questions_fts(rowid, question_text, explanation)
                VALUES (new.id, new.question_text, new.explanation);
            END;
            ''',
            '''
            CREATE TRIGGER IF NOT EXISTS pyq_fts_delete AFTER DELETE ON pyq_questions
            BEGIN
                DELETE FROM pyq_questions_fts WHERE rowid = old.id;
            END;
            ''',
            '''
            CREATE TRIGGER IF NOT EXISTS pyq_fts_update AFTER UPDATE ON pyq_questions
            BEGIN
                UPDATE pyq_questions_fts
                SET question_text = new.question_text, explanation = new.explanation
                WHERE rowid = old.id;
            END;
            '''
        ]

        for t in triggers:
            cursor.execute(t)

        conn.commit()
        print("Optimization complete: FTS5 table and triggers created.")

    except Exception as e:
        print(f"Error during optimization: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    optimize_search()
