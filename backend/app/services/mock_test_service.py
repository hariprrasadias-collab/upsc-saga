from app.db import get_db

class MockTestService:
    """
    Service for accessing Mock Test data for the Brain.
    """
    @staticmethod
    def get_brain_context():
        """Standard interface for the Brain to pull context."""
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

    @staticmethod
    def generate_from_topic(topic, count=10):
        """Generate a mock test for a topic using Gemini."""
        import google.generativeai as genai
        import os
        import json
        
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return {"success": False, "error": "API Key missing"}
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = f"""
        Create a {count}-question multiple choice test for: "{topic}".
        Strict UPSC standard.
        Return ONLY a JSON object:
        {{
            "title": "Test: {topic}",
            "questions": [
                {{
                    "question_text": "...",
                    "option_a": "...",
                    "option_b": "...",
                    "option_c": "...",
                    "option_d": "...",
                    "correct_answer": "A|B|C|D",
                    "explanation": "..."
                }}
            ]
        }}
        """
        
        try:
            response = model.generate_content(prompt)
            text = response.text.replace('```json', '').replace('```', '').strip()
            data = json.loads(text)
            
            conn = get_db()
            
            # Create Test
            cursor = conn.execute('''
                INSERT INTO mock_tests (title, subject, total_questions, duration_minutes)
                VALUES (?, 'General', ?, ?)
            ''', (data['title'], len(data['questions']), len(data['questions'])*2))
            test_id = cursor.lastrowid
            
            # Add Questions
            for i, q in enumerate(data['questions'], 1):
                conn.execute('''
                    INSERT INTO test_questions 
                    (test_id, question_number, question_text, option_a, option_b, option_c, option_d, correct_answer, explanation)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (test_id, i, q['question_text'], q['option_a'], q['option_b'], q['option_c'], q['option_d'], q['correct_answer'], q['explanation']))
                
            conn.commit()
            return {"success": True, "message": f"Created test '{data['title']}' with {len(data['questions'])} questions."}
            
        except Exception as e:
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
