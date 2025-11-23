# Migration script for Mock Test Engine
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Creating Mock Test Engine tables...")

# Table 1: Mock Tests
cursor.execute('''
    CREATE TABLE IF NOT EXISTS mock_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        test_type TEXT NOT NULL,
        subject TEXT,
        total_questions INTEGER NOT NULL,
        duration_minutes INTEGER NOT NULL,
        total_marks INTEGER NOT NULL,
        negative_marking REAL DEFAULT 0.33,
        difficulty TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
''')

# Table 2: Test Questions
cursor.execute('''
    CREATE TABLE IF NOT EXISTS test_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id INTEGER NOT NULL,
        question_number INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        explanation TEXT,
        subject TEXT,
        topic TEXT,
        difficulty TEXT,
        year INTEGER,
        marks INTEGER DEFAULT 2,
        FOREIGN KEY (test_id) REFERENCES mock_tests(id)
    )
''')

# Table 3: Test Attempts
cursor.execute('''
    CREATE TABLE IF NOT EXISTS test_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL DEFAULT 1,
        test_id INTEGER NOT NULL,
        started_at TEXT DEFAULT CURRENT_TIMESTAMP,
        submitted_at TEXT,
        time_taken INTEGER,
        total_attempted INTEGER,
        total_correct INTEGER,
        total_incorrect INTEGER,
        total_unattempted INTEGER,
        score REAL,
        percentage REAL,
        status TEXT DEFAULT 'in_progress',
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (test_id) REFERENCES mock_tests(id)
    )
''')

# Table 4: Test Answers
cursor.execute('''
    CREATE TABLE IF NOT EXISTS test_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attempt_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        selected_answer TEXT,
        is_correct BOOLEAN,
        time_spent INTEGER DEFAULT 0,
        is_marked BOOLEAN DEFAULT 0,
        FOREIGN KEY (attempt_id) REFERENCES test_attempts(id),
        FOREIGN KEY (question_id) REFERENCES test_questions(id)
    )
''')

conn.commit()
print("✅ Tables created successfully!")

# Seed sample test
print("\nSeeding sample UPSC Prelims mock test...")

cursor.execute('INSERT INTO mock_tests (title, description, test_type, subject, total_questions, duration_minutes, total_marks, negative_marking, difficulty) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
    ("UPSC Prelims Mock Test 1", "A comprehensive test covering General Studies topics including Polity, Geography, Economy, History, and Current Affairs", "full-length", "General Studies", 25, 30, 50, 0.33, "Medium"))


test_id = cursor.lastrowid

