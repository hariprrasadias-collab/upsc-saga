import os
import json
from dotenv import load_dotenv
from app.services.model_manager import model_manager

load_dotenv()

# Configure Gemini API (Managed by ModelManager)

class EssayEvaluator:
    def __init__(self):
        pass # ModelManager handles init

    def evaluate_essay(self, topic, content):
        """
        Evaluates a UPSC essay using Gemini API.
        Returns a JSON object with score, strengths, weaknesses, and model structure.
        """
        prompt = f"""
        # MISSION: UPSC ESSAY EVALUATION (CHIEF EXAMINER MODE)
        **Role:** Retired UPSC Chairperson & Lead Essay Evaluator.
        **Standards:** Strict adherence to UPSC rubric (Relevance, Coherence, Critical Analysis, Concise Expression).

        **Topic:** "{topic}"
        
        **CANDIDATE ESSAY:**
        "{content}"

        **DIRECTIVE:**
        1. **Ruthless Scoring:** Don't be generous. Average is 100-125. 140+ is exceptional.
        2. **Dimensional Check:** Did they cover PESTLE (Political, Economic, Social, Tech, Legal, Env)?
        3. **Thesis Tracking:** Did the intro promise a thesis that the conclusion delivered?
        4. **Micro-Editing:** Quote specific bad sentences and rewrite them.

        **OUTPUT SCHEMA (JSON ONLY):**
        {{
            "score": <integer_0_to_250>,
            "strengths": ["Specific point 1", "Specific point 2"],
            "weaknesses": ["Specific point 1", "Specific point 2"],
            "suggestions": ["Actionable advice 1", "Actionable advice 2"],
            "micro_edits": [
                {{ "original": "Bad sentence...", "improved": "Better sentence..." }}
            ],
            "dimensions_covered": ["Polity", "Economy", "Ethics"],
            "dimensions_missed": ["International Relations", "Technology"],
            "model_structure": {{
                "introduction": "How the perfect intro would hook the reader.",
                "body_flow": ["Theme 1", "Theme 2", "Theme 3"],
                "conclusion": "The philosophical ending."
            }},
            "overall_feedback": "The final verdict."
        }}
        """

        try:
            # Use Pro model for essays (1250 words) - Essential for large context analysis
            response = model_manager.generate_content(prompt, model_type='pro')
            response_text = response.text.strip()
            
            # Clean up potential markdown formatting
            # Clean up potential markdown formatting
            response_text = response_text.strip()
            if response_text.startswith("```"):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
                
            start = response_text.find('{')
            end = response_text.rfind('}')
            
            if start != -1 and end != -1:
                response_text = response_text[start:end+1]
                return json.loads(response_text)
            else:
                raise json.JSONDecodeError("No JSON found", response_text, 0)
        except Exception as e:
            print(f"Error evaluating essay: {e}")
            # Return fallback structure in case of error
            return {
                "score": 0,
                "strengths": ["Error in AI evaluation"],
                "weaknesses": ["Please try again later"],
                "suggestions": [],
                "model_structure": {
                    "introduction": "",
                    "body_paragraphs": [],
                    "conclusion": ""
                },
                "overall_feedback": "AI service temporarily unavailable."
            }
