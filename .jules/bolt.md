## 2026-04-04 - [N+1 query in dynamic stats generation]
**Learning:** Dynamic stat generators (like `get_boss_stats`) used inside list comprehensions over DB results can silently create massive N+1 query bottlenecks. The combination of `SELECT DISTINCT` followed by iterative `SELECT COUNT(*)` is an anti-pattern that can be solved with a single `SELECT col, COUNT(*) ... GROUP BY col`.
**Action:** When designing utility functions that fetch data by ID, always include optional pre-fetched parameter overrides (e.g., `pre_count`, `pre_row`) to allow bulk-fetching at the caller level.
