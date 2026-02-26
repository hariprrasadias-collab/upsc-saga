## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2026-02-26 - Parameter Tampering in Commerce Logic
**Vulnerability:** The `/buy` endpoint trusted the `cost` provided by the client in the request body, allowing users to purchase items for 0 or negative cost.
**Learning:** Commerce logic must never trust client-side calculations or prices. The backend must always be the source of truth for pricing.
**Prevention:** Implement server-side catalogs for items and prices. Look up the price using the item ID instead of accepting it from the request. Validate that the user has sufficient funds based on the server-side price.
