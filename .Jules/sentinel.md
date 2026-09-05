## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2024-05-24 - Hardcoded Secret in Model Manager
**Vulnerability:** Found a hardcoded OpenClaw API key inside the ModelManager class.
**Learning:** API keys and sensitive tokens must never be hardcoded into the source code, as they can be extracted by unauthorized users who gain access to the codebase.
**Prevention:** Load all sensitive tokens and API keys exclusively from environment variables or secure credential managers, using appropriate defaults or empty strings when necessary to prevent exposure.
