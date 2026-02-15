## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2026-02-15 - Client-Side Price Trust in Legacy Shop
**Vulnerability:** The legacy `/buy` endpoint trusted the `cost` parameter sent by the client, allowing items to be purchased for arbitrary amounts.
**Learning:** Duplicate implementations (e.g., `shop.py` vs `shop_new.py`) can hide legacy vulnerabilities. While the new implementation was secure, the old one remained active and exposed.
**Prevention:** Audit all registered blueprints for legacy/duplicate endpoints. Ensure price lookups always happen server-side, never trust client-provided cost.
