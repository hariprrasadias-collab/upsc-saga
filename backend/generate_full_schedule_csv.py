import csv
import datetime
from datetime import timedelta
import os

# --- CONFIGURATION ---
START_DATE = datetime.date(2026, 3, 4)
DURATION_DAYS = 730
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public', 'UPSC_Scheduler.csv')

# --- RESOURCES ---
# Phase 1: Foundation (NCERTs) - STRICT ORDER
NCERT_BOOKS = [
    {"subject": "History", "title": "NCERT Cl 6: Our Pasts I", "chapters": ["Ch 1: What, Where, How and When?", "Ch 2: From Hunting–Gathering", "Ch 3: In the Earliest Cities", "Ch 4: What Books and Burials Tell Us", "Ch 5: Kingdoms, Kings and Republic", "Ch 6: New Questions and Ideas", "Ch 7: Ashoka", "Ch 8: Vital Villages", "Ch 9: Traders, Kings", "Ch 10: New Empires", "Ch 11: Buildings, Paintings"]},
    {"subject": "Geography", "title": "NCERT Cl 6: The Earth Our Habitat", "chapters": ["Ch 1: Solar System", "Ch 2: Globe Latitudes", "Ch 3: Motions of Earth", "Ch 4: Maps", "Ch 5: Major Domains", "Ch 6: Major Landforms", "Ch 7: Our Country India", "Ch 8: Climate, Vegetation"]},
    {"subject": "Polity", "title": "NCERT Cl 6: Social & Political Life I", "chapters": ["Ch 1: Diversity", "Ch 2: Discrimination", "Ch 3: Government", "Ch 4: Democratic Govt", "Ch 5: Panchayati Raj", "Ch 6: Rural Admin", "Ch 7: Urban Admin", "Ch 8: Rural Livelihoods", "Ch 9: Urban Livelihoods"]},
    {"subject": "History", "title": "NCERT Cl 7: Our Pasts II", "chapters": ["Ch 1: Tracing Changes", "Ch 2: New Kings", "Ch 3: Delhi Sultans", "Ch 4: Mughal Empire", "Ch 5: Rulers and Buildings", "Ch 6: Towns, Traders", "Ch 7: Tribes, Nomads", "Ch 8: Devotional Paths", "Ch 9: Regional Cultures", "Ch 10: 18th Century Pol Formations"]},
    {"subject": "Geography", "title": "NCERT Cl 7: Our Environment", "chapters": ["Ch 1: Environment", "Ch 2: Inside Our Earth", "Ch 3: Our Changing Earth", "Ch 4: Air", "Ch 5: Water", "Ch 6: Natural Vegetation", "Ch 7: Human Environment", "Ch 8: Human Env Interactions", "Ch 9: Life in Deserts"]},
    {"subject": "Polity", "title": "NCERT Cl 7: Social & Political Life II", "chapters": ["Ch 1: Equality", "Ch 2: Health", "Ch 3: State Govt", "Ch 4: Gender", "Ch 5: Women Change World", "Ch 6: Media", "Ch 7: Advertising", "Ch 8: Markets", "Ch 9: Shirt in Market"]},
    {"subject": "History", "title": "NCERT Cl 8: Our Pasts III", "chapters": ["Ch 1: How, When and Where", "Ch 2: From Trade to Territory", "Ch 3: Ruling the Countryside", "Ch 4: Tribals, Dikus", "Ch 5: When People Rebel", "Ch 6: Weavers, Iron Smelters", "Ch 7: Civilising the Native", "Ch 8: Women, Caste and Reform", "Ch 9: The Making of National Movement", "Ch 10: India After Independence"]},
    {"subject": "Geography", "title": "NCERT Cl 8: Resources and Dev", "chapters": ["Ch 1: Resources", "Ch 2: Land, Soil, Water", "Ch 3: Mineral Power", "Ch 4: Agriculture", "Ch 5: Industries", "Ch 6: Human Resources"]},
    {"subject": "Polity", "title": "NCERT Cl 8: Social & Political Life III", "chapters": ["Ch 1: Constitution", "Ch 2: Secularism", "Ch 3: Parliament", "Ch 4: Laws", "Ch 5: Judiciary", "Ch 6: Criminal Justice", "Ch 7: Marginalisation", "Ch 8: Confronting Marginalisation", "Ch 9: Public Facilities", "Ch 10: Law and Social Justice"]},
    {"subject": "Economy", "title": "NCERT Cl 9: Economics", "chapters": ["Ch 1: Village Palampur", "Ch 2: People as Resource", "Ch 3: Poverty as Challenge", "Ch 4: Food Security"]},
    {"subject": "Polity", "title": "NCERT Cl 9: Democratic Politics I", "chapters": ["Ch 1: What is Democracy", "Ch 2: Constitutional Design", "Ch 3: Electoral Politics", "Ch 4: Working of Institutions", "Ch 5: Democratic Rights"]},
    {"subject": "Economy", "title": "NCERT Cl 10: Understanding Eco Dev", "chapters": ["Ch 1: Development", "Ch 2: Sectors of Indian Economy", "Ch 3: Money and Credit", "Ch 4: Globalisation", "Ch 5: Consumer Rights"]},
    {"subject": "Polity", "title": "NCERT Cl 10: Democratic Politics II", "chapters": ["Ch 1: Power Sharing", "Ch 2: Federalism", "Ch 3: Democracy and Diversity", "Ch 4: Gender, Religion, Caste", "Ch 5: Popular Struggles", "Ch 6: Political Parties", "Ch 7: Outcomes of Democracy"]},
    {"subject": "Economy", "title": "NCERT Cl 11: Indian Eco Dev", "chapters": ["Ch 1: Eve of Independence", "Ch 2: Indian Economy 1950-1990", "Ch 3: Liberalisation, Privatisation", "Ch 4: Poverty", "Ch 5: Human Capital", "Ch 6: Rural Development", "Ch 7: Employment", "Ch 8: Infrastructure", "Ch 9: Environment", "Ch 10: Comp Dev Exp of India/Neighbors"]},
    {"subject": "Polity", "title": "NCERT Cl 11: Constitution at Work", "chapters": ["Ch 1: Constitution Why and How", "Ch 2: Rights in Constitution", "Ch 3: Election and Representation", "Ch 4: Executive", "Ch 5: Legislature", "Ch 6: Judiciary", "Ch 7: Federalism", "Ch 8: Local Governments", "Ch 9: Constitution as Living Doc"]},
    {"subject": "Polity", "title": "NCERT Cl 11: Political Theory", "chapters": ["Ch 1: Political Theory Intro", "Ch 2: Freedom", "Ch 3: Equality", "Ch 4: Social Justice", "Ch 5: Rights", "Ch 6: Citizenship", "Ch 7: Nationalism", "Ch 8: Secularism", "Ch 9: Peace", "Ch 10: Development"]}
]

