## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2024-06-12 - Hardcoded OPENCLAW_API_KEY
**Vulnerability:** A hardcoded API key was found in `backend/app/services/model_manager.py` as a fallback value for `os.environ.get('OPENCLAW_API_KEY')`.
**Learning:** Default arguments in environment variable fetching can unintentionally hardcode credentials into source code, creating a critical vulnerability.
**Prevention:** Always read credentials strictly from environment variables without hardcoded fallbacks, and use a `.env.example` file to document required keys.
