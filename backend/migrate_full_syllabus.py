import sqlite3
import json

DB_PATH = 'backend/upsc_saga.db'

FULL_SYLLABUS = [
    # --- GS 1 ---
    {"paper": "GS1", "subject": "Art & Culture", "topics": [
        "Indian Culture - Salient aspects of Art Forms",
        "Literature and Architecture from ancient to modern times"
    ]},
    {"paper": "GS1", "subject": "Modern History", "topics": [
        "Modern Indian history from about the middle of the eighteenth century until the present- significant events, personalities, issues",
        "The Freedom Struggle — its various stages and important contributors/contributions from different parts of the country",
        "Post-independence consolidation and reorganization within the country"
    ]},
    {"paper": "GS1", "subject": "World History", "topics": [
        "History of the world will include events from 18th century such as industrial revolution",
        "World wars",
        "Redrawal of national boundaries",
        "Colonization",
        "Decolonization",
        "Political philosophies like communism, capitalism, socialism etc.— their forms and effect on the society"
    ]},
    {"paper": "GS1", "subject": "Society", "topics": [
        "Salient features of Indian Society, Diversity of India",
        "Role of women and women’s organization",
        "Population and associated issues",
        "Poverty and developmental issues",
        "Urbanization, their problems and their remedies",
        "Effects of globalization on Indian society",
        "Social empowerment",
        "Communalism, regionalism & secularism"
    ]},
    {"paper": "GS1", "subject": "Geography", "topics": [
        "Salient features of world’s physical geography",
        "Distribution of key natural resources across the world (including South Asia and the Indian sub-continent)",
        "Factors responsible for the location of primary, secondary, and tertiary sector industries in various parts of the world (including India)",
        "Important Geophysical phenomena such as earthquakes, Tsunami, Volcanic activity, cyclone etc.",
        "Geographical features and their location-changes in critical geographical features (including water-bodies and ice-caps) and in flora and fauna and the effects of such changes"
    ]},

    # --- GS 2 ---
    {"paper": "GS2", "subject": "Polity", "topics": [
        "Indian Constitution—historical underpinnings, evolution, features, amendments, significant provisions and basic structure",
        "Functions and responsibilities of the Union and the States",
        "Issues and challenges pertaining to the federal structure",
        "Devolution of powers and finances up to local levels and challenges therein",
        "Separation of powers between various organs dispute redressal mechanisms and institutions",
        "Comparison of the Indian constitutional scheme with that of other countries",
        "Parliament and State legislatures—structure, functioning, conduct of business, powers & privileges and issues arising out of these",
        "Structure, organization and functioning of the Executive and the Judiciary",
        "Ministries and Departments of the Government",
        "Pressure groups and formal/informal associations and their role in the Polity",
        "Salient features of the Representation of People’s Act",
        "Appointment to various Constitutional posts, powers, functions and responsibilities of various Constitutional Bodies",
        "Statutory, regulatory and various quasi-judicial bodies"
    ]},
    {"paper": "GS2", "subject": "Governance", "topics": [
        "Government policies and interventions for development in various sectors and issues arising out of their implementation",
        "Development processes and the development industry — the role of NGOs, SHGs, various groups and associations, donors, charities, institutional and other stakeholders",
        "Welfare schemes for vulnerable sections of the population by the Centre and States and the performance of these schemes",
        "Mechanisms, laws, institutions and Bodies constituted for the protection and betterment of these vulnerable sections",
        "Issues relating to development and management of Social Sector/Services relating to Health, Education, Human Resources",
        "Issues relating to poverty and hunger",
        "Important aspects of governance, transparency and accountability",
        "E-governance- applications, models, successes, limitations, and potential",
        "Citizens charters, transparency & accountability and institutional and other measures",
        "Role of civil services in a democracy"
    ]},
    {"paper": "GS2", "subject": "International Relations", "topics": [
        "India and its neighborhood- relations",
        "Bilateral, regional and global groupings and agreements involving India and/or affecting India’s interests",
        "Effect of policies and politics of developed and developing countries on India’s interests",
        "Indian diaspora",
        "Important International institutions, agencies and fora- their structure, mandate"
    ]},

    # --- GS 3 ---
    {"paper": "GS3", "subject": "Economy", "topics": [
        "Indian Economy and issues relating to planning, mobilization, of resources, growth, development and employment",
        "Inclusive growth and issues arising from it",
        "Government Budgeting",
        "Major crops-cropping patterns in various parts of the country",
        "Different types of irrigation and irrigation systems storage",
        "Transport and marketing of agricultural produce and issues and related constraints",
        "E-technology in the aid of farmers",
        "Issues related to direct and indirect farm subsidies and minimum support prices",
        "Public Distribution System- objectives, functioning, limitations, revamping",
        "Issues of buffer stocks and food security",
        "Technology missions",
        "Economics of animal-rearing",
        "Food processing and related industries in India- scope and significance, location, upstream and downstream requirements, supply chain management",
        "Land reforms in India",
        "Effects of liberalization on the economy",
        "Changes in industrial policy and their effects on industrial growth",
        "Infrastructure: Energy, Ports, Roads, Airports, Railways etc.",
        "Investment models"
    ]},
    {"paper": "GS3", "subject": "Science & Tech", "topics": [
        "Science and Technology- developments and their applications and effects in everyday life",
        "Achievements of Indians in science & technology",
        "Indigenization of technology and developing new technology",
        "Awareness in the fields of IT, Space, Computers, robotics, nano-technology, bio-technology",
        "Issues relating to intellectual property rights"
    ]},
    {"paper": "GS3", "subject": "Environment", "topics": [
        "Conservation, environmental pollution and degradation, environmental impact assessment"
    ]},
    {"paper": "GS3", "subject": "Disaster Management", "topics": [
        "Disaster and disaster management"
    ]},
    {"paper": "GS3", "subject": "Security", "topics": [
        "Linkages between development and spread of extremism",
        "Role of external state and non-state actors in creating challenges to internal security",
        "Challenges to internal security through communication networks",
        "Role of media and social networking sites in internal security challenges",
        "Basics of cyber security",
        "Money-laundering and its prevention",
        "Security challenges and their management in border areas - linkages of organized crime with terrorism",
        "Various Security forces and agencies and their mandate"
    ]},

    # --- GS 4 ---
    {"paper": "GS4", "subject": "Ethics", "topics": [
        "Ethics and Human Interface: Essence, determinants and consequences of Ethics in-human actions",
        "Dimensions of ethics",
        "Ethics in private and public relationships",
        "Human Values - lessons from the lives and teachings of great leaders, reformers and administrators",
        "Role of family society and educational institutions in inculcating values",
        "Attitude: content, structure, function; its influence and relation with thought and behaviour",
        "Moral and political attitudes",
        "Social influence and persuasion",
        "Aptitude and foundational values for Civil Service",
        "Integrity, impartiality and non-partisanship, objectivity, dedication to public service, empathy, tolerance and compassion towards the weaker-sections",
        "Emotional intelligence-concepts, and their utilities and application in administration and governance",
        "Contributions of moral thinkers and philosophers from India and world",
        "Public/Civil service values and Ethics in Public administration: Status and problems",
        "Ethical concerns and dilemmas in government and private institutions",
        "Laws, rules, regulations and conscience as sources of ethical guidance",
        "Accountability and ethical governance",
        "Strengthening of ethical and moral values in governance",
        "Ethical issues in international relations and funding",
        "Corporate governance",
        "Probity in Governance: Concept of public service",
        "Philosophical basis of governance and probity",
        "Information sharing and transparency in government",
        "Right to Information",
        "Codes of Ethics",
        "Codes of Conduct",
        "Citizen’s Charters",
        "Work culture",
        "Quality of service delivery",
        "Utilization of public funds",
        "Challenges of corruption",
        "Case Studies on above issues"
    ]},


    # --- Prelims ---
    {"paper": "Prelims", "subject": "History", "topics": [
        "History of India and Indian National Movement"
    ]},
    {"paper": "Prelims", "subject": "Geography", "topics": [
        "Indian and World Geography - Physical, Social, Economic Geography of India and the World"
    ]},
    {"paper": "Prelims", "subject": "Polity", "topics": [
        "Indian Polity and Governance - Constitution, Political System, Panchayati Raj, Public Policy, Rights Issues, etc."
    ]},
    {"paper": "Prelims", "subject": "Economy", "topics": [
        "Economic and Social Development - Sustainable Development, Poverty, Inclusion, Demographics, Social Sector Initiatives, etc."
    ]},
    {"paper": "Prelims", "subject": "Environment", "topics": [
        "General issues on Environmental ecology, Bio-diversity and Climate Change - that do not require subject specialization"
    ]},
    {"paper": "Prelims", "subject": "General Science", "topics": [
        "General Science"
    ]},
    {"paper": "Prelims", "subject": "Current Events", "topics": [
        "Current events of national and international importance"
    ]},

    # --- Optional (Generic Placeholder) ---
    {"paper": "Optional", "subject": "Paper 1", "topics": [
        "Topic 1", "Topic 2", "Topic 3", "Topic 4", "Topic 5"
    ]},
    {"paper": "Optional", "subject": "Paper 2", "topics": [
        "Topic 1", "Topic 2", "Topic 3", "Topic 4", "Topic 5"
    ]}
]

def migrate_syllabus():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Clearing existing syllabus topics...")
    cursor.execute("DELETE FROM syllabus_topics")
    
    print("Inserting full syllabus...")
    count = 0
    for item in FULL_SYLLABUS:
        paper = item['paper']
        subject = item['subject']
        for topic in item['topics']:
            cursor.execute('''
                INSERT INTO syllabus_topics (paper, subject, topic, status, last_updated)
                VALUES (?, ?, ?, 'Not Started', CURRENT_TIMESTAMP)
            ''', (paper, subject, topic))
            count += 1
            
    conn.commit()
    conn.close()
    print(f"Successfully inserted {count} topics.")

if __name__ == "__main__":
    migrate_syllabus()
