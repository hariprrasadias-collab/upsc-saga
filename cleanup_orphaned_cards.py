import sqlite3
import os

db_path = os.path.join('backend', 'upsc_saga.db')
print(f"Connecting to {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Count orphaned cards before deletion
    cursor.execute('''
        SELECT COUNT(f.id)
        FROM flashcards f
        LEFT JOIN decks d ON f.deck_id = d.id
        WHERE d.id IS NULL
    ''')
    orphaned_count = cursor.fetchone()[0]
    print(f"Found {orphaned_count} orphaned cards.")

    if orphaned_count > 0:
        # 2. Delete orphaned cards
        print("Deleting orphaned cards...")
        cursor.execute('''
            DELETE FROM flashcards
            WHERE id IN (
                SELECT f.id
                FROM flashcards f
                LEFT JOIN decks d ON f.deck_id = d.id
                WHERE d.id IS NULL
            )
        ''')
        deleted_count = cursor.rowcount
        conn.commit()
        print(f"Deleted {deleted_count} cards.")

        # 3. Verify count after deletion
        cursor.execute('''
            SELECT COUNT(f.id)
            FROM flashcards f
            LEFT JOIN decks d ON f.deck_id = d.id
            WHERE d.id IS NULL
        ''')
        remaining = cursor.fetchone()[0]
        print(f"Remaining orphaned cards: {remaining}")
    else:
        print("No orphaned cards to delete.")

except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
