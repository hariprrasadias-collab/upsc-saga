import sqlite3
import os
import json
from thefuzz import process

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')
MATCH_THRESHOLD = 80 # Confidence score for a match

def generate_topic_mapping():
    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        # 1. Get all syllabus topics
        cursor.execute("SELECT id, topic, subject FROM syllabus_topics")
        syllabus_rows = cursor.fetchall()
        syllabus_topics = {f"{row['subject']}: {row['topic']}": row['id'] for row in syllabus_rows}
        syllabus_choices = list(syllabus_topics.keys())

        # 2. Get all unique, unmatched pyq_question topics
        cursor.execute("SELECT DISTINCT topic FROM pyq_questions WHERE topic_id IS NULL AND topic IS NOT NULL")
        pyq_topics = [row['topic'] for row in cursor.fetchall()]

        print(f"Found {len(pyq_topics)} unique PYQ topics to map against {len(syllabus_choices)} syllabus topics.")

        proposed_mapping = {}
        unmatched_topics = []

        # 3. Find the best match for each PYQ topic
        for pyq_topic in pyq_topics:
            # The process.extractOne method returns a tuple: (choice, score)
            best_match = process.extractOne(pyq_topic, syllabus_choices)

            if best_match and best_match[1] >= MATCH_THRESHOLD:
                matched_syllabus_topic = best_match[0]
                syllabus_topic_id = syllabus_topics[matched_syllabus_topic]
                proposed_mapping[pyq_topic] = syllabus_topic_id
            else:
                unmatched_topics.append({
                    "pyq_topic": pyq_topic,
                    "best_match": best_match[0] if best_match else "None",
                    "score": best_match[1] if best_match else 0
                })

        # 4. Save the results to files
        mapping_path = os.path.join(os.path.dirname(__file__), 'proposed_topic_mapping.json')
        with open(mapping_path, 'w') as f:
            json.dump(proposed_mapping, f, indent=2)
        print(f"Saved {len(proposed_mapping)} proposed mappings to {mapping_path}")

        unmatched_path = os.path.join(os.path.dirname(__file__), 'unmatched_pyq_topics_with_scores.json')
        with open(unmatched_path, 'w') as f:
            json.dump(unmatched_topics, f, indent=2)
        print(f"Saved {len(unmatched_topics)} unmatched topics to {unmatched_path}")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        conn.close()
        print("Topic mapping generation completed.")

if __name__ == '__main__':
    generate_topic_mapping()
