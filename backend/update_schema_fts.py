import sqlite3
from app import create_app
from app.db import get_db

def update_schema_fts():
    print("Starting FTS schema update...")
    app = create_app()
    with app.app_context():
        conn = get_db()

        # 1. Create FTS5 Virtual Table
        print("Creating pyq_questions_fts virtual table...")
        conn.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS pyq_questions_fts USING fts5(
                question_text,
                explanation,
                content='pyq_questions',
                content_rowid='id'
            )
        ''')

        # 2. Populate FTS Table
        print("Populating FTS table...")
        conn.execute('''
            INSERT INTO pyq_questions_fts(rowid, question_text, explanation)
            SELECT id, question_text, explanation FROM pyq_questions
        ''')

        # 3. Create Triggers for Sync
        print("Creating triggers...")

        # INSERT Trigger
        conn.execute('''
            CREATE TRIGGER IF NOT EXISTS pyq_ai AFTER INSERT ON pyq_questions BEGIN
              INSERT INTO pyq_questions_fts(rowid, question_text, explanation)
              VALUES (new.id, new.question_text, new.explanation);
            END;
        ''')

        # DELETE Trigger
        conn.execute('''
            CREATE TRIGGER IF NOT EXISTS pyq_ad AFTER DELETE ON pyq_questions BEGIN
              INSERT INTO pyq_questions_fts(pyq_questions_fts, rowid, question_text, explanation)
              VALUES('delete', old.id, old.question_text, old.explanation);
            END;
        ''')

        # UPDATE Trigger
        conn.execute('''
            CREATE TRIGGER IF NOT EXISTS pyq_au AFTER UPDATE ON pyq_questions BEGIN
              INSERT INTO pyq_questions_fts(pyq_questions_fts, rowid, question_text, explanation)
              VALUES('delete', old.id, old.question_text, old.explanation);
              INSERT INTO pyq_questions_fts(rowid, question_text, explanation)
              VALUES (new.id, new.question_text, new.explanation);
            END;
        ''')

        conn.commit()
        print("✅ FTS schema update completed successfully!")

if __name__ == "__main__":
    update_schema_fts()
