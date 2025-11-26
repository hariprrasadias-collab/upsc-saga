import sqlite3

def debug_battles():
    try:
        conn = sqlite3.connect('upsc_saga.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("Checking Mock Test Attempts...")
        cursor.execute('''
            SELECT 
                at.id, 
                mt.title as boss_name, 
                mt.subject, 
                mt.total_marks, 
                at.score as my_score, 
                at.percentage,
                at.submitted_at as date_fought
            FROM test_attempts at
            JOIN mock_tests mt ON at.test_id = mt.id
            WHERE at.user_id = 1 AND at.status = 'completed'
        ''')
        rows = cursor.fetchall()
        print(f"Found {len(rows)} mock test attempts.")
        
        for i, row in enumerate(rows):
            data = dict(row)
            if data['total_marks'] is None:
                print(f"Row {i}: total_marks is None! ID: {data['id']}")
            if data['my_score'] is None:
                print(f"Row {i}: my_score is None! ID: {data['id']}")
            if data['percentage'] is None:
                print(f"Row {i}: percentage is None! ID: {data['id']}")

        print("\nChecking Answer Writing Submissions...")
        cursor.execute('''
            SELECT 
                ua.id, 
                p.question as boss_name, 
                p.subject, 
                ae.overall_score,
                ua.submitted_at as date_fought
            FROM user_answers ua
            JOIN answer_writing_prompts p ON ua.prompt_id = p.id
            LEFT JOIN answer_evaluations ae ON ua.id = ae.answer_id
            WHERE ua.user_id = 1
        ''')
        rows = cursor.fetchall()
        print(f"Found {len(rows)} answer submissions.")
        for i, row in enumerate(rows):
            data = dict(row)
            # overall_score can be None (LEFT JOIN)
            if data['overall_score'] is None:
                print(f"Row {i}: overall_score is None (Expected if not evaluated). ID: {data['id']}")
            
        conn.close()
    except Exception as e:
        print(f"Database connection error: {e}")

if __name__ == "__main__":
    debug_battles()
