import sqlite3

conn = sqlite3.connect('upsc_saga.db')
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM questions_master")
count = c.fetchone()[0]
print(f"Total questions in master table: {count}")

c.execute("SELECT source, subject, question_text FROM questions_master LIMIT 1")
row = c.fetchone()
print(f"Sample: {row}")

conn.close()
