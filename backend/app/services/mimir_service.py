import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class MimirService:
    def __init__(self):
        self.model = None
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            print("ERROR: GEMINI_API_KEY not found in environment variables")
            print(f"Current .env path: {os.path.join(os.getcwd(), '.env')}")
        else:
            print(f"SUCCESS: GEMINI_API_KEY loaded (length: {len(api_key)})")
            try:
                genai.configure(api_key=api_key)
                
                # Use models that are actually available in the API
                # Based on genai.list_models() output
                models_to_try = [
                    'gemini-flash-latest',          # Stable Flash alias
                    'gemini-pro-latest',            # Stable Pro alias
                ]
                
                model_initialized = False
                for model_name in models_to_try:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        print(f"SUCCESS: Gemini model initialized (using {model_name})")
                        model_initialized = True
                        break
                    except Exception as model_error:
                        print(f"Failed to initialize {model_name}: {model_error}")
                        continue
                
                if not model_initialized:
                    print("ERROR: All Gemini models failed to initialize")
                    print("This likely means:")
                    print("1. Your API key is invalid or expired")
                    print("2. You don't have access to Gemini API")
                    print("3. Your region/quota is restricted")
                    self.model = None
                    
            except Exception as e:
                print(f"ERROR: Failed to configure Gemini: {e}")
            
    def generate_response(self, message, history=[]):
        """
        Generate a response from Mimir using the Central Brain (Strategos).
        This enables Mimir to trigger actions and access full context.
        """
        try:
            from app.services.brain_service import brain_service
            
            # 1. Think (Reasoning & Decision)
            print(f"🧠 Mimir consulting Strategos for: '{message}'")
            brain_response = brain_service.think(message)
            
            response_text = brain_response.get('response_text', "I am lost in thought...")
            actions = brain_response.get('suggested_actions', [])
            
            # 2. Act (Execute suggested actions)
            if actions:
                response_text += "\n\n⚡ **Actions Taken:**"
                for action in actions:
                    action_type = action.get('type')
                    payload = action.get('payload', {})
                    
                    # Execute
                    result = brain_service.execute_action(action_type, payload)
                    
                    # Append result to response
                    if result.get('success'):
                        response_text += f"\n- ✅ {result.get('message')}"
                        # If action returned data (like analysis), append it
                        if result.get('analysis'):
                            response_text += f"\n\n**Analysis:**\n{result.get('analysis')}"
                        if result.get('explanation'):
                            response_text += f"\n\n**Insight:**\n{result.get('explanation')}"
                    else:
                        response_text += f"\n- ❌ Failed to {action_type}: {result.get('message')}"
            
            return response_text

        except Exception as e:
            print(f"ERROR generating Mimir response: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return f"I seem to have lost my connection to the Well of Wisdom. Error: {type(e).__name__}"

    def evaluate_answer(self, question, answer):
        if not self.model:
            return "I am currently offline. Please check my API key configuration."
            
        try:
            prompt = f"""
            You are an expert UPSC Mains Examiner. Evaluate the following answer based on the official UPSC rubric.
            
            Question: {question}
            
            Answer: {answer}
            
            Provide a detailed evaluation in strict JSON format with the following structure:
            {{
                "score": <float, 0-15>,
                "introduction_quality": "<string, brief assessment of the intro>",
                "body_quality": "<string, assessment of content, flow, and arguments>",
                "conclusion_quality": "<string, assessment of the conclusion>",
                "strengths": [<list of strings>],
                "weaknesses": [<list of strings>],
                "missing_keywords": [<list of strings, important terms missing from the answer>],
                "improvement_roadmap": [<list of strings, actionable steps to improve>],
                "model_answer_structure": "<string, brief outline of an ideal answer>"
            }}
            
            Do not include any markdown formatting (like ```json) in the response, just the raw JSON string.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating evaluation: {e}")
            return str(e)

mimir_service = MimirService()
