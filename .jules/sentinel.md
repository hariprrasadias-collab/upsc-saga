## 2024-05-23 - Hardcoded Secrets in Config
**Vulnerability:** The application was initializing `app.secret_key` with a hardcoded string `'dev_secret_key_upsc_saga'` directly in `backend/app/__init__.py`. This could allow session forgery if deployed to production without modification.
**Learning:** Hardcoded secrets often hide in initialization logic under the guise of "default development values". While convenient, they become dangerous technical debt.
**Prevention:** Always use `os.environ.get('KEY')` for secrets. If a default is needed for dev, ensure it is clearly marked or conditional, and warn the user when the insecure default is active.
