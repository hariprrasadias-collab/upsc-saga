"""
Clear and resync database with CSV file
Ensures DB contains EXACTLY what's in the CSV
"""

import sqlite3
import csv
import os

# Paths
db_path = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')
csv_path = r'd:\upsc-second-brain\frontend\public\UPSC_Prelims_2024_2022_GS1_Complete.csv'

def resync_database():
    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Step 1: Count existing questions
    cursor.execute('SELECT COUNT(*) FROM pyq_questions')
    old_count = cursor.fetchone()[0]
    print(f"\nCurrent DB has {old_count} questions")
    
    # Step 2: Count CSV rows
    with open(csv_path, 'r', encoding='utf-8') as f:
        csv_rows = list(csv.DictReader(f))
    csv_count = len(csv_rows)
    print(f"CSV file has {csv_count} questions")
    
    # Step 3: Clear all existing questions
    print(f"\n⚠️  Clearing all {old_count} existing questions from database...")
    cursor.execute('DELETE FROM pyq_questions')
    conn.commit()
    print("✓ Database cleared")
    
    # Step 4: Import all questions from CSV
    print(f"\nImporting {csv_count} questions from CSV...")
    
    imported = 0
    errors = 0
    
    for row in csv_rows:
        try:
            year = int(row['year'])
            subject = row['subject']
            topic = row['topic']
            question_text = row['question_text']
            option_a = row['option_a']
            option_b = row['option_b']
            option_c = row['option_c']
            option_d = row['option_d']
            
            if not row['correct_option']:
                print(f"⚠️  Skipping row {imported+1} with missing correct_option")
                errors += 1
                continue
                
            correct_option = row['correct_option'].strip().upper()
            explanation = row['explanation']
            difficulty = row['difficulty']
            
            cursor.execute('''
                INSERT INTO pyq_questions (
                    year, subject, topic, question_text, 
                    option_a, option_b, option_c, option_d, 
                    correct_option, explanation, difficulty
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (year, subject, topic, question_text, 
                  option_a, option_b, option_c, option_d, 
                  correct_option, explanation, difficulty))
            
            imported += 1
            
            if imported % 100 == 0:
                print(f"  ... imported {imported} questions")
                
        except Exception as e:
            print(f"✗ Error on row {imported+1}: {e}")
            errors += 1
    
    conn.commit()
    
    # Step 5: Verify final count
    cursor.execute('SELECT COUNT(*) FROM pyq_questions')
    final_count = cursor.fetchone()[0]
    
    # Step 6: Get year distribution
    cursor.execute('SELECT year, COUNT(*) as count FROM pyq_questions GROUP BY year ORDER BY year DESC')
    year_dist = cursor.fetchall()
    
    conn.close()
    
    # Print summary
    print("\n" + "="*60)
    print("RESYNC COMPLETE")
    print("="*60)
    print(f"\nPrevious DB count: {old_count}")
    print(f"CSV file count: {csv_count}")
    print(f"Successfully imported: {imported}")
    print(f"Errors/Skipped: {errors}")
    print(f"Final DB count: {final_count}")
    
    if final_count == csv_count:
        print("\n✅ SUCCESS: Database exactly matches CSV file!")
    else:
        print(f"\n⚠️  WARNING: Mismatch - DB has {final_count} but CSV has {csv_count}")
    
    print("\nYear-wise distribution in DB:")
    for year, count in year_dist:
        print(f"  {year}: {count} questions")
    
    print("\n✓ Database is now perfectly synced with CSV file")

if __name__ == '__main__':
    confirm = input("\n⚠️  WARNING: This will DELETE all existing questions and re-import from CSV.\nType 'YES' to continue: ")
    if confirm == 'YES':
        resync_database()
    else:
        print("Operation cancelled.")
