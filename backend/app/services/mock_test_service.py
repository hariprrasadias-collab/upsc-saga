from app.db import get_db
import traceback

class MockTestService:
    """
    Service for accessing Mock Test data for the Brain.
    """
    @staticmethod
    def get_brain_context():
        """Standard interface for the Brain to pull context."""
        try:
            conn = get_db()

            # Overall stats
            stats = conn.execute('''
                SELECT
                    COUNT(*) as total_attempts,
                    AVG(score) as avg_score,
                    MAX(score) as best_score,
                    AVG(percentage) as avg_percentage
                FROM test_attempts
                WHERE user_id = 1 AND status = 'completed'
            ''').fetchone()

            # Recent activity
            recent = conn.execute('''
                SELECT mt.title, ta.score, ta.percentage, ta.submitted_at
                FROM test_attempts ta
                JOIN mock_tests mt ON ta.test_id = mt.id
                WHERE ta.user_id = 1 AND ta.status = 'completed'
                ORDER BY ta.submitted_at DESC
                LIMIT 3
            ''').fetchall()

            return {
                "status": "active",
                "data": {
                    "total_attempts": stats['total_attempts'] if stats else 0,
                    "average_score": round(stats['avg_score'], 1) if stats and stats['avg_score'] else 0,
                    "recent_tests": [
                        f"{r['title']} ({round(r['percentage'], 1)}%)" for r in recent
                    ] if recent else []
                }
            }
        except Exception:
            return {"status": "error", "data": {}}

    @staticmethod
    def create_smart_test(topic):
        """Alias for generate_from_topic to fix attribute error."""
        return MockTestService.generate_from_topic(topic)

    @staticmethod
    def generate_from_topic(topic, count=10):
        """Generate a mock test for a topic using Gemini."""
        import json
        import re
        import ast
        from app.services.model_manager import model_manager
        
        # print(f"🤖 Generating Mock Test for: {topic}") # Reduced logs
        
        # API Check handled by manager
        
        # Handle "Weak Areas" special case
        if topic.lower() == "weak areas":
            try:
                from app.services.analytics_service import identify_weak_areas
                conn = get_db()
                weak_data = identify_weak_areas(conn, 1, limit=3)
                if weak_data:
                    topic = ", ".join([w['subject'] for w in weak_data])
                else:
                    topic = "General Studies"
            except Exception as e:
                topic = "General Studies"
        
        prompt = f"""
        # MISSION: DESIGN A 'TITAN LEVEL' PRELIMS TEST
        **Topic:** "{topic}"
        **Count:** {count} Questions
        
        **DIRECTIVE:**
        You are the Chief Examiner for UPSC. Your goal is to filter out the non-serious candidates.
        
        **QUESTION ARCHITECTURE:**
        1. **The Statement Trap:** Use "Only", "All", "Drastically" to trick guessers.
        2. **The Chronology Twist:** Mix up events by just 1 year.
        3. **The Current Affairs Camouflage:** Wrap a static concept in a recent news headline.

        **EXPLANATION (CRITICAL):**
        - Do not just say "A is correct".
        - Explain **WHY B, C, and D are wrong**. (e.g., "Option B is incorrect because Article 32 applies to SC, not HC").

        **OUTPUT SCHEMA (JSON ONLY):**
        {{
            "title": "Test: {topic}",
            "questions": [
                {{
                    "question_text": "Consider the following statements about [Sub-topic]...\\n1. Statement A\\n2. Statement B\\nWhich are correct?",
                    "option_a": "1 only",
                    "option_b": "2 only",
                    "option_c": "Both 1 and 2",
                    "option_d": "Neither 1 nor 2",
                    "correct_answer": "C",
                    "explanation": "Statement 1 is correct because... Statement 2 is correct because... \\n\\n**TRAP ANALYSIS:** Students often confuse X with Y."
                }}
            ]
        }}
        """
        
        try:
            # Use ModelManager for rate limiting and load balancing
            response = model_manager.generate_content(prompt, model_type='pro', max_output_tokens=4096)
            
            if hasattr(response, 'text'):
                text = response.text.strip()
            else:
                text = str(response)
            
            if "Oracle is silent" in text:
                 return {"success": False, "error": "AI Service Unavailable"}

            # Robust JSON extraction
            json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
            if json_match:
                text = json_match.group(1)
            else:
                start = text.find('{')
                end = text.rfind('}')
                if start != -1 and end != -1:
                    text = text[start:end+1]
            
            # Clean up potential trailing commas (simple regex)
            text = re.sub(r',\s*}', '}', text)
            text = re.sub(r',\s*]', ']', text)

            try:
                data = json.loads(text)
            except json.JSONDecodeError as e:
                print(f"❌ Mock Test JSON Error: {e}")
                print(f"Raw text was: {text[:500]} ...")
                return {"success": False, "error": "Failed to parse AI response (Invalid JSON)"}
            
            conn = get_db()
            
            # Create Test
            cursor = conn.execute('''
                INSERT INTO mock_tests (title, subject, total_questions, duration_minutes, test_type, total_marks)
                VALUES (?, ?, ?, ?, 'MOCK', ?)
            ''', (data['title'], topic, len(data['questions']), len(data['questions'])*2, len(data['questions'])*2))
            test_id = cursor.lastrowid
            
            # Add Questions
            # ⚡ Bolt Optimization: Replaced iterative inserts with bulk executemany
            # Expected impact: Dramatically reduces DB execution time for large mock tests (O(1) commit vs O(n))
            questions_data = [
                (test_id, i, q['question_text'], q['option_a'], q['option_b'], q['option_c'], q['option_d'], q['correct_answer'], q['explanation'])
                for i, q in enumerate(data['questions'], 1)
            ]
            conn.executemany('''
                INSERT INTO test_questions
                (test_id, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', questions_data)
                
            conn.commit()
            return {"success": True, "message": f"Created test '{data['title']}' with {len(data['questions'])} questions.", "test_id": test_id}
            
        except Exception as e:
            # print(f"❌ Mock Test Generation Error: {e}") # Reduced logs
            return {"success": False, "error": str(e)}

# Register Synapse
try:
    from app.services.synapse_registry import SynapseRegistry
    SynapseRegistry.get_instance().register_synapse(
        category='ASSESSMENT',
        name='mock_tests',
        service_ref=MockTestService,
        description='Tracks mock test performance and scores.'
    )
except ImportError:
    pass
