import sqlite3
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def migrate_pyq():
    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create PYQ Questions Table
    print("Creating pyq_questions table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pyq_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_option TEXT NOT NULL,
            explanation TEXT,
            difficulty TEXT DEFAULT 'Medium',
            is_favorite BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Check if data exists
    cursor.execute('SELECT count(*) FROM pyq_questions')
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("Seeding sample PYQ data...")
        # Sample Data (A mix of subjects and years)
        questions = [
            # 2023 - Polity
            (2023, 'Polity', 'Constitutional Bodies', 
             'Consider the following statements regarding the Election Commission of India:\n1. It is a five-member body.\n2. The Chief Election Commissioner can be removed only in like manner and on like grounds as a Judge of the Supreme Court.\nWhich of the statements given above is/are correct?',
             '1 only', '2 only', 'Both 1 and 2', 'Neither 1 nor 2', 
             'B', 
             'The Election Commission is a three-member body (CEC + 2 ECs). The CEC can be removed like a SC Judge.', 'Medium'),
             
            (2023, 'Polity', 'Fundamental Rights', 
             'Which one of the following categories of Fundamental Rights incorporates protection against untouchability as a form of discrimination?',
             'Right against Exploitation', 'Right to Freedom', 'Right to Constitutional Remedies', 'Right to Equality', 
             'D', 
             'Article 17 (Abolition of Untouchability) falls under Right to Equality (Articles 14-18).', 'Easy'),

            # 2022 - Economy
            (2022, 'Economy', 'Banking', 
             'With reference to the "Banks Board Bureau (BBB)", which of the following statements are correct?\n1. The Governor of RBI is the Chairman of BBB.\n2. BBB recommends for the selection of heads for Public Sector Banks.\n3. BBB helps the Public Sector Banks in developing strategies and capital raising plans.',
             '1 and 2 only', '2 and 3 only', '1 and 3 only', '1, 2 and 3', 
             'B', 
             'The RBI Governor is NOT the Chairman of BBB. It recommends heads for PSBs and helps in strategy.', 'Hard'),

            # 2021 - History
            (2021, 'History', 'Modern India', 
             'In the first quarter of the seventeenth century, in which of the following was/were the factory/factories of the English East India Company located?',
             'Broach', 'Chicacole', 'Trichinopoly', 'Broach only', # Simplified options for demo
             'A', 
             'By 1623, English East India Company had established factories at Surat, Broach, Ahmedabad, Agra, and Masulipatam.', 'Hard'),

            # 2020 - Environment
            (2020, 'Environment', 'Protected Areas', 
             'Which of the following are the most likely places to find the Musk Deer in its natural habitat?\n1. Askot Wildlife Sanctuary\n2. Gangotri National Park\n3. Kishanpur Wildlife Sanctuary\n4. Manas National Park',
             '1 and 2 only', '2 and 3 only', '3 and 4 only', '1 and 4 only', 
             'A', 
             'Musk Deer is found in high altitude Himalayas. Askot and Gangotri are in Uttarakhand Himalayas.', 'Medium'),
             
             # 2019 - Geography
            (2019, 'Geography', 'Agriculture', 
             'With reference to the cultivation of Kharif crops in India in the last five years, consider the following statements:\n1. Area under rice cultivation is the highest.\n2. Area under the cultivation of jowar is more than that of oilseeds.',
             '1 only', '2 only', 'Both 1 and 2', 'Neither 1 nor 2', 
             'A', 
             'Rice has the highest area under cultivation in India. Oilseeds area is generally higher than Jowar.', 'Medium'),

            # More 2023
            (2023, 'History', 'Ancient India', 'Who among the following rulers of Vijayanagara Empire constructed a large dam across Tungabhadra River?', 'Devaraya I', 'Mallikarjuna', 'Vira Vijaya', 'Virupaksha', 'A', 'Devaraya I constructed a dam across Tungabhadra to bring canal water to the city.', 'Medium'),
            (2023, 'Environment', 'Pollution', 'Consider the following heavy metals:\n1. Lead\n2. Mercury\n3. Nickel\nWhich of these are often released into the environment by coal-fired thermal power plants?', '1 only', '2 and 3 only', '1 and 3 only', '1, 2 and 3', 'D', 'Coal contains trace amounts of many heavy metals including lead, mercury, and nickel which are released upon combustion.', 'Easy'),
            
            # More 2022
            (2022, 'Polity', 'Parliament', 'Consider the following statements:\n1. A bill amending the Constitution requires a prior recommendation of the President of India.\n2. When a Constitution Amendment Bill is presented to the President of India, it is obligatory for the President of India to give his/her assent.', '1 only', '2 only', 'Both 1 and 2', 'Neither 1 nor 2', 'B', 'Prior recommendation of President is NOT required for Constitution Amendment Bill. Assent is obligatory (24th Amendment).', 'Medium'),
            (2022, 'Geography', 'Climate', 'Consider the following states:\n1. Andhra Pradesh\n2. Kerala\n3. Himachal Pradesh\n4. Tripura\nHow many of the above are generally known as tea-producing States?', 'Only one state', 'Only two states', 'Only three states', 'All four states', 'C', 'Kerala, Himachal Pradesh, and Tripura produce tea. Andhra Pradesh does not.', 'Hard')
        ]

        cursor.executemany('''
            INSERT INTO pyq_questions (year, subject, topic, question_text, option_a, option_b, option_c, option_d, correct_option, explanation, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', questions)
        print(f"Seeded {len(questions)} PYQ questions.")
    else:
        print(f"Table already exists with {count} questions. Skipping seed.")

    conn.commit()
    conn.close()
    print("PYQ Migration completed successfully!")

if __name__ == '__main__':
    migrate_pyq()
