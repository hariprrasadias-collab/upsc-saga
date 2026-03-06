## 2024-05-24 - SQL Injection in Dynamic Limits
**Vulnerability:** Found a SQL injection vulnerability where a `limit` parameter from JSON input was directly interpolated into a SQL query string (`query += f" LIMIT {limit}"`).
**Learning:** Even simple integer parameters like `limit` or `offset` can be vectors for injection if not validated or parameterized. Developers often overlook these believing they will always be numbers.
**Prevention:** Always cast numeric inputs to their respective types (int/float) and use parameterized queries (`LIMIT ?`) even for standard SQL clauses. Never trust input types from JSON.

## 2025-02-24 - IDOR / Missing Server-Side Validation in Shop
**Vulnerability:** The `/api/shop/buy` endpoint blindly trusted the `cost` and `item_name` parameters sent by the client, allowing users to purchase items for arbitrary prices (e.g., 1 Hacksilver).
**Learning:** Legacy or redundant code (like `shop.py` existing alongside `shop_new.py`) can be a major security risk if not maintained or deprecated, as it might bypass newer security controls.
**Prevention:** Implement server-side catalogs for item prices and validate all transaction parameters against a trusted source of truth. Regularly audit and deprecate unused or legacy endpoints.
