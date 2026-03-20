import time
from backend.app.db import get_db
from backend.app import create_app

app = create_app()

def old_way(conn):
    subjects = conn.execute("SELECT DISTINCT subject FROM pyq_questions ORDER BY subject").fetchall()

    bosses = []
    for row in subjects:
        boss_id = row['subject']
        count = conn.execute("SELECT COUNT(*) FROM pyq_questions WHERE subject = ?", (boss_id,)).fetchone()[0]
        name = f"The {boss_id} Golem"
        loot = ["Subject Mastery Token", "Skill Point"]
        hp = min(count, 20)
        xp_reward = hp * 50
        bosses.append({
            "id": boss_id,
            "type": "SUBJECT",
            "name": name,
            "hp": hp,
            "max_hp": count,
            "xp_reward": xp_reward,
            "loot": loot
        })
    return bosses

def new_way(conn):
    subject_counts = conn.execute("SELECT subject, COUNT(*) as count FROM pyq_questions GROUP BY subject ORDER BY subject").fetchall()

    bosses = []
    for row in subject_counts:
        boss_id = row['subject']
        count = row['count']
        name = f"The {boss_id} Golem"
        loot = ["Subject Mastery Token", "Skill Point"]
        hp = min(count, 20)
        xp_reward = hp * 50
        bosses.append({
            "id": boss_id,
            "type": "SUBJECT",
            "name": name,
            "hp": hp,
            "max_hp": count,
            "xp_reward": xp_reward,
            "loot": loot
        })
    return bosses


with app.app_context():
    conn = get_db()

    start = time.time()
    for _ in range(100):
        old_way(conn)
    print(f"Old way (subject): {(time.time() - start)*1000:.2f} ms")

    start = time.time()
    for _ in range(100):
        new_way(conn)
    print(f"New way (subject): {(time.time() - start)*1000:.2f} ms")
