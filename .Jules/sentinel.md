## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2026-02-19 - Mass Assignment in E-Commerce (Shop)
**Vulnerability:** The `/buy` endpoint trusted the `cost` provided in the client's request body, allowing users to set their own prices (e.g., buying a 200-hacksilver item for 1 hacksilver). This is a classic Mass Assignment / Business Logic Flaw.
**Learning:** Never trust client-side data for sensitive business logic like pricing. Even if the frontend sends the correct price, a malicious actor can bypass the frontend and send a modified payload.
**Prevention:** Always validate critical parameters server-side. For pricing, use a trusted source of truth (database or hardcoded catalog) and ignore client-provided cost values entirely.
