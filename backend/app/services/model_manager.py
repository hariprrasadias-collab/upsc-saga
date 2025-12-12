import os
import time
import random
import hashlib
from datetime import datetime, timedelta
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, InternalServerError
from dotenv import load_dotenv
from cachetools import TTLCache
import openai

load_dotenv()

class FallbackResponse:
    """A safe, mock response object mimicking genai.GenerateContentResponse"""
    def __init__(self, text):
        self.text = text

class ModelManager:
    """
    Centralized manager for Multi-Provider AI models (Gemini, OpenRouter, Chutes, Nvidia).
    Supports automatic fallback, rotation, caching, and cool-down logic.
    """

    # --- GOOGLE GEMINI MODELS ---
    GEMINI_PRO_MODELS = [
        'gemini-2.5-pro',
        'gemini-pro-latest'
    ]
    GEMINI_FAST_MODELS = [
        'gemini-2.5-flash',
        'gemini-2.0-flash-exp'
    ]

    # --- OPENROUTER MODELS (Tiered for Efficiency) ---
    
    # 1. FREE (Use for testing, simple echo, or when budget is 0)
    # Extensive list to handle rate limits via rotation
    OPENROUTER_FREE = [
        "google/gemini-2.0-flash-exp:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "microsoft/phi-3-medium-128k-instruct:free",
        "google/gemma-3-27b-it:free",
        "mistralai/mistral-7b-instruct:free",
        "openchat/openchat-7b:free",
        "nousresearch/hermes-3-llama-3.1-405b:free",
        "qwen/qwen-2-7b-instruct:free",
        "huggingfaceh4/zephyr-7b-beta:free",
        "nvidia/llama-3.1-nemotron-70b-instruct:free",
        "alibaba/tongyi-deepresearch-30b-a3b:free",
        "allenai/olmo-3-32b-think:free",
        "amazon/nova-2-lite-v1:free",
        "arcee-ai/trinity-mini:free",
        "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
        "kwaipilot/kat-coder-pro:free",
        "meituan/longcat-flash-chat:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        "mistralai/devstral-2512:free",
        "qwen/qwen3-coder:free",
        "z-ai/glm-4.5-air:free"
    ]

    # 2. ECONOMY (Best Value - High Intelligence / Low Cost)
    # Llama 3.1 70B is ~$0.40/M tokens, Haiku is ~$0.25/M
    OPENROUTER_ECONOMY = [
        "meta-llama/llama-3.1-70b-instruct",
        "anthropic/claude-3-haiku",
        "openai/gpt-4o-mini"
    ]

    # 3. PREMIUM (Maximum Intelligence - Higher Cost)
    # Use for complex reasoning, coding, or critical analysis.
    OPENROUTER_PREMIUM = [
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4o",
        "google/gemini-pro-1.5",
        "anthropic/claude-3.7-sonnet"
    ]

    # Combined list for rotation if needed (prefer specific tiers)
    # DEFAULTING TO FREE TIER AS REQUESTED
    OPENROUTER_MODELS = OPENROUTER_FREE + OPENROUTER_ECONOMY

    # --- NVIDIA NIM MODELS ---
    NVIDIA_MODELS = [
        'meta/llama-3.1-405b-instruct',
        'meta/llama-3.1-70b-instruct',
        'nvidia/nemotron-4-340b-instruct'
    ]

    def __init__(self):
        # 1. Google Setup
        self.google_api_key = os.environ.get('GEMINI_API_KEY')
        self.google_configured = False
        
        # 2. OpenAI-Compatible Providers Setup
        self.clients = {}
        
        # OpenRouter
        or_key = os.environ.get('OPENROUTER_API_KEY')
        if or_key:
            self.clients['openrouter'] = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=or_key,
                default_headers={
                    "HTTP-Referer": "https://github.com/hariprrasadias", 
                    "X-Title": "UPSC Second Brain"
                }
            )
            
        # Nvidia NIM
        nv_key = os.environ.get('NVIDIA_API_KEY')
        if nv_key:
             self.clients['nvidia'] = openai.OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=nv_key
            )

        # State Management
        self.current_indices = {'google_pro': 0, 'google_fast': 0, 'openrouter': 0, 'nvidia': 0}
        self.models_cache = {} 
        self.cooldowns = {}
        self.response_cache = TTLCache(maxsize=100, ttl=3600)
        self._panic_mode_until = None

        # Quota Governance
        self.DAILY_LIMIT = 1450
        self.TPM_LIMIT = 900000 
        self.quota_file = "backend/daily_quota.json"
        self.tpm_state = {'timestamp': time.time(), 'tokens': 0}

        if self.google_api_key:
            self._configure_google()
        else:
            print("⚠️ ModelManager Warning: GEMINI_API_KEY not found.")

        print(f"✨ ModelManager Ready. Active Providers: {list(self.clients.keys()) + (['google'] if self.google_configured else [])}")

    @property
    def is_configured(self):
        """Legacy property to check if ANY provider is configured."""
        return self.google_configured or bool(self.clients)

    def _configure_google(self):
        try:
            genai.configure(api_key=self.google_api_key)
            self.google_configured = True
        except Exception as e:
            print(f"❌ Google Configuration Failed: {e}")

    def _get_provider_for_model(self, model_name):
        """Determine which provider handles a given model."""
        if not model_name: return 'google'
        if model_name.startswith('gemini'): return 'google'
        if '/' in model_name: return 'openrouter' # Convention for OpenRouter
        if model_name in self.NVIDIA_MODELS: return 'nvidia'
        return 'openrouter' # Default fallback for non-gemini

    def get_model(self, model_name=None, model_type='fast'):
        """
        Legacy support for Gemini object retrieval. 
        For new providers, we stick to the client object.
        """
        if model_type == 'pro' or (model_name and model_name in self.GEMINI_PRO_MODELS):
             # Logic to return Gemini model object
             pass
        return None # Simplified for now, logic moved to generate_content

    def _is_in_cooldown(self, model_name):
        if model_name in self.cooldowns:
            if datetime.now() < self.cooldowns[model_name]:
                return True
            else:
                del self.cooldowns[model_name]
        return False

    def _mark_cooldown(self, model_name, duration_seconds=60):
        self.cooldowns[model_name] = datetime.now() + timedelta(seconds=duration_seconds)
        print(f"❄️ Model {model_name} in cool-down for {duration_seconds}s")

    def _check_panic_mode(self):
        if self._panic_mode_until:
            if datetime.now() < self._panic_mode_until:
                return True
            else:
                self._panic_mode_until = None
        return False

    def _trigger_panic_mode(self, duration_seconds=10):
        self._panic_mode_until = datetime.now() + timedelta(seconds=duration_seconds)
        print(f"🛑 PANIC MODE ACTIVATED: Skipping API calls for {duration_seconds}s")

    def _check_tpm_limit(self, prompt_len):
        est_tokens = prompt_len // 4
        now = time.time()
        if now - self.tpm_state['timestamp'] > 60:
            self.tpm_state = {'timestamp': now, 'tokens': 0}
        
        if self.tpm_state['tokens'] + est_tokens > self.TPM_LIMIT:
            wait_time = max(1, 60 - (now - self.tpm_state['timestamp']))
            print(f"⏳ TPM Limit. Throttling {wait_time:.1f}s...")
            time.sleep(wait_time)
            self.tpm_state = {'timestamp': time.time(), 'tokens': 0}
        self.tpm_state['tokens'] += est_tokens

    def _check_daily_quota(self):
        # Implementation similar to before, specifically for Google Free Tier
        # For paid APIS (OpenRouter/Nvidia), we generally skip this unless budget tracking is added
        return True 

    def _get_cache_key(self, prompt, model_name, kwargs):
        content = f"{prompt}|{model_name}|{str(sorted(kwargs.items()))}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

        return FallbackResponse("No response generated.")

    def generate_content(self, prompt, model_type='fast', model_name=None, provider=None, **kwargs):
        """
        Unified generation method with ROBUST FALLBACKS.
        """
        # Circuit Breaker
        if self._check_panic_mode(): 
            return FallbackResponse("System Offline (Panic Mode).")

        # 1. Determine Primary Strategy
        candidates = []

        # Helper to add candidate
        def add_candidate(prov, mod):
            candidates.append({'provider': prov, 'model': mod})

        # A. Explicit Request
        if provider and model_name:
            add_candidate(provider, model_name)
        
        # B. Automatic Strategy based on Type
        elif model_type == 'pro':
            # Priority 1: Google Pro
            add_candidate('google', self.GEMINI_PRO_MODELS[0])
            # Priority 2: Nvidia High-End (Free Trial)
            add_candidate('nvidia', 'meta/llama-3.1-405b-instruct')
            # Priority 3: OpenRouter Premium (if configured) or Top Free
            add_candidate('openrouter', self.OPENROUTER_MODELS[0])
            
        else: # 'fast'
            # Priority 1: Google Fast
            add_candidate('google', self.GEMINI_FAST_MODELS[0])
            # Priority 2: Nvidia 70B
            add_candidate('nvidia', 'meta/llama-3.1-70b-instruct') 
            # Priority 3: OpenRouter Free/Economy
            add_candidate('openrouter', self.OPENROUTER_FREE[0])

        # Always add a final "Hail Mary" fallback
        add_candidate('google', 'gemini-2.5-flash')
        add_candidate('openrouter', 'google/gemini-2.0-flash-exp:free')

        # Deduplicate candidates
        seen = set()
        unique_candidates = []
        for c in candidates:
            key = f"{c['provider']}:{c['model']}"
            if key not in seen:
                seen.add(key)
                unique_candidates.append(c)

        # 2. Execution Loop
        cache_key = self._get_cache_key(prompt, unique_candidates[0]['model'], kwargs)
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]

        errors = []
        for candidate in unique_candidates:
            tgt_prov = candidate['provider']
            tgt_model = candidate['model']
            
            print(f"🚀 Attempting with {tgt_prov} :: {tgt_model}...")

            try:
                response = None
                if tgt_prov == 'google':
                     response = self._generate_google(prompt, tgt_model, **kwargs)
                elif tgt_prov in self.clients:
                     response = self._generate_openai_compat(prompt, tgt_model, tgt_prov, **kwargs)
                
                if response:
                    print(f"✅ Success with {tgt_prov}")
                    self.response_cache[cache_key] = response
                    return response
            
            except Exception as e:
                err_msg = f"{tgt_prov} failed: {str(e)}"
                print(f"⚠️ {err_msg}")
                errors.append(err_msg)
                continue # Try next candidate

        # 3. Final Failure
        print("❌ All Fallbacks Failed.")
        return FallbackResponse(f"All providers failed. Errors: {'; '.join(errors)}")

    def _generate_google(self, prompt, model_name, **kwargs):
        if not self.google_configured: raise Exception("Google not configured")
        
        self._check_tpm_limit(len(prompt))
        
        # Simple rotation logic could be re-added here, keeping it simple for now
        model = genai.GenerativeModel(model_name)
        return model.generate_content(prompt, **kwargs)

    def _generate_openai_compat(self, prompt, model_name, provider_key, **kwargs):
        client = self.clients.get(provider_key)
        if not client: raise Exception(f"Client for {provider_key} not ready")
        
        # Convert internal kwargs to OpenAI format if needed
        # Mapping 'generation_config' etc. 
        
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            # Default params
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_output_tokens', 1024)
        )
        
        # Wrap response to mimic Google's object for backward compatibility
        text_content = completion.choices[0].message.content
        return FallbackResponse(text_content)

model_manager = ModelManager()
