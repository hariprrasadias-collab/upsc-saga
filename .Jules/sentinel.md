## 2025-02-28 - Parameter Tampering in Shop Purchase
**Vulnerability:** Found a parameter tampering vulnerability where the `cost` of an item in the `/api/shop/buy` endpoint was taken directly from the client request, allowing users to purchase items for negligible amounts.
**Learning:** Never trust client-side data for critical business logic like pricing or inventory. Client-side validation is easily bypassed.
**Prevention:** Implement a server-side source of truth (e.g., a database catalog or hardcoded constant) for item prices and validate the `item_id` against this source before processing the transaction. Ensure the cost used for deduction comes from the trusted server source, not the client request.
