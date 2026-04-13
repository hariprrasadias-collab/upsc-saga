
## 2024-05-18 - Fix IDOR in Lore routes
**Vulnerability:** Insecure Direct Object Reference (IDOR) where users could arbitrarily modify and delete other users' Lore records because `PUT` and `DELETE` routes were missing ownership validation (`user_id`). The queries only relied on the resource `id`.
**Learning:** All resources associated with a user account must inherently be verified for ownership using `get_current_user_id()` combined with `AND user_id=?` in update and delete queries, even if the user is authenticated.
**Prevention:** Always scope database modification commands to `WHERE id=? AND user_id=?` to ensure the requester owns the target resource before modifying it.
