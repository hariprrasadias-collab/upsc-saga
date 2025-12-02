import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class EssayEvaluator:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro-latest')

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
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up potential markdown formatting
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                
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
