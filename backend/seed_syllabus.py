import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'upsc_saga.db')

def seed_syllabus():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f">> Seeding Syllabus Tracker at: {DB_PATH}")

    syllabus_data = [
        ("History", "Modern History", "Revolt of 1857", "Not Started", "High"),
        ("History", "Modern History", "Gandhian Era", "Not Started", "High"),
        ("History", "Ancient History", "Indus Valley Civilization", "Completed", "Medium"),
        ("Polity", "Constitution", "Preamble", "Not Started", "High"),
        ("Polity", "Constitution", "Fundamental Rights", "Not Started", "High"),
        ("Geography", "Physical Geography", "Plate Tectonics", "Not Started", "Medium"),
        ("Economy", "Macroeconomics", "Banking System", "Not Started", "High"),
        ("Environment", "Ecology", "Biodiversity Hotspots", "Not Started", "Medium"),
        ("Science", "Space Technology", "ISRO Missions", "Not Started", "Low"),
        ("History", "Art & Culture", "Temple Architecture", "Not Started", "Medium")
    ]

    try:
        cursor.executemany('''
            INSERT INTO syllabus_tracker (subject, topic, sub_topic, status, priority)
            VALUES (?, ?, ?, ?, ?)
        ''', syllabus_data)
        conn.commit()
        print(f"✅ Seeded {len(syllabus_data)} syllabus items.")
    except Exception as e:
        print(f"!! Error seeding syllabus: {e}")

    conn.close()

if __name__ == "__main__":
    seed_syllabus()
