import os
import google.generativeai as genai
import time

class AIModelWrapper:
    def __init__(self, models):
        self.models = models

    def generate_content(self, prompt):
        last_error = None
        for model_name in self.models:
            try:
                # print(f"🤖 AI Factory: Attempting with {model_name}...")
                model = genai.GenerativeModel(model_name)
                return model.generate_content(prompt)
            except Exception as e:
                print(f"⚠️ AI Factory: {model_name} failed: {e}")
                last_error = e
                continue
        
        # If all models failed, raise the last error
        print(f"❌ AI Factory Critical Failure: All models exhausted.")
        raise last_error

class AIModelFactory:
    _configured = False

    @staticmethod
    def configure():
        if not AIModelFactory._configured:
            api_key = os.environ.get('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                AIModelFactory._configured = True
            else:
                print("⚠️ AI Factory: GEMINI_API_KEY not found in environment")

    @staticmethod
    def get_model(strategy='speed'):
        """
        Returns a model wrapper based on the requested strategy.
        Strategies:
        - 'speed': Prioritizes Flash models (Cost/Speed) -> Pro
        - 'quality': Prioritizes Pro models (Reasoning) -> Flash
        - 'code': Prioritizes Code/Pro models
        """
        AIModelFactory.configure()
        
        if strategy == 'speed':
            # Flash -> Pro -> Standard
            return AIModelWrapper([
                'gemini-1.5-flash', 
                'gemini-flash-latest', 
                'gemini-1.5-pro', 
                'gemini-pro'
            ])
        elif strategy == 'quality':
            # Pro -> Flash -> Standard
            return AIModelWrapper([
                'gemini-1.5-pro', 
                'gemini-pro', 
                'gemini-1.5-flash'
            ])
        elif strategy == 'code':
             return AIModelWrapper([
                'gemini-2.0-flash-exp',
                'gemini-1.5-pro',
                'gemini-pro'
            ])
        else:
            # Default to speed
            return AIModelWrapper(['gemini-1.5-flash', 'gemini-pro'])
