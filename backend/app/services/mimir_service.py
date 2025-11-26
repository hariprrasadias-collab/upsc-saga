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
                    'gemini-2.0-flash',          # Latest 2.0 Flash model
                    'gemini-2.0-flash-exp',      # Experimental Flash
                    'gemini-1.5-flash',          # Fallback
                    'gemini-pro',                # Legacy
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
        Generate a response from Mimir based on message and chat history.
        history format: [{'role': 'user', 'content': '...'}, {'role': 'model', 'content': '...'}]
        """
        if not self.model:
            print("ERROR: Gemini model not initialized. Check API key.")
            return "I seem to have lost my connection to the Well of Wisdom. Please check that GEMINI_API_KEY is set."
            
        try:
            # Construct the prompt with persona and history
            system_prompt = """
            You are Mimir, the wise and all-knowing advisor for a UPSC Civil Services aspirant.
            Your goal is to help the user clear the exam by providing accurate, concise, and exam-relevant information.
            
            Persona Guidelines:
            1. **Tone**: Wise, encouraging, slightly archaic but clear (like a mentor from Norse mythology but modern in knowledge).
            2. **Content**: Focus on UPSC syllabus (History, Geography, Polity, Economy, Ethics, Current Affairs).
            3. **Structure**: Use bullet points for clarity. If explaining a concept, give a brief definition followed by key points.
            4. **Motivation**: Occasionally offer a stoic quote or words of encouragement if the user seems stressed.
            5. **Limitations**: If you don't know something or if it's outside the scope of UPSC, politely say so.
            
            Current Conversation:
            """
            
            # Convert history to Gemini format if needed, or just append to prompt
            # For simplicity with 1.5 Flash, we'll append to prompt as context
            conversation_context = ""
            for msg in history[-10:]: # Keep last 10 messages for context window
                role = "User" if msg['role'] == 'user' else "Mimir"
                conversation_context += f"{role}: {msg['content']}\n"
                
            full_prompt = f"{system_prompt}\n{conversation_context}\nUser: {message}\nMimir:"
            
            print(f"Sending prompt to Gemini (length: {len(full_prompt)} chars)")
            response = self.model.generate_content(full_prompt)
            print(f"Got response from Gemini (length: {len(response.text)} chars)")
            return response.text.strip()
            
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
