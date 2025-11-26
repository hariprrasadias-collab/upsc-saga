import sqlite3
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def clean_duplicates():
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Find duplicates: same question_text and options
        # We want to keep the one with the MIN(id)
        
        print("Identifying duplicates...")
        
        # This query deletes rows where the ID is NOT in the list of minimum IDs for each group of duplicates
        query = '''
            DELETE FROM pyq_questions
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM pyq_questions
                GROUP BY question_text, option_a, option_b, option_c, option_d
            )
        '''
        
        cursor.execute(query)
        deleted_count = cursor.rowcount
        
        conn.commit()
        print(f"Successfully removed {deleted_count} duplicate questions.")
        
        # Verify count remaining
        cursor.execute("SELECT COUNT(*) FROM pyq_questions")
        remaining_count = cursor.fetchone()[0]
        print(f"Total questions remaining: {remaining_count}")

    except Exception as e:
        print(f"Error cleaning duplicates: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    clean_duplicates()
