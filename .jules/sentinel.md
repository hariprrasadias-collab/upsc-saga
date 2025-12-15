## 2024-05-23 - Hardcoded Flask Secret Key
**Vulnerability:** The Flask `SECRET_KEY` was hardcoded in `backend/app/__init__.py`.
**Learning:** Hardcoded secrets in source control are a common oversight, often left from initial development setup.
**Prevention:** Always use environment variables for sensitive configuration. Use a `load_dotenv` call at the application entry point to ensure `.env` files are respected.
