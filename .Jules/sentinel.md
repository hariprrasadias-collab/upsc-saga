## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2026-11-01 - Hardcoded Local Gateway Key (OpenClaw)
**Vulnerability:** A hardcoded API key (`d25c95eccbc569b1bc0d65699c5af9e39cea03ed39d728223f783dccf45616e0`) was present in the codebase for the OpenClaw local gateway initialization. Although for a local gateway, committing credentials in code is a serious risk if the model service is hosted remotely, or if it exposes internal access.
**Learning:** The fallback local model was given a default hardcoded key rather than properly handling a missing configuration state.
**Prevention:** Ensure `os.environ.get()` does not contain hardcoded credentials as a fallback value. Instead, safely check if the configuration exists and throw explicit errors or gracefully disable the local client initialization when missing.
