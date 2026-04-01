
## 2024-04-01 - Prevent N+1 queries in dynamic database loops
**Learning:** Found an N+1 query loop when the API endpoint generated dynamic boss instances by looping through distinct categories and invoking a separate query for each element's stat count.
**Action:** Always precompute aggregate metrics via a single SQL query using `GROUP BY` and pass the mapped `precomputed_count` down to helper functions. Ensure helpers correctly manage tuple indexing and dictionary lookups dynamically for broader backend database library compatibility.