# Phase 2: Core Syllabus (Standard Books)
STANDARD_BOOKS = [
    {"subject": "Polity", "title": "Laxmikanth", "chapters": ["Historical Background", "Making of Constitution", "Salient Features", "Preamble", "Union & Territory", "Citizenship", "Fundamental Rights", "DPSP", "Fundamental Duties", "Amendment", "Basic Structure", "Parliamentary System", "Federal System", "Centre-State Relations", "Inter-State Relations", "Emergency Provisions", "President", "Vice-President", "Prime Minister", "Central Council of Ministers", "Parliament", "Supreme Court", "Governor", "Chief Minister", "State Legislature", "High Court", "Panchayati Raj", "Municipalities", "Constitutional Bodies", "Non-Constitutional Bodies"]},
    {"subject": "History", "title": "Spectrum Modern History", "chapters": ["Advent of Europeans", "Expansion of British Power", "Revolt of 1857", "Socio-Religious Reforms", "Struggle Begins 1885-1905", "National Movement 1905-1918", "Mass Nationalism 1919-1939", "Quit India & INA", "Partition & Independence", "India Under British Rule (Eco/Admin)"]},
    {"subject": "Geography", "title": "GC Leong", "chapters": ["Earth's Crust", "Vulcanism", "Weathering & Mass Movement", "Landforms by Running Water", "Landforms by Glaciation", "Arid Landforms", "Limestone & Chalk", "Lakes", "Coastal Landforms", "Islands", "Oceans", "Climate: Hot Wet Equatorial", "Climate: Tropical Monsoon", "Climate: Savanna", "Climate: Desert", "Climate: Mediterranean", "Climate: Steppe", "Climate: China Type", "Climate: British Type", "Climate: Siberian", "Climate: Laurentian", "Climate: Polar"]},
    {"subject": "Environment", "title": "Shankar IAS", "chapters": ["Ecology", "Functions of Ecosystem", "Terrestrial Ecosystem", "Aquatic Ecosystem", "Env Pollution", "Renewable Energy", "Env Issues", "Env Impact Assessment", "Biodiversity", "Indian Biodiversity", "Animal Diversity", "Plant Diversity", "Marine Organisms", "Protected Areas", "Conservation Efforts", "Climate Change", "Ocean Acidification", "Ozone Depletion", "Mitigation Strategies", "India & Climate Change", "Climate Organizations", "Agriculture", "Acts and Policies", "Institutions"]},
    {"subject": "Art & Culture", "title": "Nitin Singhania", "chapters": ["Indian Architecture", "Temple Architecture", "Cave Architecture", "Indo-Islamic Architecture", "Modern Architecture", "Indian Paintings", "Indian Handicrafts", "UNESCO Sites", "Indian Music", "Indian Dance Forms", "Indian Theatre", "Indian Puppetry", "Indian Circus", "Martial Arts", "Languages in India", "Religion in India", "Buddhism & Jainism", "Indian Literature", "Schools of Philosophy", "Fairs & Festivals", "Awards & Honors"]},
    {"subject": "Economy", "title": "Ramesh Singh / Mrunal", "chapters": ["National Income", "Growth & Development", "Poverty & Unemployment", "Inflation", "Monetary Policy", "Banking System", "Financial Markets", "Fiscal Policy", "Taxation", "Planning in India", "Agriculture", "Industry", "Services", "External Sector", "International Organizations"]}
]

