## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2026-08-20 - Hardcoded API Key in Fallback
**Vulnerability:** A hardcoded API key for 'OPENCLAW_API_KEY' was left as a default fallback in os.environ.get().
**Learning:** Default fallback values in environment variable fetches can unintentionally expose real hardcoded secrets used during local development. These must be replaced with safe placeholders or removed.
**Prevention:** Never use real secrets as default fallback values in code. Use empty strings, None, or safe placeholder values (e.g., 'your-api-key-here') instead.
