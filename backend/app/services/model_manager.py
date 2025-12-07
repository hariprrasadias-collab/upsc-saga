import os
import time
import random
import hashlib
from datetime import datetime, timedelta
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, InternalServerError, NotFound, InvalidArgument
from dotenv import load_dotenv
from cachetools import TTLCache

load_dotenv()

class ModelManager:
    """
    Centralized manager for Gemini models with automatic fallback, rotation,
    caching, and cool-down logic to handle rate limits (429) and ensure high availability.
    """

    # Priority list of models to try (Based on 'list_models.py' output)
    MODEL_ROTATION = [
        'gemini-2.0-flash',
        'gemini-2.0-flash-001',
        'gemini-2.0-flash-lite-preview-02-05',
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-2.0-pro-exp-02-05'
    ]

    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.current_model_index = 0
        self.models = {}  # Cache instantiated models
        self.is_configured = False

        # Smart Features
        self.cooldowns = {} # Map model_name -> datetime until available
        self.response_cache = TTLCache(maxsize=100, ttl=3600) # 1 Hour Cache

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

        # Check Cool-down
        if self._is_in_cooldown(target_name):
            # If current target is in cooldown, force switch to find a healthy one
            if not model_name: # Only switch if asking for 'default'
                return self.switch_model()
            else:
                return None # Explicitly requested model is down

        if target_name not in self.models:
            try:
                self.models[target_name] = genai.GenerativeModel(target_name)
            except Exception as e:
                print(f"⚠️ Failed to instantiate {target_name}: {e}")
                return None

        return self.models.get(target_name)

    def _is_in_cooldown(self, model_name):
        """Check if a model is currently in cool-down period."""
        if model_name in self.cooldowns:
            if datetime.now() < self.cooldowns[model_name]:
                return True
            else:
                del self.cooldowns[model_name] # Expired
        return False

    def _mark_cooldown(self, model_name, duration_seconds=60):
        """Mark a model as unavailable for a duration."""
        self.cooldowns[model_name] = datetime.now() + timedelta(seconds=duration_seconds)
        print(f"❄️ Model {model_name} in cool-down for {duration_seconds}s")

    def switch_model(self):
        """Rotate to the next available healthy model."""
        start_index = self.current_model_index
        attempts = 0
        total_models = len(self.MODEL_ROTATION)

        while attempts < total_models:
            self.current_model_index = (self.current_model_index + 1) % total_models
            candidate_name = self.MODEL_ROTATION[self.current_model_index]

            if not self._is_in_cooldown(candidate_name):
                print(f"🔄 Switching to Healthy Model: {candidate_name}")
                return self.get_model(candidate_name)

            attempts += 1

        # If all in cooldown, just pick the next one and hope for the best
        self.current_model_index = (start_index + 1) % total_models
        forced_model = self.MODEL_ROTATION[self.current_model_index]
        print(f"⚠️ All models in cooldown. Forcing switch to: {forced_model}")
        return self.models.get(forced_model) or genai.GenerativeModel(forced_model)

    def _get_cache_key(self, prompt, kwargs):
        """Generate a stable hash key for caching."""
        # Simple hash of prompt + str(kwargs)
        content = f"{prompt}|{str(sorted(kwargs.items()))}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def generate_content(self, prompt, **kwargs):
        """
        Robust content generation with:
        - Caching (TTL)
        - Exponential Backoff
        - Model Rotation
        - Cool-down Logic
        """
        if not self.is_configured:
            raise Exception("Gemini API Key missing")

        # 1. Check Cache
        cache_key = self._get_cache_key(prompt, kwargs)
        if cache_key in self.response_cache:
            # print("⚡ Returning Cached Response") # Debug
            return self.response_cache[cache_key]

        max_retries = len(self.MODEL_ROTATION) * 2
        attempts = 0

        while attempts < max_retries:
            current_model_name = self.MODEL_ROTATION[self.current_model_index]

            # Ensure we have a model (get_model handles cooldown checks internally)
            model = self.get_model(current_model_name)

            if not model:
                # get_model might return None if implicit switch happened or instantiation failed
                # Try getting the current one again (which might have updated index)
                model = self.models.get(self.MODEL_ROTATION[self.current_model_index])
                if not model:
                     self.switch_model()
                     attempts += 1
                     continue

            try:
                response = model.generate_content(prompt, **kwargs)

                # Cache successful response
                self.response_cache[cache_key] = response
                return response

            except (ResourceExhausted, ServiceUnavailable, InternalServerError) as e:
                print(f"⚠️ API Error ({type(e).__name__}) with {current_model_name}: {e}")

                # Mark for cooldown
                self._mark_cooldown(current_model_name, duration_seconds=60)

                # Exponential Backoff
                sleep_time = min(2 ** attempts, 30) + random.uniform(0, 1)
                print(f"📉 Rotating & Sleeping {sleep_time:.2f}s...")

                self.switch_model()
                time.sleep(sleep_time)
                attempts += 1

            except (NotFound, InvalidArgument) as e:
                # 404/400 Errors - Model likely invalid or deprecated
                print(f"❌ Invalid Model {current_model_name}: {e}. Removing from rotation.")
                self.MODEL_ROTATION.remove(current_model_name)
                # Don't increment attempts heavily, just switch instantly
                self.switch_model()

            except Exception as e:
                print(f"❌ Unrecoverable Error with {current_model_name}: {e}")
                # Don't cooldown for generic logic errors, but do switch
                self.switch_model()
                attempts += 1

        raise Exception("All models failed to generate content after multiple retries.")

# Singleton Instance
model_manager = ModelManager()