# Phase 3: Mains Mastery
MAINS_TOPICS = [
    {"subject": "Optional", "title": "Optional Paper 1", "chapters": [f"Unit {i}" for i in range(1, 11)]},
    {"subject": "Optional", "title": "Optional Paper 2", "chapters": [f"Unit {i}" for i in range(1, 11)]},
    {"subject": "Ethics", "title": "Lexicon", "chapters": ["Ethics & Human Interface", "Attitude", "Aptitude & Foundational Values", "Emotional Intelligence", "Moral Thinkers", "Public Service Values", "Probity in Governance", "Case Studies"]},
    {"subject": "Essay", "title": "Essay Prep", "chapters": ["Philosophical Essays", "Social Issues Essays", "Economic Essays", "Polity/IR Essays", "Science/Tech Essays", "Abstract Essays"]},
    {"subject": "World History", "title": "Norman Lowe / NCERT", "chapters": ["Industrial Revolution", "American Revolution", "French Revolution", "Unification of Italy/Germany", "World War I", "Russian Revolution", "World War II", "Cold War", "Decolonization"]}
]

# --- GENERATION LOGIC ---

def get_slots(date_obj):
    weekday = date_obj.weekday()
    slots = []
    
    # Weekday (Mon-Fri)
    if weekday < 5:
        slots.append({"type": "Morning", "time": "04:00-07:00", "activity": "Read"})
        slots.append({"type": "Evening", "time": "20:00-23:00", "activity": "Revise"}) # Often overridden by Current Affairs
    # Weekend (Sat-Sun)
    else:
        slots.append({"type": "Weekend_Slot_1", "time": "08:00-11:00", "activity": "Read"})
        slots.append({"type": "Weekend_Slot_2", "time": "12:00-14:00", "activity": "Practice"}) # CSAT/Essay
        slots.append({"type": "Weekend_Slot_3", "time": "15:00-18:00", "activity": "Mock Test"})
        slots.append({"type": "Weekend_Slot_4", "time": "19:00-21:00", "activity": "Revise"})
        
    return slots

