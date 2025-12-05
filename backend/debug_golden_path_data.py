import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'upsc_saga.db')

def debug_data():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    
    print("--- Syllabus Topics (Sample) ---")
    syllabus = conn.execute("SELECT topic FROM syllabus_topics LIMIT 10").fetchall()
    for row in syllabus:
        print(f"'{row['topic']}'")
        
    print("\n--- PYQ Topics (Sample) ---")
    pyqs = conn.execute("SELECT DISTINCT topic FROM pyq_questions LIMIT 10").fetchall()
    for row in pyqs:
        print(f"'{row['topic']}'")
        
    print("\n--- Checking for Matches ---")
    matches = 0
    total_pyq_topics = 0
    pyq_topics = conn.execute("SELECT DISTINCT topic FROM pyq_questions").fetchall()
    for p_row in pyq_topics:
        p_topic = p_row['topic']
        total_pyq_topics += 1
        match = conn.execute("SELECT 1 FROM syllabus_topics WHERE topic = ?", (p_topic,)).fetchone()
        if match:
            matches += 1
        else:
            # Try fuzzy match or case insensitive
            pass
            
    print(f"Total PYQ Topics: {total_pyq_topics}")
    print(f"Exact Matches in Syllabus: {matches}")
    
    conn.close()

if __name__ == "__main__":
    debug_data()
