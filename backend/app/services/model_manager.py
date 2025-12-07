import os
import time
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, InternalServerError
from dotenv import load_dotenv

load_dotenv()

class ModelManager:
    """
    Centralized manager for Gemini models with automatic fallback and rotation
    to handle rate limits (429) and ensure high availability.
    """

    # Priority list of models to try
    # Start with faster/cheaper models, fall back to more capable/expensive ones if needed,
    # or just other tiers to bypass specific quota limits.
    MODEL_ROTATION = [
        'gemini-2.0-flash',
        'gemini-2.0-flash-001',
        'gemini-1.5-flash',
        'gemini-1.5-flash-latest',
        'gemini-1.5-pro',
        'gemini-1.5-pro-latest',
        'gemini-1.0-pro'
    ]

    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.current_model_index = 0
        self.models = {}  # Cache instantiated models
        self.is_configured = False

        if self.api_key:
            self._configure()
        else:
            print("⚠️ ModelManager Warning: GEMINI_API_KEY not found.")

    def _configure(self):
        try:
            genai.configure(api_key=self.api_key)
            self.is_configured = True
            print(f"✨ ModelManager Configured. Primary Model: {self.MODEL_ROTATION[0]}")
        except Exception as e:
            print(f"❌ ModelManager Configuration Failed: {e}")

    def get_model(self, model_name=None):
        """Get or instantiate a specific model or the current default."""
        if not self.is_configured:
            return None

        target_name = model_name or self.MODEL_ROTATION[self.current_model_index]

        if target_name not in self.models:
            try:
                self.models[target_name] = genai.GenerativeModel(target_name)
            except Exception as e:
                print(f"⚠️ Failed to instantiate {target_name}: {e}")
                return None

        return self.models.get(target_name)

    def switch_model(self):
        """Rotate to the next model in the list."""
        old_model = self.MODEL_ROTATION[self.current_model_index]
        self.current_model_index = (self.current_model_index + 1) % len(self.MODEL_ROTATION)
        new_model = self.MODEL_ROTATION[self.current_model_index]
        print(f"🔄 Switching Model: {old_model} -> {new_model} due to Quota/Error.")
        return new_model

    def generate_content(self, prompt, **kwargs):
        """
        Robust content generation with retry logic and model rotation.
        """
        if not self.is_configured:
            raise Exception("Gemini API Key missing")

        max_retries = len(self.MODEL_ROTATION) * 2 # Allow 2 cycles through all models
        attempts = 0

        while attempts < max_retries:
            current_model_name = self.MODEL_ROTATION[self.current_model_index]
            model = self.get_model(current_model_name)

            if not model:
                self.switch_model()
                attempts += 1
                continue

            try:
                # Add default generation config if needed, e.g., safety settings
                response = model.generate_content(prompt, **kwargs)
                return response

            except (ResourceExhausted, ServiceUnavailable, InternalServerError) as e:
                print(f"⚠️ API Error ({type(e).__name__}) with {current_model_name}: {e}")

                # Check for 429 specifically or ResourceExhausted
                if isinstance(e, ResourceExhausted) or "429" in str(e):
                    print("📉 Quota Exceeded. Rotating model...")
                    self.switch_model()
                    time.sleep(1) # Brief pause before retry
                else:
                    # For other transient errors, maybe just retry or switch
                    print("⚠️ Transient error. Rotating and retrying...")
                    self.switch_model()
                    time.sleep(2)

                attempts += 1

            except Exception as e:
                # Fatal errors or unknown errors
                print(f"❌ Unrecoverable Error with {current_model_name}: {e}")
                # If it's a parsing error or bad request, switching models might not help,
                # but we try once more just in case it's model specific.
                self.switch_model()
                attempts += 1

        raise Exception("All models failed to generate content after multiple retries.")

# Singleton Instance
model_manager = ModelManager()
