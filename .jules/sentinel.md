## 2026-10-03 - [Remove hardcoded OPENCLAW_API_KEY]
**Vulnerability:** A hardcoded, high-entropy fallback API key for OPENCLAW_API_KEY was found in `backend/app/services/model_manager.py`.
**Learning:** Hardcoding secrets as fallbacks in environment variable retrievals exposes the secret if the code is pushed to a repository.
**Prevention:** Always ensure fallback values for sensitive keys are either `None` or not hardcoded strings. Manage all keys securely through the environment.
