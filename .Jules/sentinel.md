## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2024-07-28 - Hardcoded Secret Removal
**Vulnerability:** Found a hardcoded OpenClaw API key (`d25c95ec...16e0`) used as a fallback in `backend/app/services/model_manager.py`.
**Learning:** Hardcoding API keys, even as fallbacks for local gateways, exposes sensitive credentials to version control and potential unauthorized access.
**Prevention:** Always rely on environment variables (`os.environ.get()`) without insecure default string values for credentials.
