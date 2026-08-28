## 2024-05-24 - [Fix Hardcoded Secret in ModelManager]
**Vulnerability:** A hardcoded API key was found in the fallback parameter for `OPENCLAW_API_KEY` in `backend/app/services/model_manager.py`.
**Learning:** Hardcoded credentials even for local gateway fallback mechanisms can lead to unintentional leakage if code is published or shared.
**Prevention:** Rely strictly on environment variables for API keys and secrets, even for local environments.
