## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2025-06-03 - Parameter Tampering in Shop Purchase
**Vulnerability:** The `/api/shop/buy` endpoint blindly trusted the client-provided `cost` parameter, allowing users to purchase items for 0 cost.
**Learning:** Never trust client-side calculations for critical business logic like pricing. Developers often send the price from the frontend for convenience, but this is inherently insecure.
**Prevention:** Always maintain a server-side source of truth (e.g., database or hardcoded catalog) for item prices and ignore client-provided cost values during transactions.
