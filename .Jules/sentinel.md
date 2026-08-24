## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2024-05-24 - Hardcoded Secret in Fallback Values
**Vulnerability:** Found a hardcoded API key (`d25c95eccbc569b1bc0d65699c5af9e39cea03ed39d728223f783dccf45616e0`) used as a default fallback value for `os.environ.get("OPENCLAW_API_KEY")` in `backend/app/services/model_manager.py`.
**Learning:** Default fallback values in `os.environ.get()` calls are often overlooked during security reviews because they appear to be fetching environment variables. Developers sometimes leave real development or testing secrets in these fallbacks.
**Prevention:** Never use real secrets as fallback values for environment variables. Always default to `None`, an empty string, or fail fast if a required secret is missing.
