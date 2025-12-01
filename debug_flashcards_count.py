
import sqlite3
import os

db_path = os.path.join('backend', 'upsc_saga.db')
print(f"Connecting to {db_path}")

try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Total count in flashcards table
    cursor.execute("SELECT COUNT(*) FROM flashcards")
    total_raw = cursor.fetchone()[0]
    print(f"Total rows in 'flashcards' table: {total_raw}")

    # 2. Count of cards linked to decks owned by user_id=1
    cursor.execute('''
        SELECT COUNT(f.id) 
        FROM flashcards f
        JOIN decks d ON f.deck_id = d.id
        WHERE d.user_id = 1
    ''')
    total_user_1 = cursor.fetchone()[0]
    print(f"Total cards for user_id=1: {total_user_1}")

    # 3. Check for orphaned cards (deck_id not in decks)
    cursor.execute('''
        SELECT COUNT(f.id)
        FROM flashcards f
        LEFT JOIN decks d ON f.deck_id = d.id
        WHERE d.id IS NULL
    ''')
    orphaned = cursor.fetchone()[0]
    print(f"Orphaned cards (invalid deck_id): {orphaned}")

    # 4. Check for cards in decks owned by other users
    cursor.execute('''
        SELECT d.user_id, COUNT(f.id)
        FROM flashcards f
        JOIN decks d ON f.deck_id = d.id
        WHERE d.user_id != 1
        GROUP BY d.user_id
    ''')
    other_users = cursor.fetchall()
    print("Cards by other users:")
    for row in other_users:
        print(f"User {row['user_id']}: {row[1]} cards")

    # 5. List all decks and their card counts for user 1
    print("\nDecks for User 1:")
    cursor.execute('''
        SELECT d.name, COUNT(f.id) as count
        FROM decks d
        LEFT JOIN flashcards f ON d.id = f.deck_id
        WHERE d.user_id = 1
        GROUP BY d.id
    ''')
    decks = cursor.fetchall()
    for row in decks:
        print(f"- {row['name']}: {row['count']}")

except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
