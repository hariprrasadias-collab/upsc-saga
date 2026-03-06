## 2024-05-18 - [CRITICAL] Hardcoded OpenClaw API Key
**Vulnerability:** Found a hardcoded OpenClaw API Key (`OPENCLAW_API_KEY`) set as a fallback in `backend/app/services/model_manager.py`. This exposes sensitive credentials in the source code.
**Learning:** Hardcoded credentials even as fallbacks or defaults pose a critical security risk because they get committed to version control and can be abused.
**Prevention:** Always rely strictly on environment variables (e.g., `os.environ.get('API_KEY')`) for sensitive credentials, and conditionally initialize services only if their required keys are present.
