import os
import time
import random
import hashlib
from datetime import datetime, timedelta
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, InternalServerError
from dotenv import load_dotenv
from cachetools import TTLCache

load_dotenv()

class ModelManager:
    """
    Centralized manager for Gemini models with automatic fallback, rotation,
    caching, and cool-down logic to handle rate limits (429) and ensure high availability.
    Supports Tiered usage: 'fast' (unlimited/high-quota) vs 'pro' (high-intelligence).
    """

    # High Intelligence Models (Low Rate Limit, High Cost)
    PRO_MODELS = [
        'gemini-1.5-pro',
        'gemini-1.5-pro-latest',
        'gemini-1.0-pro'
    ]

    # High Speed/Volume Models (High Rate Limit, Low Cost)
    FAST_MODELS = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-latest',
        'gemini-2.0-flash', # Experimental but fast
        'gemini-2.0-flash-001'
    ]

    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')

        # Track indices separately for each tier
        self.current_indices = {
            'pro': 0,
            'fast': 0
        }

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
            print(f"✨ ModelManager Configured. Fast: {self.FAST_MODELS[0]}, Pro: {self.PRO_MODELS[0]}")
        except Exception as e:
            print(f"❌ ModelManager Configuration Failed: {e}")

    def _get_model_list(self, model_type='fast'):
        if model_type == 'pro':
            return self.PRO_MODELS
        return self.FAST_MODELS

    def get_model(self, model_name=None, model_type='fast'):
        """Get or instantiate a specific model or the current default for the tier."""
        if not self.is_configured:
            return None

        # Determine target model name
        if model_name:
            target_name = model_name
        else:
            rotation = self._get_model_list(model_type)
            idx = self.current_indices.get(model_type, 0) % len(rotation)
            target_name = rotation[idx]

        # Check Cool-down
        if self._is_in_cooldown(target_name):
            # If current target is in cooldown, force switch to find a healthy one
            if not model_name: # Only switch if asking for 'default' for tier
                return self.switch_model(model_type)
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

    def switch_model(self, model_type='fast'):
        """Rotate to the next available healthy model within the tier."""
        rotation = self._get_model_list(model_type)
        start_index = self.current_indices.get(model_type, 0)
        attempts = 0
        total_models = len(rotation)

        while attempts < total_models:
            self.current_indices[model_type] = (self.current_indices[model_type] + 1) % total_models
            idx = self.current_indices[model_type]
            candidate_name = rotation[idx]

            if not self._is_in_cooldown(candidate_name):
                print(f"🔄 Switching to Healthy {model_type.upper()} Model: {candidate_name}")
                return self.get_model(candidate_name, model_type)

            attempts += 1

        # If all in cooldown, just pick the next one and hope for the best
        self.current_indices[model_type] = (start_index + 1) % total_models
        idx = self.current_indices[model_type]
        forced_model = rotation[idx]
        print(f"⚠️ All {model_type} models in cooldown. Forcing switch to: {forced_model}")
        return self.models.get(forced_model) or genai.GenerativeModel(forced_model)

    def _get_cache_key(self, prompt, model_type, kwargs):
        """Generate a stable hash key for caching."""
        # Simple hash of prompt + model_type + str(kwargs)
        content = f"{prompt}|{model_type}|{str(sorted(kwargs.items()))}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def generate_content(self, prompt, model_type='fast', **kwargs):
        """
        Robust content generation with:
        - Tiered Usage (Pro vs Fast)
        - Caching (TTL)
        - Exponential Backoff
        - Model Rotation
        - Cool-down Logic

        Args:
            prompt (str): The input prompt.
            model_type (str): 'fast' (default) or 'pro'.
            **kwargs: Additional arguments for genai.
        """
        if not self.is_configured:
            raise Exception("Gemini API Key missing")

        # 1. Check Cache
        cache_key = self._get_cache_key(prompt, model_type, kwargs)
        if cache_key in self.response_cache:
            # print("⚡ Returning Cached Response") # Debug
            return self.response_cache[cache_key]

        rotation = self._get_model_list(model_type)
        max_retries = len(rotation) * 2
        attempts = 0

        while attempts < max_retries:
            idx = self.current_indices.get(model_type, 0) % len(rotation)
            current_model_name = rotation[idx]

            # Ensure we have a model (get_model handles cooldown checks internally)
            model = self.get_model(model_name=current_model_name, model_type=model_type)

            if not model:
                # get_model might return None if implicit switch happened or instantiation failed
                # Try switching
                model = self.switch_model(model_type)
                if not model:
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

                self.switch_model(model_type)
                time.sleep(sleep_time)
                attempts += 1

            except Exception as e:
                print(f"❌ Unrecoverable Error with {current_model_name}: {e}")
                # Don't cooldown for generic logic errors, but do switch
                self.switch_model(model_type)
                attempts += 1

        raise Exception(f"All {model_type} models failed to generate content after multiple retries.")

# Singleton Instance
model_manager = ModelManager()
