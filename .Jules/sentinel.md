## 2024-05-23 - Hardcoded Secrets & Permissive CORS
**Vulnerability:** Found `app.secret_key` hardcoded in `backend/app/__init__.py` and CORS set to allow all origins (`*`).
**Learning:** Hardcoded secrets in source control defeat the purpose of session signing security. Permissive CORS allows any site to make requests to the API.
**Prevention:** Use `os.environ.get()` for all sensitive configuration. Enforce presence of secrets in production environments. Parse allowed origins from a comma-separated env var.
