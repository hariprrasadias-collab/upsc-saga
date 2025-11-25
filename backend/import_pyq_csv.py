import sqlite3
import csv
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')
csv_path = r'd:\upsc-second-brain\frontend\public\UPSC_Prelims_2024_2022_GS1_Complete.csv'

def import_csv():
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"Reading CSV from {csv_path}...")
    
    questions_to_insert = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Map CSV columns to DB columns
                # CSV: year,subject,topic,question_number,question_text,option_a,option_b,option_c,option_d,correct_option,explanation,difficulty
                
                # Clean up data if necessary
                year = int(row['year'])
                subject = row['subject']
                topic = row['topic']
                question_text = row['question_text']
                option_a = row['option_a']
                option_b = row['option_b']
                option_c = row['option_c']
                option_d = row['option_d']
                correct_option = row['correct_option'].strip().upper() # Ensure uppercase single letter
                explanation = row['explanation']
                difficulty = row['difficulty']
                
                questions_to_insert.append((
                    year, subject, topic, question_text, 
                    option_a, option_b, option_c, option_d, 
                    correct_option, explanation, difficulty
                ))
                
        if questions_to_insert:
            print(f"Found {len(questions_to_insert)} questions. Inserting...")
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
            print("No questions found in CSV.")
            
    except Exception as e:
        print(f"Error importing CSV: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    import_csv()
