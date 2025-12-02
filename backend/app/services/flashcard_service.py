from app.db import get_db
from app.services.ebisu_srs import get_card_maturity

class FlashcardService:
    """
    Service for accessing Flashcard data for the Brain.
    """
    @staticmethod
    def get_brain_context():
        """Standard interface for the Brain to pull context."""
        conn = get_db()
        
        # Total cards
        total = conn.execute('SELECT COUNT(*) FROM flashcards').fetchone()[0]
        
        # Due cards (simple check based on review_sessions)
        # This is a simplified check compared to the full route logic for performance
        due_count = 0
        
        # Get all cards with their latest review
        all_cards = conn.execute('''
            SELECT f.id, rs.halflife, rs.alpha, rs.beta, rs.next_review
            FROM flashcards f
            LEFT JOIN (
                SELECT flashcard_id, halflife, alpha, beta, next_review, reviewed_at
                FROM review_sessions
                WHERE (flashcard_id, reviewed_at) IN (
                    SELECT flashcard_id, MAX(reviewed_at)
                    FROM review_sessions
                    GROUP BY flashcard_id
                )
            ) rs ON f.id = rs.flashcard_id
        ''').fetchall()
        
        mastered_count = 0
        from datetime import datetime
        now = datetime.now()
        
        for card in all_cards:
            # Check if due
            if card['next_review']:
                next_review = datetime.fromisoformat(card['next_review'])
                if next_review <= now:
                    due_count += 1
            else:
                # New card is effectively due
                due_count += 1
                
            # Check mastery
            if card['halflife']:
                maturity = get_card_maturity(card['alpha'], card['beta'], card['halflife'])
                if maturity == 'mastered':
                    mastered_count += 1

        return {
            "status": "active",
            "data": {
                "total_cards": total,
                "due_for_review": due_count,
                "mastered_cards": mastered_count
            }
        }

    @staticmethod
    def generate_from_topic(topic, count=5):
        """Generate flashcards for a topic using Gemini."""
        import google.generativeai as genai
        import os
        import json
        
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return {"success": False, "error": "API Key missing"}
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro-latest')
        
        prompt = f"""
        Create {count} high-quality flashcards for the topic: "{topic}".
        Focus on UPSC relevant facts, dates, and concepts.
        Return ONLY a JSON array of objects:
        [
            {{"front": "Question...", "back": "Answer..."}},
            ...
        ]
        """
        
        try:
            response = model.generate_content(prompt)
            text = response.text.replace('```json', '').replace('```', '').strip()
            cards = json.loads(text)
            
            # Save to DB
            conn = get_db()
            deck_name = f"Auto-Gen: {topic}"
            
            # Create/Get Deck
            cursor = conn.execute("SELECT id FROM decks WHERE name = ?", (deck_name,))
            row = cursor.fetchone()
            if row:
                deck_id = row[0]
            else:
                cursor = conn.execute("INSERT INTO decks (user_id, name, subject) VALUES (1, ?, 'General')", (deck_name,))
                deck_id = cursor.lastrowid
                
            for card in cards:
                conn.execute('''
                    INSERT INTO flashcards (deck_id, front, back, source)
                    VALUES (?, ?, ?, 'ai_generated')
                ''', (deck_id, card['front'], card['back']))
                
            conn.commit()
            return {"success": True, "message": f"Created {len(cards)} flashcards in deck '{deck_name}'"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# Register Synapse
try:
    from app.services.synapse_registry import SynapseRegistry
    SynapseRegistry.get_instance().register_synapse(
        category='KNOWLEDGE',
        name='flashcards',
        service_ref=FlashcardService,
        description='Tracks flashcard retention and due reviews.'
    )
except ImportError:
    pass
