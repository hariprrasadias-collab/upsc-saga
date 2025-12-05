import sqlite3
import os
import json

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')
mapping_filepath = os.path.join(os.path.dirname(__file__), 'corrected_topic_mapping.json')

def apply_topic_mapping():
    if not os.path.exists(mapping_filepath):
        print(f"Error: Mapping file not found at {mapping_filepath}")
        print("Please create and review 'corrected_topic_mapping.json' before running this script.")
        return

    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        with open(mapping_filepath, 'r') as f:
            topic_mapping = json.load(f)

        print(f"Loaded {len(topic_mapping)} mappings from {mapping_filepath}")

        updated_count = 0
        for pyq_topic, syllabus_topic_id in topic_mapping.items():
            # This will update all questions that have this topic
            cursor.execute("""
                UPDATE pyq_questions
                SET topic_id = ?
                WHERE topic = ? AND topic_id IS NULL
            """, (syllabus_topic_id, pyq_topic))

            if cursor.rowcount > 0:
                updated_count += cursor.rowcount

        conn.commit()
        print(f"Successfully applied mappings, updating {updated_count} question rows.")

    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {mapping_filepath}. Please check the file for syntax errors.")
    except sqlite3.Error as e:
        print(f"An database error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    finally:
        conn.close()
        print("Script to apply topic mappings completed.")

if __name__ == '__main__':
    apply_topic_mapping()
