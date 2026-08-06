## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2024-05-24 - [Hardcoded API Key in default fallback]
**Vulnerability:** A hardcoded API key (OPENCLAW_API_KEY) was found as the default fallback value in os.environ.get().
**Learning:** Default fallback values in environment variable getters across the codebase should be reviewed, as they might contain real secrets previously used for local development rather than safe placeholders.
**Prevention:** Avoid placing real API keys in fallback parameters of os.environ.get(). Ensure default values are empty strings, None, or explicit placeholder strings (e.g., 'YOUR_API_KEY').
