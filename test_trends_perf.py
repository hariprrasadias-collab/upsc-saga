import time
from app import create_app
import sqlite3

app = create_app()
with app.app_context():
    from app.routes.seer import get_year_trends
    from app.db import get_db
    conn = get_db()
    for _ in range(10000):
        # Insert some dummy data to make it slower
        conn.execute("INSERT INTO pyq_questions (year, subject, question_text, option_a, option_b, option_c, option_d, correct_option) VALUES (?, ?, 'Q', 'A', 'B', 'C', 'D', 'A')", (1990 + _ % 30, f"Sub{_ % 25}"))
    conn.commit()

    # N+1 query original
    start = time.time()
    for _ in range(50):
        get_year_trends()
    end = time.time()
    print(f"Original Elapsed: {end-start}")

    # Optimized query
    def get_year_trends_optimized():
        conn = get_db()
        try:
            # We can get year, subject, and counts all in one query using GROUP BY
            rows = conn.execute('''
                SELECT year, subject, COUNT(*) as count
                FROM pyq_questions
                GROUP BY year, subject
                ORDER BY year, subject
            ''').fetchall()

            # Reconstruct the expected response structure
            years_data = {}
            for row in rows:
                year = row['year']
                subject = row['subject']
                count = row['count']

                if year not in years_data:
                    years_data[year] = {"year": year}

                years_data[year][subject] = count

            data = list(years_data.values())
            return data
        except Exception as e:
            return {'error': str(e)}

    start = time.time()
    for _ in range(50):
        get_year_trends_optimized()
    end = time.time()
    print(f"Optimized Elapsed: {end-start}")
