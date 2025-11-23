# Answer Writing AI Evaluator using Gemini Pro
import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API (reusing existing setup)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

class AnswerEvaluator:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
    
    def evaluate_answer(self, question, answer_text, word_limit, keywords=None, model_answer=None):
        """
        Evaluates a UPSC answer using Gemini Pro AI
        
        Returns:
            dict: {
                overall_score: float,
                structure_score: float,
                content_score: float,
                relevance_score: float,
                keyword_coverage: float,
                strengths: list[str],
                improvements: list[str],
                missing_keywords: list[str]
            }
        """
        
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
            # Call Gemini API
            response = self.model.generate_content(evaluation_prompt)
            response_text = response.text.strip()
            
            # Clean response - remove markdown code blocks if present
            response_text = re.sub(r'```json\s*', '', response_text)
            response_text = re.sub(r'```\s*', '', response_text)
            response_text = response_text.strip()
            
            # Parse JSON
            evaluation = json.loads(response_text)
            
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
            print(f"Response: {response_text}")
            # Return default evaluation on error
            return self._get_default_evaluation(word_count, word_limit)
        
        except Exception as e:
            print(f"Evaluation Error: {e}")
            return self._get_default_evaluation(word_count, word_limit)
    
    def _get_default_evaluation(self, word_count, word_limit):
        """Fallback evaluation if AI fails"""
        return {
            'overall_score': 5.0,
            'structure_score': 5.0,
            'content_score': 5.0,
            'relevance_score': 5.0,
            'keyword_coverage': 50.0,
            'strengths': ["Answer submitted successfully"],
            'improvements': ["AI evaluation temporarily unavailable - try again later"],
            'missing_keywords': [],
            'word_count': word_count,
            'word_limit': word_limit,
            'word_limit_met': word_count <= word_limit * 1.1
        }

# Singleton instance
evaluator = AnswerEvaluator()

if __name__ == '__main__':
    # Test the evaluator
    test_question = "Discuss the role of local governance in strengthening democracy in India."
    test_answer = """Local governance plays a crucial role in strengthening democracy in India through decentralization and citizen participation. The 73rd and 74th Constitutional Amendments institutionalized Panchayati Raj, creating a three-tier structure of local self-government. This enables grass-root democracy where citizens directly participate in decision-making on local issues like sanitation, education, and infrastructure. Local governance ensures better accountability and efficient resource allocation. However, challenges like inadequate funding and political interference persist. Strengthening local governance requires financial devolution and capacity building."""
    
    result = evaluator.evaluate_answer(
        question=test_question,
        answer_text=test_answer,
        word_limit=150,
        keywords="local governance, panchayati raj, 73rd amendment, decentralization"
    )
    
    print(json.dumps(result, indent=2))
