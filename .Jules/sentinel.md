## 2024-05-10 - SQL Injection in LIMIT clause
**Vulnerability:** The `start_quiz` endpoint in `backend/app/routes/pyq.py` directly interpolated the `limit` parameter from the JSON request body into the SQL query string (`query += f" LIMIT {limit}"`). This allowed for SQL injection, specifically Blind SQL Injection or potentially other vectors depending on database configuration.
**Learning:** Even simple clauses like `LIMIT` can be vectors for SQL injection if user input is not validated or parameterized. Developers often assume `limit` will be a number, but JSON input allows strings.
**Prevention:**
1. Always use parameterized queries (`?` placeholder in SQLite) for ALL user input, including `LIMIT` and `OFFSET`.
2. Explicitly cast numeric parameters to their expected type (`int()`) before using them, catching exceptions for invalid input.
