# Migration script for Answer Writing Practice module
import sqlite3
import os
import json

db_path = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Creating Answer Writing Practice tables...")

# Table 1: Answer Writing Prompts
cursor.execute('''
    CREATE TABLE IF NOT EXISTS answer_writing_prompts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        word_limit INTEGER NOT NULL,
        subject TEXT,
        topic TEXT,
        difficulty TEXT,
        year INTEGER,
        source TEXT,
        ideal_structure TEXT,
        keywords TEXT,
        model_answer TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )
''')

# Table 2: User Answers
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL DEFAULT 1,
        prompt_id INTEGER NOT NULL,
        answer_text TEXT NOT NULL,
        word_count INTEGER,
        time_taken INTEGER,
        submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (prompt_id) REFERENCES answer_writing_prompts(id)
    )
''')

# Table 3: Answer Evaluations
cursor.execute('''
    CREATE TABLE IF NOT EXISTS answer_evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        answer_id INTEGER NOT NULL,
        overall_score REAL,
        structure_score REAL,
        content_score REAL,
        relevance_score REAL,
        keyword_coverage REAL,
        strengths TEXT,
        improvements TEXT,
        missing_keywords TEXT,
        evaluation_type TEXT DEFAULT 'AI',
        evaluated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (answer_id) REFERENCES user_answers(id)
    )
