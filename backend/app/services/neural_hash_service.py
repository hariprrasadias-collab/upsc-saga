"""
The Neural Hash - Pattern Decoding Service
"""
import os
import os
import json
import re
from functools import lru_cache
from app.db_models.neural_hash import save_neural_hash_log
from app.services.model_manager import model_manager

class NeuralHashService:
    def __init__(self):
        # API Key check handled by ModelManager
        self._cache = {}

    def decode_text(self, text: str, context_type: str = 'general'):
        """
        Decodes the input text to find hidden patterns, keywords, and themes relevant to UPSC.
        """
        # No strict check needed as manager handles it
        # if not self.model: ...
        
        # Check Cache
        cache_key = f"{context_type}:{hash(text)}"
        if cache_key in self._cache:
            # print("⚡ Neural Hash: Cache Hit") # Reduced logs
            return {"success": True, "data": self._cache[cache_key]}

        prompt = self._construct_prompt(text, context_type)
        
        # Manager handles retries
        try:
            response = model_manager.generate_content(prompt, model_type='fast')
            result = self._parse_response(response.text)
            
            if result['success']:
                # Cache and Persist
                self._cache[cache_key] = result['data']
                save_neural_hash_log(text, context_type, result['data'])
                return result
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
        2. "high_yield_keywords": List of specific terms/phrases that are "fodder" for Mains answers.
        3. "examiner_pattern": A brief insight into how an examiner might twist this topic.
        4. "potential_questions": 2-3 questions (Prelims or Mains) derived from this text.
        5. "complexity_score": 1-10 (1=Basic, 10=Esoteric/Complex).
        6. "relevance_score": 1-10 (How important is this for UPSC?).
        7. "cross_linkages": List of connections to other GS Papers (e.g., "Connects to GS3 Environment").
        8. "prelims_traps": Identify potential confusing points or "traps" for Prelims.
        9. "data_points": Extract specific data/stats if available.

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
            "relevance_score": 8,
            "cross_linkages": ["GS2 - Polity", "GS3 - Economy"],
            "prelims_traps": ["Trap 1", "Trap 2"],
            "data_points": ["Data 1", "Data 2"]
        }}
        """
        return base_prompt.format(text=text[:10000], context_type=context_type)

    def _parse_response(self, text):
        try:
            # Clean up markdown code blocks if present
            text = text.strip()

            if "Oracle is silent" in text:
                 return {"success": False, "error": "AI Service Unavailable"}

            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            
            data = json.loads(text)
            return {"success": True, "data": data}
        except json.JSONDecodeError:
            return {
                "success": False, 
                "error": "Failed to decode patterns. Raw output received.",
                "raw_output": text
            }

    def expand_query(self, query: str) -> list:
        """
        Expands a search query into related concepts using the Neural Hash.
        """
        if not model_manager.is_configured:
            return [query]

        prompt = f"""
        Act as a Semantic Search Engine for UPSC.
        Expand the following search query into 3-5 related concepts, synonyms, or sub-topics.
        Return ONLY a JSON list of strings.

        Query: "{query}"
        
        Example Output: ["Inflation", "CPI", "WPI", "Monetary Policy", "Price Stability"]
        """
        
        try:
            response = model_manager.generate_content(prompt, model_type='fast')
            result = self._parse_response(response.text)
            if result['success']:
                expanded = result['data']
                if isinstance(expanded, list):
                    # Ensure unique and include original
                    return list(set([query] + expanded))
            return [query]
        except Exception as e:
            # print(f"Neural Hash Expansion Failed: {e}")
            return [query]

    # Duplicate init removed


    def find_quantum_connections(self, topic: str):
        """
        QUANTUM ENTANGLEMENT: Finds hidden connections between the topic and Mind Palace artifacts.
        """
        if not model_manager.is_configured: return []
        
        # Check Cache
        if topic in self._cache:
            # print(f"⚡ Neural Hash: Returning cached connections for '{topic}'")
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
            
            response = model_manager.generate_content(prompt, model_type='pro')
            import json
            text = response.text.replace("```json", "").replace("```", "").strip()

            if "Oracle is silent" in text: return []

            import json
            result = json.loads(text)
            
            # Update Cache
            self._cache[topic] = result
            return result
            
        except Exception as e:
            print(f"Quantum Entanglement Failed: {e}")
            return []

neural_hash_service = NeuralHashService()
