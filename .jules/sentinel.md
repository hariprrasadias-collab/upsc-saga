## 2026-03-13 - Hardcoded Fallback API Key in Model Manager
**Vulnerability:** A hardcoded API key for OpenClaw was present as a fallback in `os.environ.get()` within `backend/app/services/model_manager.py`.
**Learning:** Even if it's a 'local' or fallback service, hardcoding keys in source code is a critical vulnerability. It bypasses environment configuration and commits secrets to version control.
**Prevention:** Always rely strictly on environment variables for sensitive credentials (e.g., `os.environ.get('OPENCLAW_API_KEY')`) without providing a hardcoded fallback string. Conditionally initialize services only if their required keys are present.
