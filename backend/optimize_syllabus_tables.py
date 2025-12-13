import sqlite3
import os

DB_PATH = 'backend/upsc_saga.db'

def apply_indexes():
    """Applies indexes to syllabus_topics and topic_revisions tables."""
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("Applying indexes for Syllabus performance...")

        # 1. Index for syllabus_topics sorting
        # Query uses: ORDER BY t.paper, t.subject, t.id
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_syllabus_paper_subject ON syllabus_topics(paper, subject);")
        print("Created index: idx_syllabus_paper_subject")

        # 2. Index for topic_revisions join
        # Query uses: LEFT JOIN topic_revisions r ON t.id = r.topic_id
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_revisions_topic_id ON topic_revisions(topic_id);")
        print("Created index: idx_revisions_topic_id")

        conn.commit()
        print("Optimization complete.")

    except sqlite3.Error as e:
        print(f"Error applying indexes: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    apply_indexes()
