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
        
        # ⚡ Bolt Optimization: Use SQLite for time-based aggregation but preserve domain logic
        from datetime import datetime
        now_iso = datetime.now().isoformat()
        
        # Calculate due count directly in SQL to avoid slow datetime.fromisoformat loops
        due_count = conn.execute('''
            SELECT COUNT(*)
            FROM flashcards f
            LEFT JOIN (
                SELECT flashcard_id, next_review
                FROM review_sessions
                WHERE (flashcard_id, reviewed_at) IN (
                    SELECT flashcard_id, MAX(reviewed_at)
                    FROM review_sessions
                    GROUP BY flashcard_id
                )
            ) rs ON f.id = rs.flashcard_id
            WHERE rs.next_review IS NULL OR rs.next_review <= ?
        ''', (now_iso,)).fetchone()[0]
        
        # Fetch only the exact latest review parameters needed for the Ebisu SRS domain logic
        mastery_data = conn.execute('''
            SELECT alpha, beta, halflife
            FROM review_sessions
            WHERE halflife IS NOT NULL AND (flashcard_id, reviewed_at) IN (
                SELECT flashcard_id, MAX(reviewed_at)
                FROM review_sessions
                GROUP BY flashcard_id
            )
        ''').fetchall()

        # Calculate mastery strictly using the domain-specific get_card_maturity function
        mastered_count = 0
        for card in mastery_data:
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
        from app.services.model_manager import model_manager
        import json
        
        # API Check handled by manager
        
        prompt = f"""
        # MISSION: ACTIVE RECALL ARSENAL
        **Topic:** {topic}
        **Count:** {count}

        **DIRECTIVE:**
        Create "Scenario-Based" flashcards. Avoid simple definitions.

        **BAD:**
        Front: What is Article 21?
        Back: Right to Life.

        **GOOD:**
        Front: A citizen is denied a passport to travel abroad. Which SC judgment and Article protects this right?
        Back: **Maneka Gandhi vs Union of India (1978)**. Expanded **Article 21** to include the right to travel abroad and "Due Process of Law".

        **OUTPUT SCHEMA (JSON Array):**
        [
            {{"front": "The Scenario/Tricky Question", "back": "The Specific Answer + Context"}}
        ]
        """
        
        try:
            response = model_manager.generate_content(prompt, model_type='pro')
            text = response.text.strip()
            
            # Robust Extraction
            if text.startswith("```"):
                 text = text.replace('```json', '').replace('```', '').strip()

            start = text.find('[')
            end = text.rfind(']')
            
            if start != -1 and end != -1:
                text = text[start:end+1]
                cards = json.loads(text)
            else:
                raise Exception("No JSON array found in response")
            
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
