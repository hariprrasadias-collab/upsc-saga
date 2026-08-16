## 2026-08-16 - [UNION ALL Bottleneck Optimization]
**Learning:** In SQLite, iterating through thousands of raw rows fetched from `UNION ALL` across multiple tables in Python using a loop causes unnecessary O(N) memory overhead and processing delays.
**Action:** Always shift the aggregation workload to the database by wrapping the `UNION ALL` queries in a subquery and applying a SQL `GROUP BY` clause (e.g., `SELECT date, COUNT(*) FROM (...) GROUP BY date`).
