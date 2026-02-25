## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2024-05-24 - Client-Side Price Trust
**Vulnerability:** The `/api/shop/buy` endpoint blindly trusted the `cost` parameter sent by the client, allowing users to purchase items for 0 cost.
**Learning:** Developers sometimes rely on the frontend to calculate prices and pass them to the backend, assuming users won't tamper with the request.
**Prevention:** Never trust client-side pricing. The backend must always look up the price from a trusted source (database or catalog) based on the item ID.
