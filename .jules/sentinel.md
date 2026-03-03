## 2025-03-03 - Removed hardcoded API key in fallback models
**Vulnerability:** A hardcoded API key for OpenClaw was present as a default fallback value in `backend/app/services/model_manager.py` within `os.environ.get()`.
**Learning:** Hardcoded secrets can easily leak into version control and be exploited by anyone who accesses the repository.
**Prevention:** Always rely strictly on environment variables or secure vault services for accessing keys, passwords, and tokens.
