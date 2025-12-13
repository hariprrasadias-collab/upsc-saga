import os
import time
import json
import random
import hashlib
from datetime import datetime, timedelta
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, InternalServerError
from dotenv import load_dotenv
from cachetools import TTLCache
import openai
from openai import OpenAI

load_dotenv()

class FallbackResponse:
    """A safe, mock response object mimicking genai.GenerateContentResponse"""
    def __init__(self, text, candidates=None):
        self.text = text
        self.candidates = candidates or []

class ModelManager:
    """
    Centralized manager for Multi-Provider AI models (Gemini, OpenRouter, Chutes, Nvidia).
    Supports automatic fallback, rotation, caching, and persistent quota tracking.
    """

    # --- GOOGLE GEMINI MODELS ---
    GEMINI_PRO_MODELS = [
        'gemini-2.0-pro-exp-02-05',
        'gemini-1.5-pro',
        'gemini-pro'
    ]
    GEMINI_FAST_MODELS = [
        'gemini-2.0-flash',
        'gemini-2.0-flash-lite-preview-02-05',
        'gemini-1.5-flash'
    ]

    # --- OPENROUTER MODELS (Tiered for Efficiency) ---
    OPENROUTER_FREE = [
        "google/gemini-2.0-flash-lite-preview-02-05:free",
        "google/gemini-2.0-pro-exp-02-05:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "deepseek/deepseek-r1:free",
        "deepseek/deepseek-chat:free",
        "microsoft/phi-3-medium-128k-instruct:free",
        "google/gemma-2-9b-it:free",
        "mistralai/mistral-7b-instruct:free",
        "openchat/openchat-7b:free",
        "nousresearch/hermes-3-llama-3.1-405b:free",
        "qwen/qwen-2-7b-instruct:free",
        "nvidia/llama-3.1-nemotron-70b-instruct:free",
    ]

    OPENROUTER_PREMIUM = [
        "anthropic/claude-3.7-sonnet",
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4o",
        "google/gemini-pro-1.5",
    ]

    # --- NVIDIA NIM MODELS ---
    NVIDIA_MODELS_PRO = [
        'meta/llama-3.1-405b-instruct',
        'nvidia/nemotron-4-340b-instruct'
    ]

    NVIDIA_MODELS_FAST = [
        'meta/llama-3.1-70b-instruct',
        'meta/llama-3.1-8b-instruct',
        'mistralai/mixtral-8x22b-instruct-v0.1'
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
                    "HTTP-Referer": "https://github.com/hariprrasadias/upsc-saga",
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
        self.response_cache = TTLCache(maxsize=200, ttl=3600)
        self._panic_mode_until = None

        # Quota Persistence
        self.quota_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'services', 'quota_status.json')
        self.quota_status = self._load_quota_status()

        if self.google_api_key:
            self._configure_google()
        else:
            print("⚠️ ModelManager Warning: GEMINI_API_KEY not found.")

        print(f"✨ ModelManager Ready. Active Providers: {list(self.clients.keys()) + (['google'] if self.google_configured else [])}")

    @property
    def is_configured(self):
        """Check if ANY provider is configured."""
        return self.google_configured or bool(self.clients)

    def _configure_google(self):
        try:
            genai.configure(api_key=self.google_api_key)
            self.google_configured = True
        except Exception as e:
            print(f"❌ Google Configuration Failed: {e}")

    # --- QUOTA MANAGEMENT ---

    def _load_quota_status(self):
        try:
            if os.path.exists(self.quota_file):
                with open(self.quota_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Failed to load quota file: {e}")
        return {}

    def _save_quota_status(self):
        try:
            # Clean up expired entries before saving
            now = datetime.now().isoformat()
            self.quota_status = {k: v for k, v in self.quota_status.items() if v > now}

            with open(self.quota_file, 'w') as f:
                json.dump(self.quota_status, f)
        except Exception as e:
            print(f"Failed to save quota file: {e}")

    def _is_quota_exceeded(self, provider, model_name):
        key = f"{provider}:{model_name}"
        if key in self.quota_status:
            unlock_time_str = self.quota_status[key]
            unlock_time = datetime.fromisoformat(unlock_time_str)
            if datetime.now() < unlock_time:
                # print(f"⏳ Model {key} is on cooldown until {unlock_time}")
                return True
            else:
                del self.quota_status[key]
                self._save_quota_status()
        return False

    def _mark_quota_exceeded(self, provider, model_name):
        """Marks a model as quota exceeded for 24 hours."""
        key = f"{provider}:{model_name}"
        unlock_time = datetime.now() + timedelta(hours=24)
        self.quota_status[key] = unlock_time.isoformat()
        self._save_quota_status()
        print(f"⛔ Model {key} marked as QUOTA EXCEEDED until {unlock_time}")

    def _get_cache_key(self, prompt, model_name, kwargs):
        content = f"{prompt}|{model_name}|{str(sorted(kwargs.items()))}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def generate_content(self, prompt, model_type='fast', model_name=None, provider=None, **kwargs):
        """
        Unified generation method with ROBUST FALLBACKS and QUOTA MANAGEMENT.
        """
        # 1. Determine Strategy and Build Candidates List
        candidates = []

        # Helper to add candidate
        def add_candidate(prov, mod):
            if not self._is_quota_exceeded(prov, mod):
                candidates.append({'provider': prov, 'model': mod})

        # A. Explicit Request
        if provider and model_name:
            add_candidate(provider, model_name)
        
        # B. Automatic Strategy based on Type
        elif model_type == 'pro':
            # Priority 1: Nvidia High-End (Complex Tasks)
            for m in self.NVIDIA_MODELS_PRO:
                add_candidate('nvidia', m)

            # Priority 2: Google Pro
            for m in self.GEMINI_PRO_MODELS:
                add_candidate('google', m)

            # Priority 3: OpenRouter Premium/Free Top Tier
            for m in self.OPENROUTER_PREMIUM: # Only if user pays, but list exists
                 add_candidate('openrouter', m)
            for m in self.OPENROUTER_FREE:
                if '405b' in m or 'deepseek-r1' in m: # Prioritize smarter free models
                    add_candidate('openrouter', m)
            
        else: # 'fast'
            # Priority 1: Nvidia Fast
            for m in self.NVIDIA_MODELS_FAST:
                add_candidate('nvidia', m)

            # Priority 2: OpenRouter Free (Top ones)
            for m in self.OPENROUTER_FREE:
                 add_candidate('openrouter', m)

            # Priority 3: Google Fast
            for m in self.GEMINI_FAST_MODELS:
                add_candidate('google', m)

        # Fallback: Always ensure at least some models are in the list if everything else is exhausted
        if not candidates:
             # Force add base models even if "quota exceeded" check failed (desperate measure) or just add if list empty
             print("⚠️ Warning: All preferred models seem exhausted. Attempting Hail Mary.")
             candidates.append({'provider': 'google', 'model': 'gemini-2.0-flash'})
             candidates.append({'provider': 'openrouter', 'model': 'google/gemini-2.0-flash-exp:free'})

        # Deduplicate candidates while preserving order
        seen = set()
        unique_candidates = []
        for c in candidates:
            key = f"{c['provider']}:{c['model']}"
            if key not in seen:
                seen.add(key)
                unique_candidates.append(c)

        # 2. Execution Loop
        # Check cache for the primary candidate (best effort cache key)
        if unique_candidates:
             cache_key = self._get_cache_key(prompt, unique_candidates[0]['model'], kwargs)
             if cache_key in self.response_cache:
                 print("⚡ Returning cached response.")
                 return self.response_cache[cache_key]

        errors = []
        for candidate in unique_candidates:
            tgt_prov = candidate['provider']
            tgt_model = candidate['model']
            
            # Skip if provider not configured
            if tgt_prov != 'google' and tgt_prov not in self.clients:
                continue
            if tgt_prov == 'google' and not self.google_configured:
                continue

            print(f"🚀 Attempting with {tgt_prov} :: {tgt_model}...")

            try:
                response = None
                start_time = time.time()

                if tgt_prov == 'google':
                     response = self._generate_google(prompt, tgt_model, **kwargs)
                elif tgt_prov in self.clients:
                     response = self._generate_openai_compat(prompt, tgt_model, tgt_prov, **kwargs)
                
                if response:
                    duration = time.time() - start_time
                    print(f"✅ Success with {tgt_prov} ({duration:.2f}s)")

                    # Cache successful response
                    if unique_candidates:
                         cache_key = self._get_cache_key(prompt, unique_candidates[0]['model'], kwargs)
                         self.response_cache[cache_key] = response

                    return response
            
            except Exception as e:
                err_str = str(e).lower()
                print(f"⚠️ {tgt_prov} ({tgt_model}) failed: {str(e)}")

                # Intelligent Quota Handling
                if "429" in err_str or "quota" in err_str or "resource exhausted" in err_str or "credit" in err_str:
                    self._mark_quota_exceeded(tgt_prov, tgt_model)

                errors.append(f"{tgt_prov}:{tgt_model} -> {str(e)}")
                continue # Try next candidate

        # 3. Final Failure
        print("❌ All Fallbacks Failed.")
        return FallbackResponse(f"Oracle is silent. All providers failed. Errors: {'; '.join(errors)}")

    def _generate_google(self, prompt, model_name, **kwargs):
        if not self.google_configured: raise Exception("Google not configured")
        
        # Map generic kwargs to Gemini specific if needed
        gen_config = genai.types.GenerationConfig(
            temperature=kwargs.get('temperature', 0.7),
            max_output_tokens=kwargs.get('max_output_tokens', 2048)
        )
        
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt, generation_config=gen_config)
        return FallbackResponse(response.text)

    def _generate_openai_compat(self, prompt, model_name, provider_key, **kwargs):
        client = self.clients.get(provider_key)
        if not client: raise Exception(f"Client for {provider_key} not ready")
        
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_output_tokens', 2048)
        )
        
        text_content = completion.choices[0].message.content
        return FallbackResponse(text_content)

model_manager = ModelManager()
