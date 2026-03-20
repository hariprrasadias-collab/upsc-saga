import time
from backend.app.db import get_db
from backend.app import create_app

app = create_app()

def old_way(conn):
    years = conn.execute("SELECT DISTINCT year FROM pyq_questions ORDER BY year DESC").fetchall()
    year_bosses = []
    for row in years:
        boss_id = row['year']
        count = conn.execute("SELECT COUNT(*) FROM pyq_questions WHERE year = ?", (boss_id,)).fetchone()[0]
        year_bosses.append({
            "id": boss_id,
            "type": "YEAR",
            "name": f"The {boss_id} Titan",
            "hp": min(count, 20),
            "max_hp": count,
            "xp_reward": min(count, 20) * 50,
            "loot": ["Time Capsule", "Ancient Scroll"]
        })

    subjects = conn.execute("SELECT DISTINCT subject FROM pyq_questions ORDER BY subject").fetchall()
    subject_bosses = []
    for row in subjects:
        boss_id = row['subject']
        count = conn.execute("SELECT COUNT(*) FROM pyq_questions WHERE subject = ?", (boss_id,)).fetchone()[0]
        subject_bosses.append({
            "id": boss_id,
            "type": "SUBJECT",
            "name": f"The {boss_id} Golem",
            "hp": min(count, 20),
            "max_hp": count,
            "xp_reward": min(count, 20) * 50,
            "loot": ["Subject Mastery Token", "Skill Point"]
        })

    return year_bosses, subject_bosses

def new_way(conn):
    years_counts = conn.execute("SELECT year, COUNT(*) as count FROM pyq_questions GROUP BY year ORDER BY year DESC").fetchall()
    year_bosses = [{
        "id": row['year'],
        "type": "YEAR",
        "name": f"The {row['year']} Titan",
        "hp": min(row['count'], 20),
        "max_hp": row['count'],
        "xp_reward": min(row['count'], 20) * 50,
        "loot": ["Time Capsule", "Ancient Scroll"]
    } for row in years_counts]

    subject_counts = conn.execute("SELECT subject, COUNT(*) as count FROM pyq_questions GROUP BY subject ORDER BY subject").fetchall()
    subject_bosses = [{
        "id": row['subject'],
        "type": "SUBJECT",
        "name": f"The {row['subject']} Golem",
        "hp": min(row['count'], 20),
        "max_hp": row['count'],
        "xp_reward": min(row['count'], 20) * 50,
        "loot": ["Subject Mastery Token", "Skill Point"]
    } for row in subject_counts]

    return year_bosses, subject_bosses

with app.app_context():
    conn = get_db()

    start = time.time()
    for _ in range(100):
        old_way(conn)
    print(f"Old way combined: {(time.time() - start)*1000:.2f} ms")

    start = time.time()
    for _ in range(100):
        new_way(conn)
    print(f"New way combined: {(time.time() - start)*1000:.2f} ms")
