## 2025-02-14 - Optimize time distribution API query
**Learning:** In backend routes, doing a UNION ALL of all row dates and pulling them to Python for O(N) grouping causes large data transfer and memory overhead.
**Action:** Use a SQL subquery with GROUP BY to push the aggregation workload to the database and retrieve pre-calculated counts.
