import sqlite3
import os
import json

DB_PATH = 'd:/upsc-second-brain/backend/upsc_saga.db'

MOCK_QUESTIONS = [
    # QUANT - Time & Work
    {
        "category": "Quant",
        "topic": "Time & Work",
        "question_text": "A can do a work in 15 days and B in 20 days. If they work on it together for 4 days, then the fraction of the work that is left is:",
        "options": ["1/4", "1/10", "7/15", "8/15"],
        "correct_option": "8/15",
        "explanation": "A's 1 day work = 1/15. B's 1 day work = 1/20. (A+B)'s 1 day work = (1/15 + 1/20) = 7/60. Work done in 4 days = 4 * (7/60) = 7/15. Remaining work = 1 - 7/15 = 8/15.",
        "difficulty": "Easy"
    },
    {
        "category": "Quant",
        "topic": "Time & Work",
        "question_text": "A is thrice as good a workman as B and therefore is able to finish a job in 60 days less than B. Working together, they can do it in:",
        "options": ["20 days", "22.5 days", "25 days", "30 days"],
        "correct_option": "22.5 days",
        "explanation": "Ratio of times taken by A and B = 1:3. Difference in time = 2 units -> 60 days. 1 unit -> 30 days. So A takes 30 days, B takes 90 days. Together = (30*90)/(30+90) = 2700/120 = 22.5 days.",
        "difficulty": "Medium"
    },
    {
        "category": "Quant",
        "topic": "Time & Work",
        "question_text": "A alone can do a piece of work in 6 days and B alone in 8 days. A and B undertook to do it for Rs. 3200. With the help of C, they completed the work in 3 days. How much is to be paid to C?",
        "options": ["Rs. 375", "Rs. 400", "Rs. 600", "Rs. 800"],
        "correct_option": "Rs. 400",
        "explanation": "C's 1 day work = 1/3 - (1/6 + 1/8) = 1/3 - 7/24 = 1/24. Ratio of work done by A:B:C = 1/6 : 1/8 : 1/24 = 4:3:1. C's share = (1/8) * 3200 = 400.",
        "difficulty": "Medium"
    },
    # QUANT - Speed, Time & Distance
    {
        "category": "Quant",
        "topic": "Speed, Time & Distance",
        "question_text": "A train running at the speed of 60 km/hr crosses a pole in 9 seconds. What is the length of the train?",
        "options": ["120 metres", "180 metres", "324 metres", "150 metres"],
        "correct_option": "150 metres",
        "explanation": "Speed = 60*(5/18) m/sec = 50/3 m/sec. Length = Speed * Time = (50/3) * 9 = 150 meters.",
        "difficulty": "Easy"
    },
    {
        "category": "Quant",
        "topic": "Speed, Time & Distance",
        "question_text": "A person crosses a 600 m long street in 5 minutes. What is his speed in km per hour?",
        "options": ["3.6", "7.2", "8.4", "10"],
        "correct_option": "7.2",
        "explanation": "Speed = 600/300 m/sec = 2 m/sec. In km/hr = 2 * 18/5 = 7.2 km/hr.",
        "difficulty": "Easy"
    },
    {
        "category": "Quant",
        "topic": "Speed, Time & Distance",
        "question_text": "Excluding stoppages, the speed of a bus is 54 kmph and including stoppages, it is 45 kmph. For how many minutes does the bus stop per hour?",
        "options": ["9", "10", "12", "20"],
        "correct_option": "10",
        "explanation": "Due to stoppages, it covers 9 km less. Time taken to cover 9 km = (9/54)*60 min = 10 min.",
        "difficulty": "Medium"
    },
    # QUANT - Percentages
    {
        "category": "Quant",
        "topic": "Percentages",
        "question_text": "Two students appeared at an examination. One of them secured 9 marks more than the other and his marks were 56% of the sum of their marks. The marks obtained by them are:",
        "options": ["39, 30", "41, 32", "42, 33", "43, 34"],
        "correct_option": "42, 33",
        "explanation": "Let marks be x and x+9. Sum = 2x+9. (x+9) = 0.56(2x+9). 25(x+9) = 14(2x+9). 25x+225 = 28x+126. 3x = 99. x = 33. Marks are 33 and 42.",
        "difficulty": "Medium"
    },
    {
        "category": "Quant",
        "topic": "Percentages",
        "question_text": "If A's height is 40% less than that of B, how much percent B's height is more than that of A?",
        "options": ["33.33%", "40%", "60%", "66.66%"],
        "correct_option": "66.66%",
        "explanation": "Let B = 100. A = 60. B is 40 more than A. % = (40/60)*100 = 66.66%.",
        "difficulty": "Easy"
    },
    # REASONING - Syllogism
    {
        "category": "Reasoning",
        "topic": "Syllogism",
        "question_text": "Statements: Some actors are singers. All the singers are dancers.\nConclusions:\n(1) Some actors are dancers.\n(2) No singer is actor.",
        "options": ["Only (1) follows", "Only (2) follows", "Either (1) or (2) follows", "Neither (1) nor (2) follows"],
        "correct_option": "Only (1) follows",
        "explanation": "Actors (Some) -> Singers (All) -> Dancers. So intersection of Actors and Dancers exists. (1) follows. (2) contradicts statement 1.",
        "difficulty": "Easy"
    },
    {
        "category": "Reasoning",
        "topic": "Syllogism",
        "question_text": "Statements: All the harmoniums are instruments. All the instruments are flutes.\nConclusions:\n(1) All the flutes are instruments.\n(2) All the harmoniums are flutes.",
        "options": ["Only (1) follows", "Only (2) follows", "Either (1) or (2) follows", "Neither (1) nor (2) follows"],
        "correct_option": "Only (2) follows",
        "explanation": "Harmoniums (All) -> Instruments (All) -> Flutes. So All Harmoniums are Flutes. Reverse is not necessarily true.",
        "difficulty": "Easy"
    },
    {
        "category": "Reasoning",
        "topic": "Syllogism",
        "question_text": "Statements: Some mangoes are yellow. Some tixo are mangoes.\nConclusions:\n(1) Some mangoes are green.\n(2) Tixo is a yellow.",
        "options": ["Only (1) follows", "Only (2) follows", "Either (1) or (2) follows", "Neither (1) nor (2) follows"],
        "correct_option": "Neither (1) nor (2) follows",
        "explanation": "No information about green mangoes. No relation established between Tixo and Yellow.",
        "difficulty": "Medium"
    },
    # REASONING - Blood Relations
    {
        "category": "Reasoning",
        "topic": "Blood Relations",
        "question_text": "Pointing to a photograph of a boy Suresh said, 'He is the son of the only son of my mother.' How is Suresh related to that boy?",
        "options": ["Brother", "Uncle", "Cousin", "Father"],
        "correct_option": "Father",
        "explanation": "Only son of my mother = Suresh himself. Son of Suresh = The boy. So Suresh is the Father.",
        "difficulty": "Easy"
    },
    {
        "category": "Reasoning",
        "topic": "Blood Relations",
        "question_text": "If A + B means A is the mother of B; A - B means A is the brother B; A % B means A is the father of B and A x B means A is the sister of B, which of the following shows that P is the maternal uncle of Q?",
        "options": ["Q - N + M x P", "P + S x N - Q", "P - M + N x Q", "Q - S % P"],
        "correct_option": "P - M + N x Q",
        "explanation": "P - M -> P is brother of M. M + N -> M is mother of N. So P is maternal uncle of N. N x Q -> N is sister of Q. So P is maternal uncle of Q.",
        "difficulty": "Hard"
    },
    # READING COMPREHENSION
    {
        "category": "Reading Comprehension",
        "topic": "Environment",
        "question_text": "Passage: Climate change is not just about rising temperatures. It is also about extreme weather events, shifting wildlife populations and habitats, rising seas, and a range of other impacts. All of these changes are emerging as humans continue to add heat-trapping greenhouse gases to the atmosphere.\n\nQ: What is the main idea of the passage?",
        "options": ["Climate change is only about rising temperatures.", "Human activities are the sole cause of climate change.", "Climate change encompasses various impacts beyond just temperature rise.", "Wildlife populations are increasing due to climate change."],
        "correct_option": "Climate change encompasses various impacts beyond just temperature rise.",
        "explanation": "The passage explicitly states 'Climate change is not just about rising temperatures' and lists other impacts.",
        "difficulty": "Easy"
    },
    {
        "category": "Reading Comprehension",
        "topic": "Environment",
        "question_text": "Passage: Biodiversity is the variety of life on Earth, in all its forms and all its interactions. If biological diversity is dropped, the ecosystem will not function properly. It provides us with food, water, and resources.\n\nQ: According to the passage, why is biodiversity important?",
        "options": ["It looks good.", "It is necessary for proper ecosystem functioning and providing resources.", "It increases the temperature of the earth.", "It reduces the variety of life."],
        "correct_option": "It is necessary for proper ecosystem functioning and providing resources.",
        "explanation": "The passage states 'If biological diversity is dropped, the ecosystem will not function properly' and mentions it provides resources.",
        "difficulty": "Easy"
    },
    {
        "category": "Reading Comprehension",
        "topic": "Economy",
        "question_text": "Passage: Inflation is the rate at which the general level of prices for goods and services is rising and, consequently, the purchasing power of currency is falling. Central banks attempt to limit inflation, and avoid deflation, in order to keep the economy running smoothly.\n\nQ: What is the primary role of central banks mentioned in the passage?",
        "options": ["To increase inflation.", "To decrease the purchasing power.", "To limit inflation and avoid deflation.", "To print more currency."],
        "correct_option": "To limit inflation and avoid deflation.",
        "explanation": "The passage states 'Central banks attempt to limit inflation, and avoid deflation'.",
        "difficulty": "Medium"
    },
    # QUANT - Averages
    {
        "category": "Quant",
        "topic": "Averages",
        "question_text": "The average of 20 numbers is zero. Of them, at the most, how many may be greater than zero?",
        "options": ["0", "1", "10", "19"],
        "correct_option": "19",
        "explanation": "Average is 0 means sum is 0. It is possible to have 19 positive numbers and 1 large negative number such that their sum is 0.",
        "difficulty": "Easy"
    },
    {
        "category": "Quant",
        "topic": "Averages",
        "question_text": "The average weight of 8 person's increases by 2.5 kg when a new person comes in place of one of them weighing 65 kg. What might be the weight of the new person?",
        "options": ["76 kg", "76.5 kg", "85 kg", "Data inadequate"],
        "correct_option": "85 kg",
        "explanation": "Total weight increased by 8 * 2.5 = 20 kg. So new person weight = 65 + 20 = 85 kg.",
        "difficulty": "Medium"
    },
    # REASONING - Coding Decoding
    {
        "category": "Reasoning",
        "topic": "Coding Decoding",
        "question_text": "If in a certain language, MADRAS is coded as NBESBT, how is BOMBAY coded in that code?",
        "options": ["CPNCBX", "CPNCBZ", "CPOCBZ", "CQOCBZ"],
        "correct_option": "CPNCBZ",
        "explanation": "Each letter is shifted by +1. B->C, O->P, M->N, B->C, A->B, Y->Z.",
        "difficulty": "Easy"
    },
    {
        "category": "Reasoning",
        "topic": "Coding Decoding",
        "question_text": "In a certain code, TRIPPLE is written as SQHOOKD. How is DISPOSE written in that code?",
        "options": ["CHRONRD", "DSOESPI", "ESJTPTF", "ESOPSID"],
        "correct_option": "CHRONRD",
        "explanation": "Each letter is shifted by -1. D->C, I->H, S->R, P->O, O->N, S->R, E->D.",
        "difficulty": "Medium"
    },
    # QUANT - Number System
    {
        "category": "Quant",
        "topic": "Number System",
        "question_text": "The sum of first 45 natural numbers is:",
        "options": ["1035", "1280", "2070", "2140"],
        "correct_option": "1035",
        "explanation": "Sum = n(n+1)/2 = 45*46/2 = 45*23 = 1035.",
        "difficulty": "Easy"
    },
    {
        "category": "Quant",
        "topic": "Number System",
        "question_text": "Which of the following numbers is exactly divisible by 99?",
        "options": ["114345", "135792", "3572404", "913464"],
        "correct_option": "114345",
        "explanation": "Divisible by 99 means divisible by 9 and 11. 114345: Sum digits = 18 (div by 9). Alt sum = (1+4+5)-(1+3+4) = 10-8=2 (Not div by 11). Wait, let's check 114345 again. 1+4+5 = 10. 1+3+4 = 8. Diff 2. Not div by 11. Let's check 135792. Sum=27 (div by 9). Alt sum = (1+5+9)-(3+7+2) = 15-12=3. Not div by 11. Let's check 913464. Sum=27 (div by 9). Alt sum = (9+3+6)-(1+4+4) = 18-9=9. Not div by 11. Wait, let me re-calculate. 114345/99 = 1155. It IS divisible. My manual calc was wrong. 1+4+5=10. 1+3+4=8. Diff 2. Ah, 114345: 1,1,4,3,4,5. Odd pos: 1+4+4=9. Even pos: 1+3+5=9. Diff=0. Divisible by 11! Yes.",
        "difficulty": "Hard"
    },
    # REASONING - Direction Sense
    {
        "category": "Reasoning",
        "topic": "Direction Sense",
        "question_text": "One morning Udai and Vishal were talking to each other face to face at a crossing. If Vishal's shadow was exactly to the left of Udai, which direction was Udai facing?",
        "options": ["East", "West", "North", "South"],
        "correct_option": "North",
        "explanation": "Morning -> Sun in East -> Shadow in West. Shadow is to left of Udai. So West is to left of Udai. Person facing North has West to their left.",
        "difficulty": "Medium"
    },
    {
        "category": "Reasoning",
        "topic": "Direction Sense",
        "question_text": "Y is in the East of X which is in the North of Z. If P is in the South of Z, then in which direction of Y, is P?",
        "options": ["North", "South", "South-East", "South-West"],
        "correct_option": "South-West",
        "explanation": "X is North of Z. P is South of Z. So P is South of X. Y is East of X. So P is South-West of Y.",
        "difficulty": "Medium"
    },
    # QUANT - Profit & Loss
    {
        "category": "Quant",
        "topic": "Profit & Loss",
        "question_text": "Alfred buys an old scooter for Rs. 4700 and spends Rs. 800 on its repairs. If he sells the scooter for Rs. 5800, his gain percent is:",
        "options": ["4 4/7%", "5 5/11%", "10%", "12%"],
        "correct_option": "5 5/11%",
        "explanation": "CP = 4700 + 800 = 5500. SP = 5800. Gain = 300. Gain % = (300/5500)*100 = 300/55 = 60/11 = 5 5/11 %.",
        "difficulty": "Medium"
    }
]

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Creating csat_questions table...")
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS csat_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                topic TEXT NOT NULL,
                question_text TEXT NOT NULL,
                options TEXT NOT NULL,
                correct_option TEXT NOT NULL,
                explanation TEXT,
                difficulty TEXT
            )
        ''')
        print("Table created successfully.")
        
        print(f"Inserting {len(MOCK_QUESTIONS)} mock questions...")
        for q in MOCK_QUESTIONS:
            cursor.execute('''
                INSERT INTO csat_questions (category, topic, question_text, options, correct_option, explanation, difficulty)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                q['category'],
                q['topic'],
                q['question_text'],
                json.dumps(q['options']),
                q['correct_option'],
                q['explanation'],
                q['difficulty']
            ))
            
        conn.commit()
        print("Data inserted successfully.")
        
    except Exception as e:
        print(f"Error creating table or inserting data: {e}")
            
    conn.close()

if __name__ == "__main__":
    migrate()
