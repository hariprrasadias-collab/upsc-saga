import os
import json
from dotenv import load_dotenv
from app.services.model_manager import model_manager

load_dotenv()

class EssayEvaluator:
    def __init__(self):
        pass # ModelManager handles initialization

    def evaluate_essay(self, topic, content):
        """
        Evaluates a UPSC essay using Gemini API.
        Returns a JSON object with score, strengths, weaknesses, and model structure.
        """
        prompt = f"""
        You are an expert UPSC Civil Services Exam evaluator. Evaluate the following essay based on official UPSC criteria:
        1. Relevance to the topic
        2. Coherence and flow
        3. Critical thinking and multi-dimensional analysis
        4. Effective use of examples/facts
        5. Structure (Intro, Body, Conclusion)

        Topic: "{topic}"
        
        Essay Content:
        "{content}"

        Provide your evaluation in the following STRICT JSON format:
        {{
            "score": <integer_between_0_and_250>,
            "strengths": ["point 1", "point 2", ...],
            "weaknesses": ["point 1", "point 2", ...],
            "suggestions": ["suggestion 1", "suggestion 2", ...],
            "model_structure": {{
                "introduction": "Brief description of an ideal intro",
                "body_paragraphs": ["Key argument 1", "Key argument 2", "Key argument 3"],
                "conclusion": "Brief description of an ideal conclusion"
            }},
            "overall_feedback": "A short summary paragraph."
        }}
        
        Do not include markdown formatting (```json). Just return the raw JSON string.
        """

        try:
            response = model_manager.generate_content(prompt)
            if hasattr(response, 'text'):
                response_text = response.text.strip()
            else:
                response_text = str(response)
            
            # Clean up potential markdown formatting
            response_text = response_text.replace('```json', '').replace('```', '').strip()
                
            return json.loads(response_text)
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
