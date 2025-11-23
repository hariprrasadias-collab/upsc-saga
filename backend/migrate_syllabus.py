import sqlite3
import os

# Database path - Correctly pointing to root backend folder
db_path = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def migrate_syllabus():
    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create Syllabus Table
    print("Creating syllabus_topics table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS syllabus_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            subtopic TEXT,
            status TEXT DEFAULT 'Not Started',
            notes TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Check if data exists
    cursor.execute('SELECT count(*) FROM syllabus_topics')
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("Seeding UPSC Syllabus data...")
        
        # Structure: Paper -> Subject -> [Topics]
        syllabus_data = {
            'GS1': {
                'Art & Culture': [
                    'Indian culture: Salient aspects of Art Forms',
                    'Literature and Architecture from ancient to modern times'
                ],
                'Modern History': [
                    'Modern Indian history from about the middle of the eighteenth century until the present',
                    'The Freedom Struggle — its various stages',
                    'Important contributors/contributions from different parts of the country'
                ],
                'World History': [
                    'History of the world: Industrial revolution',
                    'World wars',
                    'Redrawal of national boundaries',
                    'Colonization and decolonization',
                    'Political philosophies like communism, capitalism, socialism'
                ],
                'Society': [
                    'Salient features of Indian Society, Diversity of India',
                    'Role of women and women’s organization',
                    'Population and associated issues',
                    'Poverty and developmental issues',
                    'Urbanization, their problems and their remedies',
                    'Effects of globalization on Indian society',
                    'Social empowerment, communalism, regionalism & secularism'
                ],
                'Geography': [
                    'Salient features of world’s physical geography',
                    'Distribution of key natural resources across the world',
                    'Factors responsible for the location of primary, secondary, and tertiary sector industries',
                    'Important Geophysical phenomena such as earthquakes, Tsunami, Volcanic activity, cyclone',
                    'Geographical features and their location-changes in critical geographical features'
                ]
            },
            'GS2': {
                'Polity': [
                    'Indian Constitution—historical underpinnings, evolution, features, amendments',
                    'Functions and responsibilities of the Union and the States',
                    'Separation of powers between various organs',
                    'Comparison of the Indian constitutional scheme with that of other countries',
                    'Parliament and State legislatures—structure, functioning, conduct of business',
                    'Structure, organization and functioning of the Executive and the Judiciary'
                ],
                'Governance': [
                    'Salient features of the Representation of People’s Act',
                    'Appointment to various Constitutional posts, powers, functions',
                    'Statutory, regulatory and various quasi-judicial bodies',
                    'Government policies and interventions for development in various sectors',
                    'Development processes and the development industry (NGOs, SHGs)',
                    'Welfare schemes for vulnerable sections',
                    'Issues relating to development and management of Social Sector/Services (Health, Education, HR)',
                    'Issues relating to poverty and hunger',
                    'Important aspects of governance, transparency and accountability',
                    'E-governance- applications, models, successes, limitations',
                    'Citizens charters, transparency & accountability and institutional and other measures',
                    'Role of civil services in a democracy'
                ],
                'International Relations': [
                    'India and its neighborhood- relations',
                    'Bilateral, regional and global groupings and agreements involving India',
                    'Effect of policies and politics of developed and developing countries on India’s interests',
                    'Important International institutions, agencies and fora'
                ]
            },
            'GS3': {
                'Economy': [
                    'Indian Economy and issues relating to planning, mobilization, of resources, growth, development and employment',
                    'Inclusive growth and issues arising from it',
                    'Government Budgeting',
                    'Major crops-cropping patterns in various parts of the country',
                    'Different types of irrigation and irrigation systems storage',
                    'Transport and marketing of agricultural produce and issues and related constraints',
                    'E-technology in the aid of farmers',
                    'Issues related to direct and indirect farm subsidies and minimum support prices',
                    'Public Distribution System- objectives, functioning, limitations, revamping',
                    'Food processing and related industries in India',
                    'Land reforms in India',
                    'Effects of liberalization on the economy',
                    'Changes in industrial policy and their effects on industrial growth',
                    'Infrastructure: Energy, Ports, Roads, Airports, Railways etc.',
                    'Investment models'
                ],
                'Science & Tech': [
                    'Science and Technology- developments and their applications and effects in everyday life',
                    'Achievements of Indians in science & technology',
                    'Indigenization of technology and developing new technology',
                    'Awareness in the fields of IT, Space, Computers, robotics, nano-technology, bio-technology',
                    'Issues relating to intellectual property rights'
                ],
                'Environment': [
                    'Conservation, environmental pollution and degradation',
                    'Environmental impact assessment'
                ],
                'Disaster Management': [
                    'Disaster and disaster management'
                ],
                'Internal Security': [
                    'Linkages between development and spread of extremism',
                    'Role of external state and non-state actors in creating challenges to internal security',
                    'Challenges to internal security through communication networks',
                    'Role of media and social networking sites in internal security challenges',
                    'Basics of cyber security',
                    'Money-laundering and its prevention',
                    'Security challenges and their management in border areas',
                    'Linkages of organized crime with terrorism',
                    'Various Security forces and agencies and their mandate'
                ]
            },
            'GS4': {
                'Ethics': [
                    'Ethics and Human Interface: Essence, determinants and consequences of Ethics in-human actions',
                    'Dimensions of ethics; Ethics - in private and public relationships',
                    'Human Values - lessons from the lives and teachings of great leaders, reformers and administrators',
                    'Role of family society and educational institutions in inculcating values',
                    'Attitude: content, structure, function; its influence and relation with thought and behaviour',
                    'Moral and political attitudes; social influence and persuasion',
                    'Aptitude and foundational values for Civil Service',
                    'Integrity, impartiality and non-partisanship, objectivity, dedication to public service, empathy, tolerance and compassion',
                    'Emotional intelligence-concepts, and their utilities and application in administration and governance',
                    'Contributions of moral thinkers and philosophers from India and world',
                    'Public/Civil service values and Ethics in Public administration',
                    'Status and problems; ethical concerns and dilemmas in government and private institutions',
                    'Laws, rules, regulations and conscience as sources of ethical guidance',
                    'Accountability and ethical governance',
                    'Strengthening of ethical and moral values in governance',
                    'Probity in Governance: Concept of public service',
                    'Philosophical basis of governance and probity',
                    'Information sharing and transparency in government, Right to Information',
                    'Codes of Ethics, Codes of Conduct, Citizen’s Charters, Work culture, Quality of service delivery',
                    'Utilization of public funds, challenges of corruption',
                    'Case Studies on above issues'
                ]
            }
        }

        # Flatten and Insert
        rows = []
        for paper, subjects in syllabus_data.items():
            for subject, topics in subjects.items():
                for topic in topics:
                    rows.append((paper, subject, topic, None)) # Subtopic is None for now

        cursor.executemany('''
            INSERT INTO syllabus_topics (paper, subject, topic, subtopic)
            VALUES (?, ?, ?, ?)
        ''', rows)
        print(f"Seeded {len(rows)} syllabus topics.")
    else:
        print(f"Table already exists with {count} topics. Skipping seed.")

    conn.commit()
    conn.close()
    print("Syllabus Migration completed successfully!")

if __name__ == '__main__':
    migrate_syllabus()
