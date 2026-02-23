## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2026-02-22 - Hardcoded Secret Key in Flask Init
**Vulnerability:** The application was initialized with a hardcoded `SECRET_KEY` in `backend/app/__init__.py`, with no mechanism to override it in production, and it was used as the default value.
**Learning:** Hardcoded default secrets often become production secrets if environment configuration is missed or fails. A "fail open" approach where a default weak key is used without warning is dangerous.
**Prevention:** Always use `os.environ.get('SECRET_KEY')`. If a default is necessary for development, ensure it triggers a critical warning in logs or fails to start in production environments.
