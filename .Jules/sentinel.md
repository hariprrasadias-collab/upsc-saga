## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2024-05-24 - Hardcoded Secret Key in Application Root
**Vulnerability:** The Flask secret key was hardcoded as a string literal ('dev_secret_key_upsc_saga') in the application factory.
**Learning:** Boilerplate code often leaves default secrets that persist into production if not explicitly parameterized. Checking for 'secret' or 'key' strings in `__init__.py` is a high-yield scan.
**Prevention:** Always use `os.getenv('KEY', 'dev_fallback')` and ensure `python-dotenv` is loaded at application startup.
