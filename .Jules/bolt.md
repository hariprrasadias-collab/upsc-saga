## 2024-03-24 - N+1 Query Optimization for Category Counts
**Learning:** Using a single `GROUP BY` query to fetch all category counts at once, passing the results downstream via `precomputed_count` kwargs, prevents N+1 query bottlenecks instead of triggering iterative `SELECT COUNT(*)` lookups for each category (e.g., when generating boss stats based on dynamic category sizes).
**Action:** Always identify opportunities to batch aggregate queries using `GROUP BY` when a list of items requires individual counts or calculations, and pass the precomputed data to helper functions.