def generate_csv():
    current_date = START_DATE
    end_date = START_DATE + timedelta(days=DURATION_DAYS)
    
    # Queues - STRICT ORDERING
    ncert_queue = [(b, c) for b in NCERT_BOOKS for c in b['chapters']]
    standard_queue = [(b, c) for b in STANDARD_BOOKS for c in b['chapters']]
    mains_queue = [(b, c) for b in MAINS_TOPICS for c in b['chapters']]
    
    # State
    srs_queue = [] # {"date": date, "subject": sub, "topic": topic}
    completed_chapters_count = 0
    chapters_since_flashcard = 0
    current_book_title = ""
    
    rows = []
    
    while current_date < end_date:
        day_str = current_date.strftime("%A")
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Determine Phase & Queue
        days_passed = (current_date - START_DATE).days
        
        if ncert_queue:
            phase = "Foundation"
            active_queue = ncert_queue
        elif standard_queue:
            phase = "Core"
            active_queue = standard_queue
        elif mains_queue:
            phase = "Mains"
            active_queue = mains_queue
        else:
            phase = "Prelims"
            active_queue = [] # Revision focus
            
        slots = get_slots(current_date)
        
        # SRS Check
        todays_reviews = [x for x in srs_queue if x['date'] <= current_date]
        srs_queue = [x for x in srs_queue if x['date'] > current_date]
        
        for slot in slots:
            row = {
                "Date": date_str,
                "Day": day_str,
                "Slot_Type": slot['type'],
                "Time": slot['time'],
                "Subject": "",
                "Topic": "",
                "Activity_Type": slot['activity'],
                "Resources": ""
            }
            
            # --- WEEKDAY LOGIC ---
            if slot['type'] == "Morning":
                # Priority: New Study (Morning is for heavy concepts)
                if active_queue:
                    book, chapter = active_queue.pop(0)
                    row["Subject"] = book['subject']
                    row["Topic"] = f"{book['title']} - {chapter}"
                    row["Resources"] = book['title']
                    
                    # Add to SRS
                    srs_queue.append({"date": current_date + timedelta(days=7), "subject": book['subject'], "topic": chapter})
                    srs_queue.append({"date": current_date + timedelta(days=30), "subject": book['subject'], "topic": chapter})
                    
                    completed_chapters_count += 1
                    chapters_since_flashcard += 1
                    
                    if current_book_title != book['title']:
                        current_book_title = book['title']
                else:
                    row["Subject"] = "Revision"
                    row["Topic"] = "General Revision / Backlog"
                    row["Resources"] = "Notes"

            elif slot['type'] == "Evening":
                # Current Affairs (45m) + SRS Revision (2h)
                row["Subject"] = "CA & Revision"
                row["Activity_Type"] = "Revise"
                row["Resources"] = "The Hindu + Notes"
                
                topic_parts = ["Daily News Analysis"]
                
                # Add SRS items (up to 3 per evening)
                reviews_added = 0
                while todays_reviews and reviews_added < 3:
                    review = todays_reviews.pop(0)
                    topic_parts.append(f"Revise: {review['topic']}")
                    reviews_added += 1
                
                # Push remaining back to srs_queue for tomorrow
                if todays_reviews:
                     for rem in todays_reviews:
                         rem['date'] = current_date + timedelta(days=1)
                         srs_queue.append(rem)
                     todays_reviews = []
                
                row["Topic"] = " + ".join(topic_parts)
                
                # Check Flashcard Trigger
                if chapters_since_flashcard >= 10:
                    row["Topic"] += " + CREATE FLASHCARDS (Last 10 Chaps)"
                    chapters_since_flashcard = 0

            # --- WEEKEND LOGIC ---
            elif slot['type'] == "Weekend_Slot_1":
                # Heavy Lift / New Study
                if active_queue:
                    book, chapter = active_queue.pop(0)
                    row["Subject"] = book['subject']
                    row["Topic"] = f"{book['title']} - {chapter}"
                    row["Resources"] = book['title']
                    
                    srs_queue.append({"date": current_date + timedelta(days=7), "subject": book['subject'], "topic": chapter})
                    srs_queue.append({"date": current_date + timedelta(days=30), "subject": book['subject'], "topic": chapter})
                    
                    completed_chapters_count += 1
                    chapters_since_flashcard += 1
                else:
                    row["Subject"] = "Optional"
                    row["Topic"] = "Deep Dive / Revision"
                    row["Resources"] = "Standard Texts"

            elif slot['type'] == "Weekend_Slot_2":
                # CSAT / Essay
                if day_str == "Saturday":
                    row["Subject"] = "CSAT"
                    row["Topic"] = "Maths/Logic Practice"
                    row["Activity_Type"] = "Practice"
                    row["Resources"] = "PYQs / RS Aggarwal"
                else: # Sunday
                    row["Subject"] = "Essay"
                    row["Topic"] = "Weekly Essay Writing"
                    row["Activity_Type"] = "Write"
                    row["Resources"] = "Previous Year Topics"

            elif slot['type'] == "Weekend_Slot_3":
                # Mock Test
                row["Subject"] = "Mock Test"
                row["Topic"] = f"Sectional Test (Based on completed {phase} topics)"
                row["Activity_Type"] = "Mock Test"
                row["Resources"] = "Test Series"

            elif slot['type'] == "Weekend_Slot_4":
                # Weekly Revision
                row["Subject"] = "Revision"
                row["Topic"] = "Weekly Consolidation"
                row["Activity_Type"] = "Revise"
                row["Resources"] = "Self Notes"

            rows.append(row)
            
        current_date += timedelta(days=1)

    # Write CSV
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Date", "Day", "Slot_Type", "Time", "Subject", "Topic", "Activity_Type", "Resources"])
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Successfully generated {OUTPUT_FILE} with {len(rows)} rows.")

if __name__ == "__main__":
    generate_csv()
