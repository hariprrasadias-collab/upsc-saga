## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2024-05-27 - Hardcoded API Key Fallback
**Vulnerability:** A hardcoded `OPENCLAW_API_KEY` was found being used as a fallback value in `os.environ.get()` within `backend/app/services/model_manager.py`.
**Learning:** Default fallback values in environment variable lookups across the codebase may contain real, hardcoded secrets previously used for local development rather than safe placeholders.
**Prevention:** Never hardcode secrets in code, even as fallback values. Use empty strings or `None` and enforce environment configuration for local development.
