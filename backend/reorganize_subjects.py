"""
Reorganize PYQ subjects and topics to proper UPSC structure
Maps granular subjects to main UPSC categories
"""

import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'upsc_saga.db')

# Mapping of current subjects to proper UPSC subject categories
SUBJECT_MAPPING = {
    # Polity & Governance
    'Polity': 'Polity & Governance',
    'Constitutional Law': 'Polity & Governance',
    'Parliament': 'Polity & Governance',
    'Parliamentary Procedure': 'Polity & Governance',
    'Governance': 'Polity & Governance',
    'Government': 'Polity & Governance',
    'Administration': 'Polity & Governance',
    'Elections': 'Polity & Governance',
    'Electoral Law': 'Polity & Governance',
    'Law': 'Polity & Governance',
    'Political Science': 'Polity & Governance',
    'Political Theory': 'Polity & Governance',
    'Political Philosophy': 'Polity & Governance',
    'Regulation': 'Polity & Governance',
    
    # Economy
    'Economy': 'Economy',
    'Economics': 'Economy',
    'Banking': 'Economy',
    'Finance': 'Economy',
    'Budget': 'Economy',
    'Taxation': 'Economy',
    'Trade': 'Economy',
    'Trade Policy': 'Economy',
    'International Trade': 'Economy',
    'International Economics': 'Economy',
    'International Finance': 'Economy',
    'Monetary Policy': 'Economy',
    'Employment': 'Economy',
    'International Labor': 'Economy',
    'Mining': 'Economy',
    'Intellectual Property': 'Economy',
    'Skill Development': 'Economy',
    
    # Environment & Ecology
    'Environment': 'Environment & Ecology',
    'Environmental Science': 'Environment & Ecology',
    'Ecology': 'Environment & Ecology',
    'Conservation': 'Environment & Ecology',
    'Wildlife': 'Environment & Ecology',
    'Forests': 'Environment & Ecology',
    'Pollution': 'Environment & Ecology',
    'Climate': 'Environment & Ecology',
    'Carbon Cycle': 'Environment & Ecology',
    'Soil': 'Environment & Ecology',
    'Marine Life': 'Environment & Ecology',
    'Marine Biology': 'Environment & Ecology',
    'Ornithology': 'Environment & Ecology',
    
    # Science & Technology
    'Science': 'Science & Technology',
    'Science & Technology': 'Science & Technology',
    'Science and Technology': 'Science & Technology',
    'Technology': 'Science & Technology',
    'Biotechnology': 'Science & Technology',
    'Nanotechnology': 'Science & Technology',
    'Space': 'Science & Technology',
    'Space Technology': 'Science & Technology',
    'Space Exploration': 'Science & Technology',
    'Astronomy': 'Science & Technology',
    'Energy': 'Science & Technology',
    'Cyber Security': 'Science & Technology',
    'Digital Identity': 'Science & Technology',
    'Remote Sensing': 'Science & Technology',
    'Defence': 'Science & Technology',
    'Defense': 'Science & Technology',
    
    # History & Culture
    'History': 'History & Culture',
    'Culture': 'History & Culture',
    'Architecture': 'History & Culture',
    'Art': 'History & Culture',
    'Arts': 'History & Culture',
    'Dance': 'History & Culture',
    'Martial Arts': 'History & Culture',
    'Religion': 'History & Culture',
    'Buddhism': 'History & Culture',
    'Philosophy': 'History & Culture',
    'Languages': 'History & Culture',
    'Calendar': 'History & Culture',
    'National Symbols': 'History & Culture',
    'Colonial History': 'History & Culture',
    'Independence Movement': 'History & Culture',
    'Labour History': 'History & Culture',
    'Social History': 'History & Culture',
    'Archaeology': 'History & Culture',
    
    # Geography
    'Geography': 'Geography',
    
    # Agriculture
    'Agriculture': 'Agriculture',
    'Food Security': 'Agriculture',
    'Food Safety': 'Agriculture',
    
    # Biology & Life Sciences
    'Biology': 'Biology',
    'Botany': 'Biology',
    'Evolution': 'Biology',
    
    # Chemistry
    'Chemistry': 'Chemistry',
    
    # Social Issues
    'Social': 'Social Issues',
    'Social Welfare': 'Social Issues',
    'Social Security': 'Social Issues',
    'Health': 'Social Issues',
    'Medicine': 'Social Issues',
    'Nutrition': 'Social Issues',
    'Education': 'Social Issues',
    'Higher Education': 'Social Issues',
    'Indigenous Communities': 'Social Issues',
    
    # Current Affairs & International Relations
    'Current Affairs': 'Current Affairs',
    'International Relations': 'International Relations',
    'International Organization': 'International Relations',
    'International Organizations': 'International Relations',
    'UN Agencies': 'International Relations',
    'Global': 'International Relations',
    
    # Government Schemes & Initiatives
    'Government Schemes': 'Government Schemes',
    'Infrastructure': 'Government Schemes',
    'Urban Development': 'Government Schemes',
    'Planning': 'Government Schemes',
    
    # Miscellaneous
    'Sports': 'Sports',
    'Sports & Awards': 'Sports',
    'Awards': 'Sports',
    'Media': 'Media',
    'Standards': 'Standards',
    'Facilities': 'Facilities',
    'Regional Products': 'Regional Products',
}

def reorganize_subjects():
    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\nFetching all questions...")
    cursor.execute('SELECT id, subject, topic FROM pyq_questions')
    questions = cursor.fetchall()
    
    print(f"Found {len(questions)} questions to reorganize\n")
    
    updated = 0
    unmapped = set()
    
    for id, old_subject, old_topic in questions:
        # Get new subject from mapping
        new_subject = SUBJECT_MAPPING.get(old_subject)
        
        if not new_subject:
            unmapped.add(old_subject)
            continue
        
        # If subject changed, make old subject the topic (if topic was empty or same as subject)
        if new_subject != old_subject:
            # If topic is None, empty, or same as subject, use old subject as topic
            if not old_topic or old_topic == old_subject:
                new_topic = old_subject
            else:
                # Keep existing topic
                new_topic = old_topic
            
            cursor.execute('''
                UPDATE pyq_questions 
                SET subject = ?, topic = ?
                WHERE id = ?
            ''', (new_subject, new_topic, id))
            
            updated += 1
            
            if updated % 100 == 0:
                print(f"  Updated {updated} questions...")
    
    conn.commit()
    
    # Get new stats
    cursor.execute('SELECT COUNT(DISTINCT subject) FROM pyq_questions')
    new_subject_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT DISTINCT subject FROM pyq_questions ORDER BY subject')
    new_subjects = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    print("\n" + "="*60)
    print("REORGANIZATION COMPLETE")
    print("="*60)
    print(f"\nQuestions updated: {updated}")
    print(f"Previous subject count: 112")
    print(f"New subject count: {new_subject_count}")
    
    if unmapped:
        print(f"\nUnmapped subjects ({len(unmapped)}):")
        for subj in sorted(unmapped):
            print(f"  - {subj}")
    
    print("\nNew subject categories:")
    for subj in new_subjects:
        print(f"  - {subj}")
    
    print("\n✓ Database reorganized successfully!")

if __name__ == '__main__':
    reorganize_subjects()
