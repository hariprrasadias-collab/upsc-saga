
## 2026-04-04 - Analytics Trends N+1 Query Fix
**Learning:** In analytical queries where we iterate over grouped records to fetch historical metrics (like calculating trend lines for low-scoring mock tests), running iterative `SELECT` queries inside loops causes a severe N+1 bottleneck.
**Action:** Extract all required grouped keys (e.g., subjects), use a single parameterized `IN (...)` clause to fetch all relevant historical data at once, and group the results in-memory using `collections.defaultdict(list)`.
