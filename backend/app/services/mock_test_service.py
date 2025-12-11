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
        import os
        import json
        import re
        from app.services.model_manager import model_manager
        
        # print(f"🤖 Generating Mock Test for: {topic}") # Reduced logs
        
        if not model_manager.is_configured:
            return {"success": False, "error": "API Key missing"}
        
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
        Create a {count}-question multiple choice test for: "{topic}".
        Strict UPSC standard.
        
        CRITICAL OUTPUT RULES:
        1. Return ONLY a valid JSON object.
        2. Use DOUBLE QUOTES for all keys and strings.
        3. NO trailing commas.
        4. NO comments.
        
        Structure:
        {{
            "title": "Test: {topic}",
            "questions": [
                {{
                    "question_text": "...",
                    "option_a": "...",
                    "option_b": "...",
                    "option_c": "...",
                    "option_d": "...",
                    "correct_answer": "A",
                    "explanation": "..."
                }}
            ]
        }}
        """
        
        try:
            response = model_manager.generate_content(prompt, model_type='fast')
            
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
            except json.JSONDecodeError:
                return {"success": False, "error": "Failed to parse AI response (Invalid JSON)"}
            
            conn = get_db()
            
            # Create Test
            cursor = conn.execute('''
                INSERT INTO mock_tests (title, subject, total_questions, duration_minutes, test_type, total_marks)
                VALUES (?, ?, ?, ?, 'MOCK', ?)
            ''', (data['title'], topic, len(data['questions']), len(data['questions'])*2, len(data['questions'])*2))
            test_id = cursor.lastrowid
            
            # Add Questions
            for i, q in enumerate(data['questions'], 1):
                conn.execute('''
                    INSERT INTO test_questions 
                    (test_id, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (test_id, i, q['question_text'], q['option_a'], q['option_b'], q['option_c'], q['option_d'], q['correct_answer'], q['explanation']))
                
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
