import sqlite3
import csv
import os
import hashlib
import json

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')
csv_path = r'd:\upsc-second-brain\frontend\public\UPSC_Prelims_2024_2022_GS1_Complete.csv'

def generate_question_hash(text, options):
    """Generate a unique hash for duplicate detection."""
    # Ensure options are in a consistent string format for hashing
    content = f"{text}{str(options)}".encode('utf-8')
    return hashlib.md5(content).hexdigest()

def import_csv():
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Load existing hashes
    print("Loading existing questions to check for duplicates...")
    existing_hashes = set()
    try:
        cursor.execute("SELECT question_text, option_a, option_b, option_c, option_d FROM pyq_questions")
        rows = cursor.fetchall()
        for row in rows:
            # Reconstruct options list/structure to match what we do during import
            # In import_questions.py options are stored as JSON list. 
            # Here in pyq_questions they are separate columns.
            # We'll use a tuple of options for consistency in hashing.
            options_tuple = (
                row['option_a'],
                row['option_b'],
                row['option_c'],
                row['option_d']
            )
            existing_hashes.add(generate_question_hash(row['question_text'], options_tuple))
        print(f"Loaded {len(existing_hashes)} existing question hashes.")
    except sqlite3.OperationalError:
        print("Warning: Could not fetch existing questions. Table might be empty or missing.")

    print(f"Reading CSV from {csv_path}...")
    
    questions_to_insert = []
    duplicate_count = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Map CSV columns to DB columns
                year = int(row['year'])
                subject = row['subject']
                topic = row['topic']
                question_text = row['question_text']
                option_a = row['option_a']
                option_b = row['option_b']
                option_c = row['option_c']
                option_d = row['option_d']
                correct_option = row['correct_option'].strip().upper()
                explanation = row['explanation']
                difficulty = row['difficulty']
                
                options_tuple = (option_a, option_b, option_c, option_d)
                q_hash = generate_question_hash(question_text, options_tuple)

                if q_hash in existing_hashes:
                    duplicate_count += 1
                    continue

                questions_to_insert.append((
                    year, subject, topic, question_text, 
                    option_a, option_b, option_c, option_d, 
                    correct_option, explanation, difficulty
                ))
                # Add to existing hashes so we don't add duplicates within the same CSV run
                existing_hashes.add(q_hash)
                
        if questions_to_insert:
            print(f"Found {len(questions_to_insert)} new questions. Inserting...")
            cursor.executemany('''
                INSERT INTO pyq_questions (
                    year, subject, topic, question_text, 
                    option_a, option_b, option_c, option_d, 
                    correct_option, explanation, difficulty
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', questions_to_insert)
            
            conn.commit()
            print(f"Successfully imported {len(questions_to_insert)} questions.")
        else:
            print("No new questions found to import.")
            
        print(f"Skipped {duplicate_count} duplicate questions.")
            
    except Exception as e:
        print(f"Error importing CSV: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    import_csv()
