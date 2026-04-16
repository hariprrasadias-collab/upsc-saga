
## 2026-04-16 - Fix N+1 query in Arena Bosses endpoint
**Learning:** Generating dynamic lists by running SELECT COUNT(*) for every single distinct category in a loop creates significant N+1 database performance bottlenecks.
**Action:** Use a single GROUP BY database query to fetch all category counts at once, and pass the results downstream via kwargs (e.g., precomputed_count) to avoid iterative database lookups.
