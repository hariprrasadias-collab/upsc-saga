"""
Cleanup script to remove orphaned flashcards from the database.
Orphaned flashcards are those with:
1. deck_id IS NULL
2. deck_id references a non-existent deck

Usage:
    python cleanup_orphaned_flashcards.py [--dry-run]
"""

import sys
sys.path.insert(0, 'backend')

from app import create_app
from app.db import get_db
import argparse

# Create Flask app context
app = create_app()
app.app_context().push()

def find_orphaned_flashcards():
    """Find all orphaned flashcards."""
    conn = get_db()
    
    # Find flashcards with NULL deck_id
    null_deck = conn.execute('''
        SELECT id, front, back, created_at 
        FROM flashcards 
        WHERE deck_id IS NULL
    ''').fetchall()
    
    # Find flashcards referencing non-existent decks
    invalid_deck = conn.execute('''
        SELECT f.id, f.front, f.back, f.deck_id, f.created_at
        FROM flashcards f
        LEFT JOIN decks d ON f.deck_id = d.id
        WHERE f.deck_id IS NOT NULL AND d.id IS NULL
    ''').fetchall()
    
    return list(null_deck) + list(invalid_deck)

def delete_orphaned_flashcards(dry_run=True):
    """Delete orphaned flashcards from the database."""
    conn = get_db()
    orphaned = find_orphaned_flashcards()
    
    if not orphaned:
        print("✅ No orphaned flashcards found!")
        return 0
    
    print(f"\n🔍 Found {len(orphaned)} orphaned flashcard(s):\n")
    
    for i, card in enumerate(orphaned, 1):
        front_preview = card['front'][:50] + '...' if len(card['front']) > 50 else card['front']
        print(f"{i}. ID: {card['id']}")
        print(f"   Front: {front_preview}")
        print(f"   Created: {card['created_at']}")
        print()
    
    if dry_run:
        print("🔒 DRY RUN MODE - No flashcards were deleted.")
        print("Run with --execute to actually delete these flashcards.\n")
        return len(orphaned)
    
    # Delete orphaned flashcards
    orphaned_ids = [card['id'] for card in orphaned]
    
    # First delete associated review sessions
    conn.execute(f'''
        DELETE FROM review_sessions 
        WHERE flashcard_id IN ({','.join('?' * len(orphaned_ids))})
    ''', orphaned_ids)
    
    # Then delete the flashcards
    conn.execute(f'''
        DELETE FROM flashcards 
        WHERE id IN ({','.join('?' * len(orphaned_ids))})
    ''', orphaned_ids)
    
    conn.commit()
    
    print(f"✅ Successfully deleted {len(orphaned)} orphaned flashcard(s)!\n")
    return len(orphaned)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remove orphaned flashcards')
    parser.add_argument('--execute', action='store_true', 
                       help='Actually delete the flashcards (default is dry-run)')
    
    args = parser.parse_args()
    
    deleted_count = delete_orphaned_flashcards(dry_run=not args.execute)
    
    # Show summary
    print("=" * 50)
    print(f"Total orphaned flashcards: {deleted_count}")
    print("=" * 50)
