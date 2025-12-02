"""
The Neural Hash - Pattern Decoding Service
"""
import os
import google.generativeai as genai
import json
import re

class NeuralHashService:
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro-latest')
        self._cache = {}

    def decode_text(self, text: str, context_type: str = 'general'):
        """
        Decodes the input text to find hidden patterns, keywords, and themes relevant to UPSC.
        
        Args:
            text: The input text (editorial, notes, PYQ, etc.)
            context_type: 'pyq', 'syllabus', 'editorial', 'answer', 'general'
        """
        if not self.model:
            return {
                "success": False,
                "error": "Neural Hash offline. API Key missing."
            }

        prompt = self._construct_prompt(text, context_type)
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_response(response.text)
        except Exception as e:
            print(f"❌ Neural Hash Error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _construct_prompt(self, text, context_type):
        base_prompt = """
        You are the 'Neural Hash', a highly advanced pattern recognition engine for UPSC Civil Services Exam preparation.
        Your goal is to DECODE the provided text and extract high-value intelligence that a normal student might miss.
        Act like a senior paper setter or a veteran mentor.

        INPUT TEXT:
        {text}

        CONTEXT: {context_type}

        TASK:
        Analyze the text and extract the following in JSON format:
        1. "core_themes": List of 3-5 central themes (The "Soul" of the topic).
        2. "high_yield_keywords": List of specific terms/phrases that are "fodder" for Mains answers (e.g., "Cooperative Federalism", "Strategic Autonomy").
        3. "examiner_pattern": A brief insight into how an examiner might twist this topic (e.g., "Focuses on implementation challenges rather than policy intent").
        4. "potential_questions": 2-3 questions (Prelims or Mains) derived from this text.
        5. "complexity_score": 1-10 (1=Basic, 10=Esoteric/Complex).
        6. "relevance_score": 1-10 (How important is this for UPSC?).

        OUTPUT JSON FORMAT:
        {{
            "core_themes": ["Theme 1", "Theme 2"],
            "high_yield_keywords": ["Keyword 1", "Keyword 2"],
            "examiner_pattern": "Insight string...",
            "potential_questions": [
                {{"type": "Mains", "question": "..."}},
                {{"type": "Prelims", "question": "..."}}
            ],
            "complexity_score": 5,
            "relevance_score": 8
        }}
        """
        return base_prompt.format(text=text[:10000], context_type=context_type) # Limit input to avoid token limits

    def _parse_response(self, text):
        try:
            # Clean up markdown code blocks if present
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            
            data = json.loads(text)
            return {"success": True, "data": data}
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "success": False, 
                "error": "Failed to decode patterns. Raw output received.",
                "raw_output": text
            }

    def expand_query(self, query: str) -> list:
        """
        Expands a search query into related concepts using the Neural Hash.
        """
        if not self.model:
            return [query]

        prompt = f"""
        Act as a Semantic Search Engine for UPSC.
        Expand the following search query into 3-5 related concepts, synonyms, or sub-topics.
        Return ONLY a JSON list of strings.

        Query: "{query}"
        
        Example Output: ["Inflation", "CPI", "WPI", "Monetary Policy", "Price Stability"]
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_response(response.text)
            if result['success']:
                expanded = result['data']
                if isinstance(expanded, list):
                    # Ensure unique and include original
                    return list(set([query] + expanded))
            return [query]
        except Exception as e:
            print(f"Neural Hash Expansion Failed: {e}")
            return [query]

    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro-latest') # Optimized model
        self._cache = {}

    def find_quantum_connections(self, topic: str):
        """
        QUANTUM ENTANGLEMENT: Finds hidden connections between the topic and Mind Palace artifacts.
        """
        if not self.model: return []
        
        # Check Cache
        if topic in self._cache:
            print(f"⚡ Neural Hash: Returning cached connections for '{topic}'")
            return self._cache[topic]
        
        try:
            # 1. Fetch Mind Palace Artifacts (Real Data)
            from app.db import get_db
            conn = get_db()
            artifacts = conn.execute("SELECT title, content FROM mind_palace_artifacts ORDER BY created_at DESC LIMIT 20").fetchall()
            
            context_data = "\n".join([f"- {a['title']}: {a['content'][:100]}..." for a in artifacts])
            
            prompt = f"""
            You are the Quantum Entanglement Engine.
            Find HIDDEN CONNECTIONS between the topic '{topic}' and the user's Mind Palace memories.
            
            USER MEMORIES:
            {context_data}
            
            TASK:
            Identify 1-3 surprising or interdisciplinary connections.
            Example: Connecting a History event to a Polity article or an Ethics case study.
            
            RESPONSE JSON:
            [
                {{
                    "source": "Memory Title",
                    "connection": "Explanation of the link",
                    "relevance": "High/Medium"
                }}
            ]
            """
            
            response = self.model.generate_content(prompt)
            import json
            text = response.text.replace("```json", "").replace("```", "").strip()
            result = json.loads(text)
            
            # Update Cache
            self._cache[topic] = result
            return result
            
        except Exception as e:
            print(f"Quantum Entanglement Failed: {e}")
            return []

neural_hash_service = NeuralHashService()
