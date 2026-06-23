## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.
## 2025-02-27 - Hardcoded API Key in Model Manager
**Vulnerability:** Found a hardcoded OpenClaw API key in `backend/app/services/model_manager.py` intended for local fallback.
**Learning:** Even fallback or alternative gateway credentials can be exposed if hardcoded in source control.
**Prevention:** Always default missing environment variables to empty strings and handle the error logically rather than hardcoding default API keys.