# Sample Questions (25 questions covering various GS topics)
questions = [
    # Polity (5 questions)
    (1, "Which of the following statements about the Indian Constitution is/are correct?\n1. It is the lengthiest written constitution\n2. It is partly rigid and partly flexible\n3. It establishes a federal system with unitary features\nSelect the correct answer:", 
     "1 only", "1 and 2 only", "2 and 3 only", "All of the above", "D", 
     "All three statements are correct. The Indian Constitution is the world's lengthiest written constitution, it has both rigid (special majority) and flexible (simple majority) amendment procedures, and establishes a quasi-federal system with strong central government.", 
     "Polity", "Constitutional Features", "Easy", None),
    
    (2, "The concept of 'Basic Structure' of the Constitution was propounded in which case?",
     "Golaknath case", "Kesavananda Bharati case", "Minerva Mills case", "Maneka Gandhi case", "B",
     "The Basic Structure doctrine was established in Kesavananda Bharati v. State of Kerala (1973), which held that certain fundamental features of the Constitution cannot be amended.",
     "Polity", "Judicial Decisions", "Medium", None),
    
    (3, "Which Article of the Constitution provides for the creation of All India Services?",
     "Article 310", "Article 312", "Article 315", "Article 320", "B",
     "Article 312 empowers the Rajya Sabha to create All India Services by passing a resolution with 2/3rd majority. Currently, IAS, IPS, and IFS are All India Services.",
     "Polity", "All India Services", "Hard", 2019),
    
    (4, "The Ninth Schedule of the Constitution contains laws related to:",
     "Anti-defection", "Land reforms and abolition of zamindari", "Emergency provisions", "Fundamental Duties", "B",
     "The Ninth Schedule was added by the First Amendment (1951) to protect land reform laws from judicial review under Article 31B.",
     "Polity", "Constitutional Amendments", "Medium", None),
    
    (5, "Which of the following is NOT a feature of the Indian federal system?",
     "Dual polity", "Single citizenship", "Equal representation of states in Rajya Sabha", "Written Constitution", "C",
     "Unlike the US Senate, Indian Rajya Sabha does not have equal representation - states have different numbers of seats based on population (unequal representation).",
     "Polity", "Federalism", "Medium", None),
    
    # Geography (5 questions)
    (6, "The Western Ghats are an example of:",
     "Fold mountains", "Block mountains", "Volcanic mountains", "Residual mountains", "B",
     "Western Ghats are fault block mountains (horsts) formed due to faulting and vertical displacement of the earth's crust.",
     "Geography", "Physical Geography", "Easy", None),
    
    (7, "Which of the following ocean currents is a warm current?",
     "Labrador Current", "Canary Current", "Gulf Stream", "California Current", "C",
     "Gulf Stream is a warm current flowing from the Gulf of Mexico along the eastern coast of USA towards Europe.",
     "Geography", "Ocean Currents", "Easy", 2018),
    
    (8, "The Tropic of Cancer passes through how many Indian states?",
     "6", "7", "8", "9", "C",
     "The Tropic of Cancer (23.5°N) passes through 8 states: Gujarat, Rajasthan, MP, Chhattisgarh, Jharkhand, West Bengal, Tripura, and Mizoram.",
     "Geography", "Indian Geography", "Medium", None),
    
    (9, "Which type of soil is known as 'Regur'?",
     "Alluvial soil", "Black soil", "Red soil", "Laterite soil", "B",
     "Black soil (also called Regur or black cotton soil) is rich in lime, iron, magnesium and alumina. Found extensively in Deccan plateau.",
     "Geography", "Soil Types", "Easy", None),
    
    (10, "The river Brahmaputra is known by which name in Tibet?",
     "Tsangpo", "Dihang", "Jamuna", "Lohit", "A",
     "In Tibet, Brahmaputra is called Yarlung Tsangpo. It enters India as Dihang and becomes Brahmaputra in Assam.",
     "Geography", "Indian Rivers", "Medium", 2020),
    
    # Economy (5 questions)
    (11, "Which of the following is NOT a component of India's Forex reserves?",
     "Gold reserves", "Special Drawing Rights (SDR)", "Reserve Tranche Position in IMF", "Sovereign Gold Bonds", "D",
     "Forex reserves comprise: Foreign Currency Assets, Gold, SDRs, and Reserve Tranche Position. Sovereign Gold Bonds are domestic instruments.",
     "Economy", "Forex Reserves", "Medium", None),
    
    (12, "The term 'Stagflation' refers to:",
     "High inflation with high growth", "Low inflation with low growth", "High inflation with low growth", "Deflation with recession", "C",
     "Stagflation is the simultaneous occurrence of stagnant economic growth (low GDP growth or recession) and high inflation.",
     "Economy", "Economic Terms", "Easy", None),
    
    (13, "The Base Year for calculating GDP in India is currently:",
     "2004-05", "2011-12", "2014-15", "2017-18", "B",
     "India's GDP base year was revised to 2011-12 from 2004-05. This helps account for structural changes in the economy.",
     "Economy", "National Income", "Easy", 2021),
    
    (14, "Which committee recommended the concept of 'Minimum Support Price (MSP)'?",
     "L.C. Jain Committee", "Swaminathan Committee", "Rangarajan Committee", "Dalwai Committee", "B",
     "M.S. Swaminathan Committee (National Commission on Farmers) recommended MSP should be at least 50% more than weighted average cost of production.",
     "Economy", "Agriculture", "Hard", None),
    
    (15, "NABARD was established based on recommendations of:",
     "CRAFICARD Committee", "Sivaraman Committee", "Narasimham Committee", "Gadgil Committee", "B",
     "NABARD was established in 1982 based on recommendations of B. Sivaraman Committee to serve as an apex institution for rural credit.",
     "Economy", "Banking & Finance", "Hard", 2017),
    
    # History (5 questions)
    (16, "The First Factory Act in India was passed in:",
     "1881", "1891", "1911", "1921", "A",
     "The First Factory Act of 1881 was passed to improve labor conditions, especially for children and women in factories.",
     "History", "Modern India", "Medium", None),
    
    (17, "The 'Doctrine of Lapse' was introduced by:",
     "Lord Wellesley", "Lord Hastings", "Lord Dalhousie", "Lord Cornwallis", "C",
     "Lord Dalhousie introduced the Doctrine of Lapse (1848-56) which denied succession rights to adopted heirs, leading to annexation of several states.",
     "History", "British Policy", "Easy", 2019),
    
    (18, "The Quit India Movement was launched in:",
     "1940", "1941", "1942", "1943", "C",
     "The Quit India Movement was launched on 8 August 1942 with the slogan 'Do or Die'. It demanded immediate British withdrawal from India.",
     "History", "Freedom Struggle", "Easy", None),
    
    (19, "Which Viceroy partitioned Bengal in 1905?",
     "Lord Curzon", "Lord Minto", "Lord Hardinge", "Lord Chelmsford", "A",
     "Lord Curzon partitioned Bengal in 1905 ostensibly for administrative convenience but actually to divide Hindus and Muslims. It was annulled in 1911.",
     "History", "British Rule", "Medium", 2018),
    
    (20, "The Gandhi-Irwin Pact was signed in:",
     "1929", "1930", "1931", "1932", "C",
     "The Gandhi-Irwin Pact was signed on 5 March 1931, leading to suspension of Civil Disobedience Movement and Gandhi's participation in Second Round Table Conference.",
     "History", "Freedom Movement", "Medium", None),
    
    # Current Affairs & Misc (5 questions)
    (21, "The International Solar Alliance (ISA) headquarters is located in:",
     "Paris", "Gurugram", "New Delhi", "Geneva", "B",
     "ISA headquarters is in Gurugram, India. It was jointly launched by India and France in 2015 to promote solar energy.",
     "Current Affairs", "International Organizations", "Easy", None),
    
    (22, "Which of the following is a UNESCO World Heritage Site in India?\n1. Qutub Minar\n2. Red Fort\n3. Gateway of India\nSelect the correct answer:",
     "1 only", "1 and 2 only", "2 and 3 only", "All of the above", "B",
     "Qutub Minar and Red Fort are UNESCO World Heritage Sites. Gateway of India is not a World Heritage Site.",
     "Art & Culture", "Heritage Sites", "Medium", None),
    
    (23, "The Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) provides:",
     "₹4,000 per year", "₹6,000 per year", "₹8,000 per year", "₹10,000 per year", "B",
     "PM-KISAN provides direct income support of ₹6,000 per year to farmer families in three equal installments of ₹2,000 each.",
     "Current Affairs", "Government Schemes", "Easy", 2020),
    
    (24, "The Global Hunger Index is published by:",
     "FAO", "WFP", "Concern Worldwide and Welthungerhilfe", "World Bank", "C",
     "Global Hunger Index is published jointly by Concern Worldwide (Ireland) and Welthungerhilfe (Germany).",
     "Current Affairs", "Reports & Indices", "Hard", None),
    
    (25, "Article 371 of the Constitution contains special provisions for:",
     "Jammu & Kashmir", "North-Eastern states", "Maharashtra and Gujarat", "All of the above", "D",
     "Article 371 and its variants (371A to 371J) provide special provisions for multiple states including J&K (now abrogated), NE states, Maharashtra, Gujarat, etc.",
     "Polity", "Special Provisions", "Hard", 2021),
]

for q in questions:
    cursor.execute('''
        INSERT INTO test_questions 
        (test_id, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation, subject, topic, difficulty, year)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (test_id, q[0], q[1], q[2], q[3], q[4], q[5], q[6], q[7], q[8], q[9], q[10], q[11]))

conn.commit()
print(f"✅ Seeded test with {len(questions)} questions!")

# Show summary
cursor.execute('SELECT COUNT(*) FROM mock_tests')
test_count = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM test_questions')
question_count = cursor.fetchone()[0]

print(f"\n📊 Database Summary:")
print(f"   Tests: {test_count}")
print(f"   Questions: {question_count}")

conn.close()
print("\n🎉 Migration completed successfully!")
print("Mock Test Engine is ready to use!")
