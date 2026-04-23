## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2026-04-23 - Hardcoded API Key Fallback in Model Manager
**Vulnerability:** Found a hardcoded OpenClaw API key (`d25c95eccbc569b1bc0d65699c5af9e39cea03ed39d728223f783dccf45616e0`) used as a fallback value for the `OPENCLAW_API_KEY` environment variable in `backend/app/services/model_manager.py`.
**Learning:** Hardcoded credentials in source code pose a critical security risk as they can be easily extracted and abused if the repository is exposed or shared. Fallbacks for sensitive values should be empty strings or `None` to force operators to explicitly provide credentials in secure configuration files (like `.env`).
**Prevention:** Always use empty strings `''` or `None` as defaults when fetching sensitive environment variables (e.g., `os.environ.get('SECRET', '')`). Never commit API keys, tokens, or passwords to the codebase, even as fallback defaults for local development.
