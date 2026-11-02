## 2025-02-14 - Fix Hardcoded API Key in OpenClaw Fallback
**Vulnerability:** A hardcoded default API key (`d25c...`) was present in `backend/app/services/model_manager.py` for the OpenClaw fallback model.
**Learning:** Even default fallback configurations for local API gateways should not contain hardcoded keys that could be exposed if the source code is public.
**Prevention:** Use `os.environ.get('KEY_NAME', None)` and ensure downstream logic handles the absence of the key gracefully, or use a truly non-secret fallback placeholder string explicitly marked as such (e.g. `dummy_local_key`), but best practice is to omit it entirely.
