# Answer Writing AI Evaluator using Gemini Pro
import os
import json
import re
from dotenv import load_dotenv
from app.services.model_manager import model_manager

load_dotenv()

# Configure Gemini API (Managed by ModelManager)

class AnswerEvaluator:
    def __init__(self):
        pass # ModelManager handles init
    
    def evaluate_answer(self, question, answer_text, word_limit, keywords=None, model_answer=None):
        """
        Evaluates a UPSC answer using Gemini Pro AI via ModelManager
        """
        if not model_manager.is_configured:
            return self._get_default_evaluation(0, word_limit, "AI Offline")

        # Count words
        word_count = len(answer_text.split())
        
        # Build evaluation prompt
        evaluation_prompt = f"""
        # MISSION: UPSC MAINS ANSWER EVALUATION (GS1/GS2/GS3/GS4)
        **Role:** Strict Mains Examiner.

        **QUESTION:** "{question}"
        **DIRECTIVE WORD:** (Identify if it is Discuss, Critically Analyze, Elucidate, etc. and score adherence).
        **WORD LIMIT:** {word_limit} (Actual: {word_count})

        **CANDIDATE ANSWER:**
        "{answer_text}"

        **EVALUATION PROTOCOL:**
        1. **Intro/Conclusion Check:** Does it define terms? Is the conclusion forward-looking?
        2. **Sub-heading Scan:** Are there clear sub-headings?
        3. **Data/Auth Check:** Did they cite a Report, Index, Article, or Case Law? If not, penalize Content Score.
        4. **Diagram Check:** Suggest where a diagram/flowchart could have been used.

        **OUTPUT SCHEMA (JSON ONLY):**
        {{
            "overall_score": <float 0-10>,
            "structure_score": <float 0-10>,
            "content_score": <float 0-10>,
            "relevance_score": <float 0-10>,
            "keyword_coverage": <float 0-100>,
            "directive_word_adherence": "Did they 'Discuss' or just 'List'?",
            "strengths": ["Strength 1", "Strength 2"],
            "improvements": ["Weakness 1", "Weakness 2"],
            "value_additions": ["Add: NITI Aayog Report X", "Add: Article Y"],
            "diagram_suggestion": "Draw a Hub-and-Spoke model for...",
            "missing_keywords": ["Keyword 1", "Keyword 2"],
            "model_answer_structure": ["Intro", "Body 1", "Body 2", "Conclusion"]
        }}
        """
        
        try:
            # Call Gemini API via Manager - Pro for deep analysis
            response = model_manager.generate_content(evaluation_prompt, model_type='pro')
            response_text = response.text.strip()
            
            if hasattr(response, 'text'):
                response_text = response.text.strip()
            else:
                response_text = str(response)

            if "Oracle is silent" in response_text:
                 return self._get_default_evaluation(word_count, word_limit, "AI Busy")

            # Clean response - remove markdown code blocks if present
            response_text = response_text.strip()
            
            # Robust Extraction
            if response_text.startswith("```"):
                 response_text = response_text.replace('```json', '').replace('```', '').strip()

            start = response_text.find('{')
            end = response_text.rfind('}')
            
            if start != -1 and end != -1:
                response_text = response_text[start:end+1]
                evaluation = json.loads(response_text)
            else:
                raise json.JSONDecodeError("No JSON object found", response_text, 0)
            
            # Validate and set defaults
            evaluation['overall_score'] = float(evaluation.get('overall_score', 5.0))
            evaluation['structure_score'] = float(evaluation.get('structure_score', 5.0))
            evaluation['content_score'] = float(evaluation.get('content_score', 5.0))
            evaluation['relevance_score'] = float(evaluation.get('relevance_score', 5.0))
            evaluation['keyword_coverage'] = float(evaluation.get('keyword_coverage', 50.0))
            
            # Ensure lists
            evaluation['strengths'] = evaluation.get('strengths', ["Answer provided"])
            evaluation['improvements'] = evaluation.get('improvements', ["Could add more depth"])
            evaluation['missing_keywords'] = evaluation.get('missing_keywords', [])
            
            # Add word count info
            evaluation['word_count'] = word_count
            evaluation['word_limit'] = word_limit
            evaluation['word_limit_met'] = word_count <= word_limit * 1.1  # 10% tolerance
            
            return evaluation
            
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            return self._get_default_evaluation(word_count, word_limit, "Parsing Error")
        
        except Exception as e:
            print(f"Evaluation Error: {e}")
            return self._get_default_evaluation(word_count, word_limit, "System Error")
    
    def _get_default_evaluation(self, word_count, word_limit, reason="unavailable"):
        """Fallback evaluation if AI fails"""
        return {
            'overall_score': 5.0,
            'structure_score': 5.0,
            'content_score': 5.0,
            'relevance_score': 5.0,
            'keyword_coverage': 50.0,
            'strengths': ["Answer submitted successfully"],
            'improvements': [f"AI evaluation temporarily {reason} - try again later"],
            'missing_keywords': [],
            'word_count': word_count,
            'word_limit': word_limit,
            'word_limit_met': word_count <= word_limit * 1.1
        }

# Singleton instance
evaluator = AnswerEvaluator()
