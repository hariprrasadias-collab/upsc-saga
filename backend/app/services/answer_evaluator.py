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
You are an expert UPSC Mains examiner with 20+ years of experience. Evaluate this answer strictly according to UPSC standards.

QUESTION:
{question}

WORD LIMIT: {word_limit} words
ACTUAL WORDS: {word_count} words

EXPECTED KEYWORDS:
{keywords or 'Not provided'}

STUDENT'S ANSWER:
{answer_text}

{"MODEL ANSWER (for reference):" + model_answer if model_answer else ""}

Evaluate the answer on the following criteria:

1. STRUCTURE (0-10): Introduction, logical flow, paragraph organization, conclusion
2. CONTENT (0-10): Factual accuracy, depth of analysis, examples, critical thinking, dimensions covered
3. RELEVANCE (0-10): Direct answer to question, no deviation, balanced approach
4. KEYWORD COVERAGE (0-100%): Percentage of expected keywords present

Provide your evaluation in STRICT JSON format (NO markdown, NO code blocks, ONLY valid JSON):

{{
  "overall_score": <float 0-10>,
  "structure_score": <float 0-10>,
  "content_score": <float 0-10>,
  "relevance_score": <float 0-10>,
  "keyword_coverage": <float 0-100>,
  "strengths": ["specific strength 1", "specific strength 2", "specific strength 3"],
  "improvements": ["specific improvement 1", "specific improvement 2", "specific improvement 3"],
  "missing_keywords": ["keyword1", "keyword2"],
  "word_limit_feedback": "comment on word count adherence"
}}

Be constructive but honest. Focus on UPSC-specific requirements: multidimensional analysis, factual accuracy, balanced perspective, and answer framework.
"""
        
        try:
            # Call Gemini API via Manager
            response = model_manager.generate_content(evaluation_prompt, model_type='fast')
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
