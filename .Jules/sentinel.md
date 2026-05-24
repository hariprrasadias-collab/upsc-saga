## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2024-05-24 - [Remove Hardcoded API Key]
**Vulnerability:** A hardcoded `OPENCLAW_API_KEY` was found in `backend/app/services/model_manager.py` as a default fallback value.
**Learning:** Hardcoding API keys or secrets in source code, even as fallback defaults, poses a significant risk of leaking sensitive credentials if the code is exposed.
**Prevention:** Always rely entirely on environment variables or secure secret management services for keys. Provide empty strings or securely handle missing variables rather than embedding live defaults.
