import sqlite3
import os
import json

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def backfill_pyq_topic_id():
    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # Get all syllabus topics and create a lookup table
        cursor.execute("SELECT id, topic FROM syllabus_topics")
        syllabus_topics = {row['topic'].strip().lower(): row['id'] for row in cursor.fetchall()}

        # Get all pyq_questions that need backfilling
        cursor.execute("SELECT id, topic FROM pyq_questions WHERE topic_id IS NULL")
        pyq_questions = cursor.fetchall()

        print(f"Found {len(pyq_questions)} PYQ questions to backfill.")

        unmatched_topics = []
        matched_count = 0

        for question in pyq_questions:
            pyq_topic = question['topic'].strip().lower()

            if pyq_topic in syllabus_topics:
                topic_id = syllabus_topics[pyq_topic]
                cursor.execute("UPDATE pyq_questions SET topic_id = ? WHERE id = ?", (topic_id, question['id']))
                matched_count += 1
            else:
                unmatched_topics.append(question['topic'])

        conn.commit()
        print(f"Successfully matched and updated {matched_count} questions.")

        if unmatched_topics:
            print(f"Could not find matches for {len(unmatched_topics)} topics.")
            # Save unmatched topics to a file for review
            unmatched_path = os.path.join(os.path.dirname(__file__), 'unmatched_pyq_topics.json')
            with open(unmatched_path, 'w') as f:
                json.dump(list(set(unmatched_topics)), f, indent=2)
            print(f"Unmatched topics saved to {unmatched_path}")


    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        conn.close()
        print("Backfill script completed.")

if __name__ == '__main__':
    backfill_pyq_topic_id()
