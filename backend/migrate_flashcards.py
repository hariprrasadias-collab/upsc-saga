import sqlite3
import os
import json
from datetime import datetime, timedelta

# Database path - use the main database in backend root
db_path = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def migrate_flashcards():
    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Create Decks Table
    print("Creating decks table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS decks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 1,
            name TEXT NOT NULL,
            description TEXT,
            subject TEXT,
            color TEXT DEFAULT '#3498db',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # 2. Create Flashcards Table
    print("Creating flashcards table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id INTEGER NOT NULL,
            front TEXT NOT NULL,
            back TEXT NOT NULL,
            card_type TEXT DEFAULT 'basic',
            source TEXT DEFAULT 'manual',
            source_id INTEGER,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (deck_id) REFERENCES decks (id) ON DELETE CASCADE
        )
    ''')

    # 3. Create Review Sessions Table
    print("Creating review_sessions table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS review_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flashcard_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL DEFAULT 1,
            rating INTEGER NOT NULL,
            time_taken INTEGER DEFAULT 0,
            halflife REAL NOT NULL,
            alpha REAL NOT NULL,
            beta REAL NOT NULL,
            next_review TIMESTAMP,
            reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (flashcard_id) REFERENCES flashcards (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Check if we need to seed data
    cursor.execute('SELECT COUNT(*) FROM decks')
    deck_count = cursor.fetchone()[0]
    
    if deck_count == 0:
        print("Seeding sample decks and flashcards...")
        
        # Create sample decks
        decks_data = [
            ('Indian History - Ancient', 'Ancient Indian civilization and empires', 'GS1', '#e74c3c'),
            ('Indian History - Medieval', 'Medieval Indian history', 'GS1', '#9b59b6'),
            ('Indian Polity', 'Constitutional framework and governance', 'GS2', '#3498db'),
            ('Indian Economy', 'Economic development and planning', 'GS3', '#2ecc71'),
            ('Environment & Ecology', 'Environmental conservation and biodiversity', 'GS3', '#1abc9c'),
            ('General Science', 'Physics, Chemistry, Biology basics', 'Prelims', '#f39c12'),
        ]
        
        deck_ids = {}
        for name, desc, subject, color in decks_data:
            cursor.execute(
                'INSERT INTO decks (name, description, subject, color) VALUES (?, ?, ?, ?)',
                (name, desc, subject, color)
            )
            deck_ids[subject] = cursor.lastrowid
        
        # Sample flashcards - GS1 Ancient History
        ancient_cards = [
            ('Who was the founder of the Mauryan Empire?', 'Chandragupta Maurya (322 BCE)'),
            ('What were the main features of Ashoka\'s Dhamma?', 'Non-violence, tolerance, respect for elders, generosity towards monks'),
            ('Name the capital of the Mauryan Empire', 'Pataliputra (modern-day Patna)'),
            ('What is the significance of the Sangam Age?', 'Period of Tamil literary development (300 BCE - 300 CE)'),
            ('Who was Kautilya?', 'Author of Arthashastra, advisor to Chandragupta Maurya'),
            ('What was the Indus Valley Civilization known for?', 'Well-planned cities, drainage systems, standardized weights'),
            ('Name two important Harappan sites', 'Mohenjo-daro and Harappa'),
            ('What does "Vedic Age" refer to?', 'Period of composition of Vedas (1500-500 BCE)'),
        ]
        
        # GS1 Medieval History
        medieval_cards = [
            ('Who founded the Delhi Sultanate?', 'Qutb-ud-din Aibak (1206)'),
            ('What was the Bhakti Movement?', 'Devotional movement emphasizing personal devotion over rituals'),
            ('Name three important Mughal emperors', 'Akbar, Jahangir, Shah Jahan, Aurangzeb'),
            ('What was Akbar\'s Din-i-Ilahi?', 'Syncretic religion combining elements of Islam, Hinduism, Jainism'),
            ('Who built the Taj Mahal?', 'Emperor Shah Jahan (1632-1653)'),
        ]
        
        # GS2 Polity
        polity_cards = [
            ('How many fundamental rights are there in the Indian Constitution?', 'Six (Right to Equality, Freedom, Against Exploitation, Freedom of Religion, Cultural and Educational Rights, Constitutional Remedies)'),
            ('What is Article 21?', 'Right to Life and Personal Liberty'),
            ('Who is the Chairman of Rajya Sabha?', 'Vice President of India'),
            ('What is the term of Lok Sabha?', '5 years (unless dissolved earlier)'),
            ('What is Article 356?', 'President\'s Rule (State Emergency)'),
            ('Name the original jurisdiction of Supreme Court', 'Disputes between Centre and States, Interstate disputes'),
            ('What is Article 370?', 'Special status to Jammu & Kashmir (repealed in 2019)'),
            ('How many schedules are there in the Constitution?', '12 Schedules'),
        ]
        
        # GS3 Economy
        economy_cards = [
            ('What is GDP?', 'Gross Domestic Product - total value of goods and services produced in a country'),
            ('What is the difference between Fiscal Policy and Monetary Policy?', 'Fiscal: Government spending/taxation. Monetary: Money supply/interest rates by RBI'),
            ('What is the repo rate?', 'Rate at which RBI lends to commercial banks'),
            ('What is NITI Aayog?', 'National Institution for Transforming India (replaced Planning Commission)'),
            ('What is GST?', 'Goods and Services Tax - unified indirect tax'),
            ('What is FDI?', 'Foreign Direct Investment - investment from foreign entities in Indian companies'),
        ]
        
        # GS3 Environment
        env_cards = [
            ('What is biodiversity hotspot?', 'Region with high species diversity and endemism under threat'),
            ('Name India\'s biodiversity hotspots', 'Western Ghats, Eastern Himalayas, Indo-Burma, Sundaland'),
            ('What is the Paris Agreement?', 'Global climate agreement to limit warming to below 2°C'),
            ('What are Western Disturbances?', 'Extra-tropical storms from Mediterranean bringing winter rain'),
            ('What is REDD+?', 'Reducing Emissions from Deforestation and forest Degradation'),
        ]
        
        # General Science
        science_cards = [
            ('What is Newton\'s First Law?', 'Law of Inertia: Object remains at rest or in motion unless acted upon'),
            ('What is photosynthesis?', 'Process by which plants convert light energy to chemical energy'),
            ('What is the atomic number of Carbon?', '6'),
            ('What are the three states of matter?', 'Solid, Liquid, Gas'),
            ('What is the speed of light?', '3 × 10^8 m/s (approximately 300,000 km/s)'),
        ]
        
        # Insert all cards
        all_cards = [
            (deck_ids['GS1'], ancient_cards),
            (deck_ids['GS1'], medieval_cards[:3]),  # Split medieval between two GS1 decks
            (deck_ids['GS2'], polity_cards),
            (deck_ids['GS3'], economy_cards),
            (deck_ids['GS3'], env_cards),
            (deck_ids['Prelims'], science_cards),
        ]
        
        # Use first GS1 deck for ancient, create second entry for medieval
        cursor.execute(
            'INSERT INTO decks (name, description, subject, color) VALUES (?, ?, ?, ?)',
            ('Indian History - Medieval', 'Medieval Indian history', 'GS1', '#9b59b6')
        )
        medieval_deck_id = cursor.lastrowid
        
        total_cards = 0
        for deck_id, cards in all_cards:
            for front, back in cards:
                cursor.execute(
                    '''INSERT INTO flashcards (deck_id, front, back, card_type, source, tags)
                       VALUES (?, ?, ?, 'basic', 'manual', '[]')''',
                    (deck_id, front, back)
                )
                total_cards += 1
        
        # Add medieval cards to separate deck
        for front, back in medieval_cards:
            cursor.execute(
                '''INSERT INTO flashcards (deck_id, front, back, card_type, source, tags)
                   VALUES (?, ?, ?, 'basic', 'manual', '[]')''',
                (medieval_deck_id, front, back)
            )
            total_cards += 1
        
        print(f"Seeded {total_cards} flashcards across {len(decks_data) + 1} decks.")
    else:
        cursor.execute('SELECT COUNT(*) FROM flashcards')
        card_count = cursor.fetchone()[0]
        print(f"Tables already exist with {deck_count} decks and {card_count} flashcards. Skipping seed.")

    conn.commit()
    conn.close()
    print("Flashcards migration completed successfully!")

if __name__ == '__main__':
    migrate_flashcards()
