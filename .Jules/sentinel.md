## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2025-02-28 - Hardcoded API Key Fallback
**Vulnerability:** Found a hardcoded API key used as a fallback (`OPENCLAW_API_KEY`) in `ModelManager` (located at `backend/app/services/model_manager.py`).
**Learning:** Hardcoded secrets in code can be leaked if the repository is made public or accessed by unauthorized individuals. A default secret provided in code defeats the purpose of an API key because it becomes universally known.
**Prevention:** Always rely strictly on environment variables for API keys and never provide hardcoded string values as fallbacks. Conditionally instantiate services based on the presence of the API key.
