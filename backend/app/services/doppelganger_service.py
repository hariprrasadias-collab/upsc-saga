"""
The Doppelgänger - Adversarial AI Service
Learns from user mistakes to create the ultimate personalized opponent.
"""
import json
from app.db import get_db
from app.services.model_manager import model_manager

class DoppelgangerService:
    def __init__(self):
        pass

    def analyze_player_style(self, user_id=1):
        """
        Analyzes mistakes to find the 'Gap'.
        """
        try:
            conn = get_db()

            # Fetch recent mistakes
            mistakes = conn.execute('''
                SELECT question_text, user_answer, correct_answer, explanation, topic
                FROM quiz_history
                WHERE user_id = ? AND is_correct = 0
                ORDER BY timestamp DESC LIMIT 20
            ''', (user_id,)).fetchall()

            if not mistakes:
                return "No mistakes found. The Shadow is dormant."

            mistake_data = "\n".join([f"Q: {m['question_text']}\nTopic: {m['topic']}\nWrong: {m['user_answer']} (Correct: {m['correct_answer']})" for m in mistakes])

            prompt = f"""
            # MISSION: ANALYZE PLAYER WEAKNESS
            **Role:** The Doppelgänger (Adversarial AI).

            **PLAYER MISTAKES:**
            {mistake_data}

            **DIRECTIVE:**
            Identify the COGNITIVE BIAS pattern.
            - Does the player guess blindly on dates?
            - Do they fall for 'All of the above'?
            - Do they confuse similar constitutional articles?

            **OUTPUT:**
            A 'Villain Monologue' describing exactly how you will defeat them next time.
            """

            response = model_manager.generate_content(prompt, model_type='pro')
            return response.text

        except Exception as e:
            print(f"Doppelganger Analysis Failed: {e}")
            return "The Shadow is unclear."

    def generate_shadow_duel(self, user_id=1):
        """
        Creates a 'Shadow Duel' - a quiz made 100% of trap questions.
        """
        print("👤 Doppelgänger: Constructing Shadow Duel...")
        try:
            analysis = self.analyze_player_style(user_id)

            prompt = f"""
            # MISSION: SHADOW DUEL GENERATION
            **Analysis of Player:**
            {analysis}

            **TASK:**
            Generate 5 'Trap' Questions designed to exploit these specific weaknesses.
            If they confuse dates, give them 4 dates very close to each other.
            If they ignore 'NOT', put 'NOT' in every question.

            **OUTPUT SCHEMA (JSON):**
            [
                {{
                    "question": "...",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "B",
                    "trap_explanation": "I chose this because you always fall for..."
                }}
            ]
            """

            response = model_manager.generate_content(prompt, model_type='pro')

            # Parse JSON
            text = response.text.strip()
            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()

            questions = json.loads(text)

            # Save to DB as a special quiz
            from app.services.mock_test_service import MockTestService
            # We can reuse create_custom_test logic or insert manually
            # Let's manual insert to tag it as 'SHADOW'
            conn = get_db()
            cursor = conn.execute('''
                INSERT INTO mock_tests (title, subject, total_questions, duration_minutes, test_type, total_marks)
                VALUES (?, ?, ?, ?, 'SHADOW', ?)
            ''', ("⚔️ Shadow Duel", "Mixed", len(questions), 10, len(questions)*2))
            test_id = cursor.lastrowid

            # ⚡ Bolt Optimization: Use executemany for batch insertions to reduce database I/O and context-switching overhead
            question_tuples = [
                (test_id, i, q['question'], q['options'][0], q['options'][1], q['options'][2], q['options'][3], q['correct_answer'], q['trap_explanation'])
                for i, q in enumerate(questions, 1)
            ]
            conn.executemany('''
                INSERT INTO test_questions
                (test_id, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', question_tuples)
            conn.commit()

            return {
                "success": True,
                "message": "The Shadow awaits.",
                "test_id": test_id,
                "analysis": analysis
            }

        except Exception as e:
            print(f"Shadow Duel Creation Failed: {e}")
            return {"success": False, "error": str(e)}

doppelganger_service = DoppelgangerService()
