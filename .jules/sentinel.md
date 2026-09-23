## 2026-09-23 - Hardcoded API Key in ModelManager
**Vulnerability:** Hardcoded OPENCLAW_API_KEY in backend/app/services/model_manager.py
**Learning:** Found a hardcoded secret in the codebase instead of exclusively using environment variables. This creates a critical security risk where the key could be leaked if the code is public.
**Prevention:** Always use environment variables without a sensitive default string for API keys.
