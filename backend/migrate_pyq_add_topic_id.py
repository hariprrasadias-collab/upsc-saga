import sqlite3
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def migrate_add_topic_id_to_pyq():
    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(pyq_questions)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'topic_id' not in columns:
            print("Adding 'topic_id' column to 'pyq_questions' table...")
            # Add the topic_id column, allowing NULL for now
            cursor.execute('''
                ALTER TABLE pyq_questions
                ADD COLUMN topic_id INTEGER REFERENCES syllabus_topics(id)
            ''')
            print("Column 'topic_id' added successfully.")
        else:
            print("Column 'topic_id' already exists.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        conn.commit()
        conn.close()
        print("Migration for adding topic_id completed.")

if __name__ == '__main__':
    migrate_add_topic_id_to_pyq()
