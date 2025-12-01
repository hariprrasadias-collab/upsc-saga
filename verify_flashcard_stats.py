import sqlite3
import os
from datetime import datetime

db_path = os.path.join('backend', 'upsc_saga.db')
print(f"Connecting to {db_path}\n")

try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    user_id = 1

    # 1. Total cards for user
    cursor.execute('''
        SELECT COUNT(f.id)
        FROM flashcards f
        JOIN decks d ON f.deck_id = d.id
        WHERE d.user_id = ?
    ''', (user_id,))
    total = cursor.fetchone()[0]
    print(f"✓ Total Cards for User {user_id}: {total}")

    # 2. Maturity breakdown
    all_cards = conn.execute('''
        SELECT f.id, rs.halflife, rs.alpha, rs.beta
        FROM flashcards f
        JOIN decks d ON f.deck_id = d.id
        LEFT JOIN (
            SELECT flashcard_id, halflife, alpha, beta
            FROM review_sessions
            WHERE (flashcard_id, reviewed_at) IN (
                SELECT flashcard_id, MAX(reviewed_at)
                FROM review_sessions
                GROUP BY flashcard_id
            )
        ) rs ON f.id = rs.flashcard_id
        WHERE d.user_id = ?
    ''', (user_id,)).fetchall()

    maturity_counts = {'new': 0, 'learning': 0, 'young': 0, 'mature': 0, 'mastered': 0}
    for card in all_cards:
        if card['halflife'] is None:
            maturity_counts['new'] += 1
        else:
            hl = card['halflife']
            # Updated logic: halflife < 1 is now 'learning', not 'new'
            if hl < 1: maturity = 'learning'
            elif hl < 7: maturity = 'learning'
            elif hl < 30: maturity = 'young'
            elif hl < 180: maturity = 'mature'
            else: maturity = 'mastered'
            maturity_counts[maturity] += 1

    print(f"\n✓ Maturity Breakdown:")
    for key, count in maturity_counts.items():
        print(f"  {key.capitalize()}: {count}")

    # 3. Total reviews
    cursor.execute('SELECT COUNT(*) FROM review_sessions WHERE user_id = ?', (user_id,))
    total_reviews = cursor.fetchone()[0]
    print(f"\n✓ Total Reviews: {total_reviews}")

    # 4. Streak (using localtime)
    recent_days = conn.execute('''
        SELECT DATE(reviewed_at, 'localtime') as review_date
        FROM review_sessions
        WHERE user_id = ? AND reviewed_at >= datetime('now', '-30 days', 'localtime')
        GROUP BY DATE(reviewed_at, 'localtime')
        ORDER BY review_date DESC
    ''', (user_id,)).fetchall()

    streak = 0
    if recent_days:
        last_date = datetime.now().date()
        for row in recent_days:
            review_date = datetime.fromisoformat(row['review_date']).date()
            if (last_date - review_date).days <= 1:
                streak += 1
                last_date = review_date
            else:
                break

    print(f"✓ Daily Streak: {streak} days")

    print("\n" + "="*50)
    print("✓ All statistics calculated successfully!")
    print("="*50)

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    if conn:
        conn.close()
