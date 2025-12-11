import os
from app.services.model_manager import model_manager
from dotenv import load_dotenv
from app.services.model_manager import model_manager

load_dotenv()

class MimirService:
    def __init__(self):
        pass # ModelManager handles initialization
            
    def generate_response(self, message, history=[]):
        """
        Generate a response from Mimir using the Central Brain (Strategos).
        This enables Mimir to trigger actions and access full context.
        """
        try:
            from app.services.brain_service import brain_service
            
            # 1. Think (Reasoning & Decision)
            # print(f"🧠 Mimir consulting Strategos for: '{message}'") # Reduced logs
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
            return f"I seem to have lost my connection to the Well of Wisdom. Error: {type(e).__name__}"

    def evaluate_answer(self, question, answer):
        try:
            prompt = f"""
            You are an expert UPSC Mains Examiner. Evaluate the following answer based on the official UPSC rubric.
            
            Question: {question}
            
            Answer: {answer}
            
            Provide a detailed evaluation in strict JSON format.
            """
            # Use ModelManager (Pro tier for evaluation)
            response = model_manager.generate_content(prompt, model_type='pro')
            return response.text
        except Exception as e:
            print(f"Error generating evaluation: {e}")
            return str(e)

mimir_service = MimirService()
