## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2024-05-25 - Hardcoded Secret Key
**Vulnerability:** Found `SECRET_KEY` with an insecure fallback string even in production.
**Learning:** Frameworks often allow setting fallback secrets, but doing so compromises security in production deployments by defaulting to a known string if the env var fails to load.
**Prevention:** Always check the environment state (e.g. `FLASK_ENV == "production"`) and explicitly raise a `RuntimeError` if critical security variables are absent.
