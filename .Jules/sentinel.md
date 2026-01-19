## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2024-05-24 - Hardcoded Secret Key in Flask App
**Vulnerability:** The Flask application was initializing with a hardcoded `secret_key` ('dev_secret_key_upsc_saga') directly in the code, without checking for an environment variable override.
**Learning:** Even if a key is labeled "dev", hardcoding it makes it the default for all environments unless code is changed. Developers often forget to change this when deploying.
**Prevention:** Always use `os.getenv('KEY')` first. If a default is needed for dev convenience, make it explicit and warn if used in production.
