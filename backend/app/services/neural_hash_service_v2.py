"""
The Neural Hash - Pattern Decoding Service (V2 - Robust Fallback)
"""
import os
import json
import re
from functools import lru_cache
from app.db_models.neural_hash import save_neural_hash_log
from app.utils.ai_factory import AIModelFactory

class NeuralHashService:
    def __init__(self):
        self._cache = {}
        # No need to init genai here, factory handles it

    def decode_text(self, text: str, context_type: str = 'general'):
        """
        Decodes the input text to find hidden patterns, keywords, and themes relevant to UPSC.
        """
        # Check Cache
        cache_key = f"{context_type}:{hash(text)}"
        if cache_key in self._cache:
            print("⚡ Neural Hash: Cache Hit")
            return {"success": True, "data": self._cache[cache_key]}

        prompt = self._construct_prompt(text, context_type)
        
        try:
            # Use Factory to get a robust model wrapper
            model = AIModelFactory.get_model(strategy='speed')
            response = model.generate_content(prompt)
            result = self._parse_response(response.text)
            
            if result['success']:
                # Cache and Persist
                self._cache[cache_key] = result['data']
                save_neural_hash_log(text, context_type, result['data'])
                return result
            else:
                 return result

        except Exception as e:
            print(f"❌ Neural Hash Critical Failure: {e}")
            return {
                "success": False,
                "error": f"Neural Hash Overload. All models busy/quota exceeded. Error: {str(e)}"
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

neural_hash_service = NeuralHashService()
