import sqlite3
import os
import json

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'app', 'upsc_saga.db')

def add_comprehensive_topics():
    """Add comprehensive CSAT topics across all categories"""
    print(f"Adding comprehensive CSAT topics to {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
   
    # Additional comprehensive questions
    comprehensive_questions = [
        # Data Interpretation
        {
            "category": "Data Interpretation",
            "topic": "Tables",
            "question_text": "A table shows sales data for 5 products over 4 quarters. If Product A sales in Q1 were 2000 and increased by 15% in Q2, what were Q2 sales?",
            "options": json.dumps(["2150", "2300", "2250", "2000"]),
            "correct_option": "2300",
            "explanation": "15% of 2000 = 300. Q2 sales = 2000 + 300 = 2300",
            "difficulty": "Easy"
        },
        {
            "category": "Data Interpretation",
            "topic": "Bar Graphs",
            "question_text": "A bar graph shows rainfall (cm) for 6 months. If average rainfall is 50cm and Jan-May total is 220cm, what is June rainfall?",
            "options": json.dumps(["60cm", "70cm", "80cm", "50cm"]),
            "correct_option": "80cm",
            "explanation": "Total for 6 months = 50 × 6 = 300cm. June = 300 - 220 = 80cm",
            "difficulty": "Medium"
        },
        # Logical Reasoning - Additional topics
        {
            "category": "Reasoning",
            "topic": "Coding-Decoding",
            "question_text": "If BOOK is coded as CQPM, how is PAPER coded?",
            "options": json.dumps(["QBQFS", "OBODO", "QCQFS", "RCRGT"]),
            "correct_option": "QBQFS",
            "explanation": "Each letter is shifted +1 in alphabet. P→Q, A→B, P→Q, E→F, R→S",
            "difficulty": "Medium"
        },
        {
            "category": "Reasoning",
            "topic": "Series Completion",
            "question_text": "Find the next number: 2, 6, 12, 20, 30, ?",
            "options": json.dumps(["40", "42", "45", "48"]),
            "correct_option": "42",
            "explanation": "Differences: 4, 6, 8, 10, 12. Next difference is 12, so 30 + 12 = 42",
            "difficulty": "Easy"
        },
        {
            "category": "Reasoning",
            "topic": "Direction Sense",
            "question_text": "A person walks 5km South, then 3km East, then 5km North. How far is he from starting point?",
            "options": json.dumps(["3km", "5km", "8km", "13km"]),
            "correct_option": "3km",
            "explanation": "South and North cancel out. Only East 3km displacement remains.",
            "difficulty": "Easy"
        },
        # Quantitative Aptitude - More topics
        {
            "category": "Quant",
            "topic": "Ratio & Proportion",
            "question_text": "Two numbers are in ratio 3:5. If their sum is 80, find the larger number.",
            "options": json.dumps(["30", "40", "50", "60"]),
            "correct_option": "50",
            "explanation": "Let numbers be 3x and 5x. 3x + 5x = 80, 8x = 80, x = 10. Larger = 5x = 50",
            "difficulty": "Easy"
        },
        {
            "category": "Quant",
            "topic": "Simple Interest",
            "question_text": "A sum of Rs. 1000 at 10% p.a. for 3 years yields simple interest of?",
            "options": json.dumps(["Rs. 200", "Rs. 250", "Rs. 300", "Rs. 350"]),
            "correct_option": "Rs. 300",
            "explanation": "SI = (P × R × T) / 100 = (1000 × 10 × 3) / 100 = 300",
            "difficulty": "Easy"
        },
        {
            "category": "Quant",
            "topic": "Averages",
            "question_text": "Average of 5 numbers is 30. If one number 50 is excluded, what is new average?",
            "options": json.dumps(["20", "25", "27.5", "32.5"]),
            "correct_option": "25",
            "explanation": "Sum of 5 = 30 × 5 = 150. Excluding 50: Sum = 100. New avg = 100/4 = 25",
            "difficulty": "Medium"
        },
        {
            "category": "Quant",
            "topic": "Profit & Loss",
            "question_text": "A shopkeeper sells an article at 20% profit. If CP was Rs. 500, what is SP?",
            "options": json.dumps(["Rs. 550", "Rs. 600", "Rs. 620", "Rs. 700"]),
            "correct_option": "Rs. 600",
            "explanation": "SP = CP + 20% of CP = 500 + 100 = 600",
            "difficulty": "Easy"
        },
        # Reading Comprehension - Different types
        {
            "category": "Reading Comprehension",
            "topic": "Science & Technology",
            "question_text": "[Passage about AI] Question: What is the main concern about AI mentioned?",
            "options": json.dumps(["Job displacement", "Privacy", "Cost", "Complexity"]),
            "correct_option": "Job displacement",
            "explanation": "The passage emphasizes automation's impact on employment",
            "difficulty": "Medium"
        },
        {
            "category": "Reading Comprehension",
            "topic": "Social Issues",
            "question_text": "[Passage on education] Question: According to passage, main barrier to education is?",
            "options": json.dumps(["Poverty", "Infrastructure", "Both A & B", "None"]),
            "correct_option": "Both A & B",
            "explanation": "Passage explicitly states both poverty and lack of schools as barriers",
            "difficulty": "Easy"
        },
        {
            "category": "Reading Comprehension",
            "topic": "Economics",
            "question_text": "[Passage on inflation] Question: What measure is suggested to control inflation?",
            "options": json.dumps(["Increase interest rates", "Print more currency", "Reduce taxes", "Increase spending"]),
            "correct_option": "Increase interest rates",
            "explanation": "Higher interest rates reduce money supply and curb inflation",
            "difficulty": "Medium"
        }
    ]
    
    added_count = 0
    for q in comprehensive_questions:
        try:
            # Check if similar question already exists
            cursor.execute('''
                SELECT COUNT(*) FROM csat_questions 
                WHERE category = ? AND topic = ? AND question_text = ?
            ''', (q['category'], q['topic'], q['question_text']))
            
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO csat_questions (category, topic, question_text, options, correct_option, explanation, difficulty)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (q['category'], q['topic'], q['question_text'], q['options'], q['correct_option'], q['explanation'], q['difficulty']))
                added_count += 1
        except Exception as e:
            print(f"Error adding question: {e}")
    
    conn.commit()
    
    # Show unique topics now available
    cursor.execute('''
        SELECT DISTINCT category, topic FROM csat_questions
        ORDER BY category, topic
    ''')
    topics = cursor.fetchall()
    
    print(f"\nAdded {added_count} new questions.")
    print(f"\nAvailable CSAT Topics:")
    current_category = None
    for category, topic in topics:
        if category != current_category:
            print(f"\n{category}:")
            current_category = category
        print(f"  - {topic}")
    
    conn.close()
    print("\nCSAT topics expansion complete!")

if __name__ == '__main__':
    add_comprehensive_topics()
