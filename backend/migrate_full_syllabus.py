import sqlite3
import os
import json

# Correctly pointing to the root backend folder
db_path = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

def seed_full_syllabus():
    """
    Clears the existing syllabus and seeds it with a comprehensive,
    multi-level UPSC syllabus for all GS papers.
    """
    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Create table if it doesn't exist
    print("Ensuring syllabus_topics table exists...")
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
    print("Table exists.")

    # 2. Clear existing data
    print("Clearing existing data from syllabus_topics...")
    cursor.execute("DELETE FROM syllabus_topics")
    conn.commit()
    print("Data cleared successfully.")

    # 2. Define the new, comprehensive syllabus structure
    syllabus_data = {
        'GS1': {
            'Indian Heritage and Culture': {
                'Indian Culture': [
                    'Salient aspects of Art Forms, Literature and Architecture from ancient to modern times.'
                ]
            },
            'Modern Indian History': {
                'Mid-18th Century to Present': [
                    'Significant events, personalities, issues.'
                ],
                'The Freedom Struggle': [
                    'Its various stages and important contributors/contributions from different parts of the country.'
                ],
                'Post-independence Consolidation': [
                    'Consolidation and reorganization within the country.'
                ]
            },
            'History of the World': {
                '18th Century Events': [
                    'Industrial revolution, world wars, redrawal of national boundaries, colonization, decolonization.'
                ],
                'Political Philosophies': [
                    'Communism, capitalism, socialism etc. - their forms and effect on society.'
                ]
            },
            'Indian Society': {
                'Salient Features': [
                    'Diversity of India.'
                ],
                'Role of Women & Population Issues': [
                    'Role of women and women’s organization, population and associated issues, poverty and developmental issues, urbanization, their problems and their remedies.'
                ],
                'Globalization': [
                    'Effects of globalization on Indian society.'
                ],
                'Social Empowerment': [
                    'Communalism, regionalism & secularism.'
                ]
            },
            'Geography': {
                'World Physical Geography': [
                    'Salient features of world’s physical geography.'
                ],
                'Natural Resources': [
                    'Distribution of key natural resources across the world (including South Asia and the Indian sub-continent); factors responsible for the location of primary, secondary, and tertiary sector industries in various parts of the world (including India).'
                ],
                'Geophysical Phenomena': [
                    'Important Geophysical phenomena such as earthquakes, Tsunami, Volcanic activity, cyclone etc., geographical features and their location- changes in critical geographical features (including water-bodies and ice-caps) and in flora and fauna and the effects of such changes.'
                ]
            }
        },
        'GS2': {
            'Governance, Constitution, Polity': {
                'Indian Constitution': [
                    'Historical underpinnings, evolution, features, amendments, significant provisions and basic structure.'
                ],
                'Functions and Responsibilities': [
                    'Functions and responsibilities of the Union and the States, issues and challenges pertaining to the federal structure, devolution of powers and finances up to local levels and challenges therein.'
                ],
                'Separation of Powers': [
                    'Separation of powers between various organs dispute redressal mechanisms and institutions.'
                ],
                'Comparison with Other Constitutions': [
                    'Comparison of the Indian constitutional scheme with that of other countries.'
                ],
                'Parliament and State Legislatures': [
                    'Structure, functioning, conduct of business, powers & privileges and issues arising out of these.'
                ],
                'Executive and Judiciary': [
                    'Structure, organization and functioning of the Executive and the Judiciary—Ministries and Departments of the Government; pressure groups and formal/informal associations and their role in the Polity.'
                ],
                'Representation of People\'s Act': [
                    'Salient features of the Representation of People’s Act.'
                ],
                'Constitutional Posts': [
                    'Appointment to various Constitutional posts, powers, functions and responsibilities of various Constitutional Bodies.'
                ],
                'Statutory and Regulatory Bodies': [
                    'Statutory, regulatory and various quasi-judicial bodies.'
                ]
            },
            'Social Justice': {
                'Government Policies and Interventions': [
                    'Government policies and interventions for development in various sectors and issues arising out of their design and implementation.'
                ],
                'Development Processes': [
                    'Development processes and the development industry —the role of NGOs, SHGs, various groups and associations, donors, charities, institutional and other stakeholders.'
                ],
                'Vulnerable Sections': [
                    'Welfare schemes for vulnerable sections of the population by the Centre and States and the performance of these schemes; mechanisms, laws, institutions and Bodies constituted for the protection and betterment of these vulnerable sections.'
                ],
                'Social Sector/Services': [
                    'Issues relating to development and management of Social Sector/Services relating to Health, Education, Human Resources.'
                ],
                'Poverty and Hunger': [
                    'Issues relating to poverty and hunger.'
                ]
            },
            'International Relations': {
                'India and its Neighborhood': [
                    'Relations.'
                ],
                'Bilateral and Global Groupings': [
                    'Bilateral, regional and global groupings and agreements involving India and/or affecting India’s interests.'
                ],
                'Policies of Other Countries': [
                    'Effect of policies and politics of developed and developing countries on India’s interests, Indian diaspora.'
                ],
                'Important International Institutions': [
                    'Important International institutions, agencies and fora, their structure, mandate.'
                ]
            }
        },
        'GS3': {
            'Economic Development': {
                'Indian Economy': [
                    'Issues relating to planning, mobilization of resources, growth, development and employment.'
                ],
                'Inclusive Growth': [
                    'Inclusive growth and issues arising from it.'
                ],
                'Government Budgeting': [],
                'Cropping Patterns': [
                    'Major crops cropping patterns in various parts of the country, different types of irrigation and irrigation systems storage, transport and marketing of agricultural produce and issues and related constraints; e-technology in the aid of farmers.'
                ],
                'Farm Subsidies and MSP': [
                    'Issues related to direct and indirect farm subsidies and minimum support prices; Public Distribution System- objectives, functioning, limitations, revamping; issues of buffer stocks and food security; Technology missions; economics of animal-rearing.'
                ],
                'Food Processing': [
                    'Food processing and related industries in India- scope and significance, location, upstream and downstream requirements, supply chain management.'
                ],
                'Land Reforms': [
                    'Land reforms in India.'
                ],
                'Liberalization': [
                    'Effects of liberalization on the economy, changes in industrial policy and their effects on industrial growth.'
                ],
                'Infrastructure': [
                    'Energy, Ports, Roads, Airports, Railways etc.'
                ],
                'Investment Models': []
            },
            'Technology': {
                'Science & Technology': [
                    'Developments and their applications and effects in everyday life.'
                ],
                'Achievements of Indians': [
                    'Achievements of Indians in science & technology; indigenization of technology and developing new technology.'
                ],
                'IT, Space, Computers, Robotics': [
                    'Awareness in the fields of IT, Space, Computers, robotics, nano-technology, bio-technology and issues relating to intellectual property rights.'
                ]
            },
            'Biodiversity and Environment': {
                'Conservation': [
                    'Conservation, environmental pollution and degradation, environmental impact assessment.'
                ]
            },
            'Security and Disaster Management': {
                'Disaster Management': [],
                'Extremism': [
                    'Linkages between development and spread of extremism.'
                ],
                'Internal Security Challenges': [
                    'Role of external state and non-state actors in creating challenges to internal security. Challenges to internal security through communication networks, role of media and social networking sites in internal security challenges, basics of cyber security; money-laundering and its prevention.'
                ],
                'Border Areas Security': [
                    'Security challenges and their management in border areas; linkages of organized crime with terrorism.'
                ],
                'Security Forces': [
                    'Various Security forces and agencies and their mandate.'
                ]
            }
        },
        'GS4': {
            'Ethics, Integrity and Aptitude': {
                'Ethics and Human Interface': [
                    'Essence, determinants and consequences of Ethics in human actions; dimensions of ethics; ethics in private and public relationships. Human Values – lessons from the lives and teachings of great leaders, reformers and administrators; role of family, society and educational institutions in inculcating values.'
                ],
                'Attitude': [
                    'Content, structure, function; its influence and relation with thought and behaviour; moral and political attitudes; social influence and persuasion.'
                ],
                'Aptitude and Foundational Values': [
                    'Aptitude and foundational values for Civil Service, integrity, impartiality and non-partisanship, objectivity, dedication to public service, empathy, tolerance and compassion towards the weaker sections.'
                ],
                'Emotional Intelligence': [
                    'Concepts, and their utilities and application in administration and governance.'
                ],
                'Moral Thinkers': [
                    'Contributions of moral thinkers and philosophers from India and world.'
                ],
                'Public/Civil Service Values': [
                    'Public/Civil service values and Ethics in Public administration: Status and problems; ethical concerns and dilemmas in government and private institutions; laws, rules, regulations and conscience as sources of ethical guidance; accountability and ethical governance; strengthening of ethical and moral values in governance; ethical issues in international relations and funding; corporate governance.'
                ],
                'Probity in Governance': [
                    'Concept of public service; Philosophical basis of governance and probity; Information sharing and transparency in government, Right to Information, Codes of Ethics, Codes of Conduct, Citizen’s Charters, Work culture, Quality of service delivery, Utilization of public funds, challenges of corruption.'
                ],
                'Case Studies': [
                    'Case Studies on above issues.'
                ]
            }
        }
    }

    # 3. Flatten and Insert Data
    rows_to_insert = []
    for paper, subjects in syllabus_data.items():
        for subject, topics in subjects.items():
            for topic, subtopics in topics.items():
                if subtopics:
                    for subtopic in subtopics:
                        rows_to_insert.append((paper, subject, topic, subtopic, 'Not Started'))
                else:
                    # If there are no subtopics, insert the topic itself as a main entry
                    rows_to_insert.append((paper, subject, topic, None, 'Not Started'))

    print(f"Prepared {len(rows_to_insert)} new syllabus entries for insertion.")

    cursor.executemany('''
        INSERT INTO syllabus_topics (paper, subject, topic, subtopic, status)
        VALUES (?, ?, ?, ?, ?)
    ''', rows_to_insert)

    print("New syllabus data seeded successfully.")

    conn.commit()
    conn.close()
    print("Syllabus seeding mission completed!")


if __name__ == '__main__':
    seed_full_syllabus()

