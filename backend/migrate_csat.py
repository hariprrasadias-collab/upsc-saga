import sqlite3
import os
import json

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'app', 'upsc_saga.db')

def migrate():
    print(f"Migrating database at {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create csat_questions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS csat_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL, -- Quant, Reasoning, RC
        topic TEXT NOT NULL,
        question_text TEXT NOT NULL,
        options TEXT NOT NULL, -- JSON string of options
        correct_option TEXT NOT NULL,
        explanation TEXT,
        difficulty TEXT DEFAULT 'Medium'
    )
    ''')
    
    print("Created csat_questions table.")
    
    # Check if we need to seed data
    cursor.execute('SELECT COUNT(*) FROM csat_questions')
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("Seeding sample CSAT questions...")
        sample_questions = [
            {
                "category": "Quant",
                "topic": "Time & Work",
                "question_text": "A can do a piece of work in 10 days and B in 15 days. If they work together, how long will they take to finish the work?",
                "options": json.dumps(["5 days", "6 days", "8 days", "9 days"]),
                "correct_option": "6 days",
                "explanation": "A's 1 day work = 1/10. B's 1 day work = 1/15. (A+B)'s 1 day work = 1/10 + 1/15 = 5/30 = 1/6. So, they will take 6 days.",
                "difficulty": "Easy"
            },
            {
                "category": "Quant",
                "topic": "Percentages",
                "question_text": "If the price of sugar increases by 20%, by what percentage should a housewife reduce her consumption so that expenditure remains the same?",
                "options": json.dumps(["16.66%", "20%", "25%", "15%"]),
                "correct_option": "16.66%",
                "explanation": "Reduction % = (R / (100 + R)) * 100 = (20 / 120) * 100 = 16.66%",
                "difficulty": "Medium"
            },
            {
                "category": "Reasoning",
                "topic": "Syllogism",
                "question_text": "Statements: All cats are dogs. Some dogs are birds. Conclusion I: Some cats are birds. Conclusion II: Some birds are dogs.",
                "options": json.dumps(["Only I follows", "Only II follows", "Both follow", "Neither follows"]),
                "correct_option": "Only II follows",
                "explanation": "From 'Some dogs are birds', it follows that 'Some birds are dogs'. There is no direct relation given between cats and birds.",
                "difficulty": "Medium"
            },
            {
                "category": "Reasoning",
                "topic": "Blood Relations",
                "question_text": "Pointing to a photograph, a man said, 'I have no brother or sister but that man's father is my father's son.' Whose photograph was it?",
                "options": json.dumps(["His own", "His son", "His father", "His nephew"]),
                "correct_option": "His son",
                "explanation": "Since he has no siblings, 'my father's son' is the man himself. So, the man's father is the speaker himself. Thus, the photograph is of his son.",
                "difficulty": "Hard"
            },
            {
                "category": "RC",
                "topic": "Reading Comprehension",
                "question_text": "Passage: Climate change is a reality. We are seeing its effects in extreme weather events... Question: What is the main theme?",
                "options": json.dumps(["Weather patterns", "Climate Change Reality", "Politics", "Economics"]),
                "correct_option": "Climate Change Reality",
                "explanation": "The passage explicitly states climate change is a reality and discusses its effects.",
                "difficulty": "Easy"
            }
        ]
        
        for q in sample_questions:
            cursor.execute('''
                INSERT INTO csat_questions (category, topic, question_text, options, correct_option, explanation, difficulty)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (q['category'], q['topic'], q['question_text'], q['options'], q['correct_option'], q['explanation'], q['difficulty']))
            
        print(f"Seeded {len(sample_questions)} questions.")
    
    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == '__main__':
    migrate()
