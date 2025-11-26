import sqlite3

def check_schemas():
    try:
        conn = sqlite3.connect('upsc_saga.db')
        cursor = conn.cursor()
        
        print("--- User Answers ---")
        try:
            cursor.execute("PRAGMA table_info(user_answers)")
            for col in cursor.fetchall():
                print(col)
        except Exception as e:
            print(e)

        print("\n--- Answer Evaluations ---")
        try:
            cursor.execute("PRAGMA table_info(answer_evaluations)")
            for col in cursor.fetchall():
                print(col)
        except Exception as e:
            print(e)
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schemas()