''')

conn.commit()
print("✅ Tables created successfully!")

# Seed some sample prompts
print("\nSeeding sample prompts...")

sample_prompts = [
    {
        "question": "Discuss the role of local governance in strengthening democracy in India.",
        "word_limit": 150,
        "subject": "GS2",
        "topic": "Polity - Local Governance",
        "difficulty": "Medium",
        "year": 2022,
        "source": "PYQ",
        "keywords": "local governance, panchayati raj, 73rd amendment, decentralization, grass-root democracy, participation",
        "model_answer": "Local governance strengthens democracy through decentralization and citizen participation. The 73rd and 74th Constitutional Amendments institutionalized Panchayati Raj, empowering rural and urban local bodies. This enables grass-root democracy where citizens directly participate in decision-making on local issues like sanitation, education, and infrastructure. Local governance ensures better accountability, efficient resource allocation, and inclusive development. However, challenges like inadequate funding, political interference, and capacity gaps persist. Strengthening local governance requires financial devolution, capacity building, and ensuring social inclusion. When empowered, local bodies can transform democracy from a distant concept to lived reality."
    },
    {
        "question": "Analyze the impact of climate change on agricultural productivity in India. Suggest policy measures to address this challenge.",
        "word_limit": 250,
        "subject": "GS3",
        "topic": "Environment - Climate Change & Agriculture",
        "difficulty": "Medium",
        "year": 2023,
        "source": "PYQ",
        "keywords": "climate change, agricultural productivity, monsoon variability, crop failure, adaptation, mitigation, climate-resilient agriculture, insurance",
        "model_answer": "Climate change poses severe threats to India's agricultural productivity through increased temperature, erratic monsoons, and extreme weather events. Studies show that a 1°C rise in temperature can reduce wheat yields by 6-7%. Changing rainfall patterns affect kharif crops, while heat stress reduces crop quality. Increased pest attacks and soil degradation further compound the crisis. Smallholder farmers, constituting 86% of farming community, are most vulnerable. Policy interventions must focus on: 1) Promoting climate-resilient varieties through research and distribution 2) Expanding crop insurance coverage under PM Fasal Bima Yojana 3) Investing in irrigation infrastructure (micro-irrigation, drip systems) 4) Strengthening weather forecasting and early warning systems 5) Encouraging crop diversification and agro-forestry 6) Providing adequate credit at low interest rates. Additionally, promoting organic farming and zero-budget natural farming can enhance soil health. Carbon credits for farmers practicing sustainable agriculture can provide additional income. A comprehensive National Adaptation Plan for agriculture, backed by adequate funding and technology transfer, is essential to secure India's food security in the face of climate change."
    },
    {
        "question": "What is the significance of ethical values in governance? Illustrate with examples.",
        "word_limit": 150,
        "subject": "GS4",
        "topic": "Ethics - Governance",
        "difficulty": "Easy",
        "year": 2021,
        "source": "PYQ",
        "keywords": "ethical values, governance, integrity, accountability, transparency, public trust, citizen-centric, corruption-free",
        "model_answer": "Ethical values form the bedrock of good governance, ensuring public trust and effective service delivery. Integrity prevents corruption and ensures honest decision-making. Accountability makes officials answerable for their actions, as seen in RTI Act implementation. Transparency builds citizen confidence - e-governance portals publishing government data exemplify this. Compassion ensures welfare schemes reach the needy, like during COVID-19 relief distribution. Impartiality guarantees equal treatment, crucial in judicial administration. The 'Swachh Bharat' campaign's success demonstrates how value-driven governance can transform society. Conversely, ethical lapses like the 2G spectrum scam eroded public trust. Strong ethical foundation creates responsive, citizen-centric administration that serves national interest over personal gain."
    },
    {
        "question": "The impact of digital technology on Indian society is a double-edged sword. Discuss.",
        "word_limit": 250,
        "subject": "GS1",
        "topic": "Society - Social Change",
        "difficulty": "Hard",
        "year": 2023,
        "source": "Custom",
        "keywords": "digital technology, digital divide, information access, social media, cyber security, digital india, financial inclusion, online education",
        "model_answer": "Digital technology has revolutionized Indian society, bringing unprecedented opportunities while creating new challenges. On the positive side, digital India initiatives have enhanced governance through e-governance portals, reducing corruption and improving service delivery. Financial inclusion via UPI and digital payments has empowered millions. Online education platforms democratized learning, especially during COVID-19 pandemic. E-commerce created employment and market access for small businesses. Telemedicine brought healthcare to remote areas. However, the digital divide persists - only 40% rural households have internet access versus 80% urban. This exacerbates inequality in education, employment, and opportunities. Social media has created echo chambers, spread misinformation, and fueled polarization. Cyber security threats, data privacy concerns, and digital surveillance raise questions about individual freedoms. Job displacement due to automation affects traditional sectors. Youth addiction to screens impacts mental health. Screen time during pandemic affected children's physical development. To harness technology's benefits while mitigating risks, India needs: robust data protection laws, universal digital literacy programs, bridging digital divide through infrastructure investment, and promoting responsible technology use. The goal should be inclusive digital growth that leaves no one behind."
    },
    {
        "question": "Examine the role of judiciary in protecting fundamental rights in India.",
        "word_limit": 150,
        "subject": "GS2",
        "topic": "Polity - Judiciary",
        "difficulty": "Medium",
        "year": 2020,
        "source": "PYQ",
        "keywords": "judiciary, fundamental rights, judicial review, Article 32, PIL, judicial activism, supreme court, constitutional remedies",
        "model_answer": "The Indian judiciary serves as the guardian of fundamental rights through constitutional mechanisms. Article 32 empowers Supreme Court to issue writs for enforcement of rights, making it the 'soul' of Constitution as per Dr. Ambedkar. Judicial review allows courts to strike down unconstitutional laws. Public Interest Litigation (PIL) democratized justice, enabling citizens to approach courts for collective rights. Landmark judgments like Maneka Gandhi expanded the scope of Article 21 to include right to live with dignity. The judiciary protected privacy rights in Puttaswamy judgment. However, judicial overreach sometimes blurs separation of powers. Pendency of cases and accessibility issues limit effectiveness. Nevertheless, an independent and active judiciary remains crucial for protecting constitutional rights against executive and legislative excesses, ensuring democratic values thrive."
    }
]

for prompt in sample_prompts:
    cursor.execute('''
        INSERT INTO answer_writing_prompts 
        (question, word_limit, subject, topic, difficulty, year, source, keywords, model_answer)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        prompt['question'],
        prompt['word_limit'],
        prompt['subject'],
        prompt['topic'],
        prompt['difficulty'],
        prompt.get('year'),
        prompt['source'],
        prompt['keywords'],
        prompt.get('model_answer', '')
    ))

conn.commit()
print(f"✅ Seeded {len(sample_prompts)} sample prompts!")

# Show summary
cursor.execute('SELECT COUNT(*) FROM answer_writing_prompts')
prompt_count = cursor.fetchone()[0]
print(f"\n📊 Total prompts in database: {prompt_count}")

conn.close()
print("\n🎉 Migration completed successfully!")
print("You can now use the Answer Writing Practice feature!")
