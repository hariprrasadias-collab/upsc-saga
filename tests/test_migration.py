import sqlite3
import os
import unittest

# Define the migration logic directly here or import it if modular enough.
# Since the original script has hardcoded DB_PATH, I'll adapt the logic for the test.

def apply_indexes_to_conn(conn):
    cursor = conn.cursor()
    try:
        # 1. Index for syllabus_topics sorting
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_syllabus_paper_subject ON syllabus_topics(paper, subject);")

        # 2. Index for topic_revisions join
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_revisions_topic_id ON topic_revisions(topic_id);")

        conn.commit()
        return True, "Success"
    except Exception as e:
        return False, str(e)

class TestDatabaseMigration(unittest.TestCase):
    def setUp(self):
        # Create an in-memory database
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()

        # Setup Schema
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS syllabus_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper TEXT,
                subject TEXT,
                topic TEXT,
                subtopic TEXT,
                status TEXT DEFAULT 'Not Started',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS topic_revisions (
                topic_id INTEGER,
                last_revised_at TIMESTAMP,
                revision_count INTEGER DEFAULT 0,
                next_revision_date DATE,
                status TEXT DEFAULT 'pending'
            )
        ''')
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_indexes_are_created(self):
        # Verify indexes don't exist yet
        self.cursor.execute("PRAGMA index_list(syllabus_topics)")
        indexes = self.cursor.fetchall()
        self.assertEqual(len(indexes), 0, "Should have no indexes initially")

        self.cursor.execute("PRAGMA index_list(topic_revisions)")
        indexes = self.cursor.fetchall()
        self.assertEqual(len(indexes), 0, "Should have no indexes initially")

        # Run Migration
        success, msg = apply_indexes_to_conn(self.conn)
        self.assertTrue(success, f"Migration failed: {msg}")

        # Verify Indexes exist
        self.cursor.execute("PRAGMA index_list(syllabus_topics)")
        indexes = self.cursor.fetchall()
        # Look for idx_syllabus_paper_subject
        index_names = [i[1] for i in indexes]
        self.assertIn('idx_syllabus_paper_subject', index_names)

        self.cursor.execute("PRAGMA index_list(topic_revisions)")
        indexes = self.cursor.fetchall()
        # Look for idx_revisions_topic_id
        index_names = [i[1] for i in indexes]
        self.assertIn('idx_revisions_topic_id', index_names)

        # Verify columns in index
        # idx_syllabus_paper_subject should have paper (rank 0) and subject (rank 1)
        self.cursor.execute("PRAGMA index_info(idx_syllabus_paper_subject)")
        info = self.cursor.fetchall()
        # info structure: (seqno, cid, name)
        columns = [col[2] for col in info]
        self.assertEqual(columns, ['paper', 'subject'])

        # idx_revisions_topic_id should have topic_id
        self.cursor.execute("PRAGMA index_info(idx_revisions_topic_id)")
        info = self.cursor.fetchall()
        columns = [col[2] for col in info]
        self.assertEqual(columns, ['topic_id'])

if __name__ == '__main__':
    unittest.main()
