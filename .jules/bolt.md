## 2026-04-05 - [N+1 Bottleneck in API Endpoints]
**Learning:** When an API route iterates through dynamic categories and independently fetches associated stats (like row counts) directly from SQLite within each loop iteration, it creates an N+1 query problem that scales linearly and degrades performance.
**Action:** Use aggregate GROUP BY queries in the initial fetch to pull all required statistics simultaneously, and update the stats generator functions to accept these pre-fetched parameters as optional overrides.
