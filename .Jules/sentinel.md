## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2026-07-23 - Hardcoded API Key in model_manager.py
**Vulnerability:** A hardcoded API key was found as a fallback for the `OPENCLAW_API_KEY` environment variable in `backend/app/services/model_manager.py`.
**Learning:** Hardcoded credentials are a critical security vulnerability, as they can be easily extracted from the source code and used by unauthorized parties. Even as a fallback, sensitive keys should never be committed to version control.
**Prevention:** Always load sensitive credentials from environment variables or secure secret management systems without providing hardcoded default values in the code.
