import pandas as pd
import sqlite3
import json
import hashlib
import sys
import os

DB_PATH = 'upsc_saga.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def generate_question_hash(text, options):
    """Generate a unique hash for duplicate detection."""
    content = f"{text}{str(options)}".encode('utf-8')
    return hashlib.md5(content).hexdigest()

def validate_row(row, index):
    """Validate a single row of data."""
    # Adjusted for the specific CSV format which has 'year' instead of 'source'
    required_fields = ['year', 'subject', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']
    missing = [field for field in required_fields if pd.isna(row.get(field))]
    
    if missing:
        return False, f"Row {index}: Missing fields: {', '.join(missing)}"
    
    if str(row['correct_option']).strip().upper() not in ['A', 'B', 'C', 'D']:
        return False, f"Row {index}: Invalid correct_option '{row['correct_option']}'. Must be A, B, C, or D."
        
    return True, ""

def import_questions(csv_file_path):
    if not os.path.exists(csv_file_path):
        print(f"Error: File '{csv_file_path}' not found.")
        return

    print(f"Reading {csv_file_path}...")
    try:
        # Use latin-1 or cp1252 if utf-8 fails, common with Excel CSVs
        try:
            df = pd.read_csv(csv_file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(csv_file_path, encoding='cp1252')
            
        # Normalize column names
        df.columns = [c.lower().strip() for c in df.columns]
        
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    success_count = 0
    error_count = 0
    duplicate_count = 0
    
    print("Starting import...")
    
    # Get existing hashes to check for duplicates
    existing_hashes = set()
    try:
        cursor.execute("SELECT question_text, options FROM questions_master")
        rows = cursor.fetchall()
        for row in rows:
            existing_hashes.add(generate_question_hash(row['question_text'], row['options']))
    except sqlite3.OperationalError:
        print("Warning: Could not fetch existing questions. Table might be empty.")

    for index, row in df.iterrows():
        is_valid, error_msg = validate_row(row, index + 2) # +2 for header and 0-index
        if not is_valid:
            print(f"Skipping: {error_msg}")
            error_count += 1
            continue

        # Format options as JSON
        options = [
            str(row['option_a']).strip(),
            str(row['option_b']).strip(),
            str(row['option_c']).strip(),
            str(row['option_d']).strip()
        ]
        options_json = json.dumps(options)
        
        # Check duplicate
        q_hash = generate_question_hash(row['question_text'], options_json)
        if q_hash in existing_hashes:
            duplicate_count += 1
            continue

        try:
            # Construct source from year
            source = f"PYQ-{int(row['year'])}"
            
            cursor.execute('''
                INSERT INTO questions_master (source, subject, topic, difficulty, question_text, options, correct_option, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                source,
                row['subject'],
                row.get('topic', 'General'),
                row.get('difficulty', 'Medium'),
                row['question_text'],
                options_json,
                str(row['correct_option']).strip().upper(),
                row.get('explanation', '')
            ))
            existing_hashes.add(q_hash)
            success_count += 1
        except Exception as e:
            print(f"Error inserting row {index + 2}: {e}")
            error_count += 1

    conn.commit()
    conn.close()

    print("\n=== Import Summary ===")
    print(f"Total Rows Processed: {len(df)}")
    print(f"Successfully Imported: {success_count}")
    print(f"Duplicates Skipped: {duplicate_count}")
    print(f"Errors/Invalid: {error_count}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_questions.py <path_to_csv>")
    else:
        import_questions(sys.argv[1])
