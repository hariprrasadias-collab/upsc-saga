## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2024-05-25 - Hardcoded OPENCLAW_API_KEY in Model Manager
**Vulnerability:** A hardcoded API key was found as a fallback value for `OPENCLAW_API_KEY` in `backend/app/services/model_manager.py`.
**Learning:** Hardcoded credentials even as fallback values can be exposed if the source code is compromised, leading to unauthorized access.
**Prevention:** All API keys should be strictly loaded from environment variables or secure credential stores without default fallback values in code.
